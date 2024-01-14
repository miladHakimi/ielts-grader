import datetime
import os

from src.controllers import increment_requests, increment_api_count
import speech_recognition as sr
from google.cloud import speech, storage
from pymediainfo import MediaInfo

r = sr.Recognizer()

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_API_KEY_DIR = os.environ.get('GOOGLE_API_KEY_DIR')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_API_KEY_DIR

client = speech.SpeechClient()
storage_client = storage.Client()


def generate_speaking_topic(message, tele_bot, gpt_api):
    chat_gpt_request = "Suppose that you are an IELTS teacher that creates random IELTS speaking task 2 topics. Produce a random speaking topic that is formatted like a IELTS speaking topic. Start the topic with 'Topic:'"
    response = gpt_api.prompt(chat_gpt_request)
    if 'Topic:' in response:
        response = response.split('Topic:')[1]
    tele_bot.reply_to(message, response)
    increment_requests(message)


def grade_speaking(message, bot, gpt_api):
    bot.reply_to(message, "Please record your voice and send it to me.")
    bot.register_next_step_handler(
        message, process_speaking_step, bot, gpt_api)
    increment_requests(message)


def upload_file(file_name):
    bucket = storage_client.get_bucket(bucket_or_name=BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)


def erase_file(file_name):
    """ Erases file from the local storage and the cloud """
    bucket = storage_client.get_bucket(bucket_or_name=BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.delete()
    os.remove(file_name)


def get_transcript(file_name):
    media_info = MediaInfo.parse(file_name)
    sample_rate = media_info.audio_tracks[0].sampling_rate
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=sample_rate,
        enable_automatic_punctuation=True,
        language_code="en-US",
    )
    audio = speech.RecognitionAudio(
        uri='gs://%s/%s' %
        (BUCKET_NAME, file_name))
    response = client.long_running_recognize(
        config=config, audio=audio).result(
        timeout=500)
    transcript = "".join(
        [result.alternatives[0].transcript for result in response.results])
    return transcript


def process_speaking_step(message, bot, gpt_api):
    if message.voice:
        bot.reply_to(message, "Please wait a couple of minutes while we process your voice.")
        bot.send_chat_action(
            chat_id=message.chat.id,
            action="record_audio",
            timeout=500)
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        user_id = message.from_user.id
        timestamp = str(datetime.datetime.now().timestamp())
        file_name_ogg = "{}_{}.ogg".format(user_id, timestamp)
        with open(file_name_ogg, 'wb') as new_file:
            new_file.write(downloaded_file)
        try:
            upload_file(file_name_ogg)
            transcript = get_transcript(file_name_ogg)
            bot.send_chat_action(chat_id=message.chat.id, action="typing")
        except Exception as e:
            bot.reply_to(message, "An error has occured while processing your input. Please try again.")
            print(e)
            erase_file(file_name_ogg)
            return
        erase_file(file_name_ogg)

        marking_prompt = "Suppose you're an IELTS speaking reviewer. Qualitatively assess my ielts speaking task based on these factors: " \
            "Coherence and flow:\n"\
            "Sentence structure and syntax:\n"\
            "Vocabulary usage: \n"\
            "Lack of hesitations and repetitions: \n"\
            "Finally, give it a grade range base on academic ielts grading system form 0 to 9. "\
            "The min and max in the grade range must be 1 point apart. State exactly what is wrong and how to fix it. Start with \"Coherence and flow:\".\n{}".format(transcript)

        response = gpt_api.prompt(marking_prompt)
        bot.reply_to(
            message,
            "Recognized text: {}\n\nGrade:{}".format(
                transcript,
                response))


def generate_idea(message, bot, gpt_api):
    def generate_speaking_idea(message, bot, gpt_api):
        prompt = "Suppose you are an IELTS teacher that comes up with good ideas for speaking topics. Generate an answer for the following topic that contains around 150 words. Topic: {}".format(
            message.text)
        response = gpt_api.prompt(prompt)
        bot.reply_to(message, response)

    bot.reply_to(message, "Please send the topic.")
    bot.register_next_step_handler(
        message, generate_speaking_idea, bot, gpt_api)
