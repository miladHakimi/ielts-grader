import datetime
import os

from src.controllers import increment_requests, increment_api_count
import speech_recognition as sr 
from pydub import AudioSegment

r = sr.Recognizer()


def generate_speaking_topic(message, tele_bot, gpt_api):
    chat_gpt_request = "Suppose that you are an IELTS teacher that creates random IELTS speaking task 2 topics. Produce a random speaking topic that is formatted like a IELTS speaking topic. Start the topic with 'Topic:'"
    response = gpt_api.prompt(chat_gpt_request)
    if 'Topic:' in response.choices[0].text:
        response.choices[0].text = response.choices[0].text.split('Topic:')[1]
    tele_bot.reply_to(message, response.choices[0].text)
    increment_requests(message)
    # increment_api_count("speaking/Generate Topic")


def grade_speaking(message, bot, gpt_api):
    bot.reply_to(message, "Please record your voice and send it to me.")
    bot.register_next_step_handler(message, process_speaking_step, bot, gpt_api)
    # increment_requests(message)


def process_speaking_step(message, bot, gpt_api):
    if message.voice:
        new_message = bot.reply_to(message, "Processing...")
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        user_id = message.from_user.id
        timestamp = str(datetime.datetime.now().timestamp())
        file_name_ogg = "{}_{}.ogg".format(user_id, timestamp)
        file_name_wav = "{}_{}.wav".format(user_id, timestamp)

        with open(file_name_ogg, 'wb') as new_file:
            new_file.write(downloaded_file)
        sound = AudioSegment.from_ogg(file_name_ogg)
        sound.export(file_name_wav, format="wav")
        with sr.AudioFile(file_name_wav) as source:
            bot.edit_message_text(chat_id=message.chat.id, message_id=new_message.message_id, text="Detecting speech...")
            user_audio = r.record(source)
            text = r.recognize_google(user_audio, language="en-US")
            punctuation_prompt = "Only add punctuation to the following text:\n{}".format(text)
            correction = gpt_api.prompt(punctuation_prompt).choices[0].text
            bot.edit_message_text(chat_id=message.chat.id, message_id=new_message.message_id, text="Evaluating ...")
            marking_prompt = "Suppose you're an IELTS speaking reviewer. Qualitatively assess my ielts speaking task based on these factors: " \
                    "Coherence and flow:\n"\
                    "Sentence structure and syntax:\n"\
                    "Vocabulary usage: \n"\
                    "Lack of hesitations and repetitions: \n"\
                    "Finally, give it a grade range base on academic ielts grading system form 0 to 9. "\
                    "The min and max in the grade range must be 1 point apart. State exactly what is wrong and how to fix it. Start with \"Coherence and flow:\".\n{}".format(correction)
            response = gpt_api.prompt(marking_prompt)
            bot.reply_to(message, "Recognized text: {}\n\nGrade:{}".format(correction, response.choices[0].text))
        # Remove files
        os.remove(file_name_ogg)
        os.remove(file_name_wav)


def generate_idea(message, bot, gpt_api):
    def generate_speaking_idea(message, bot, gpt_api):
        prompt = "Suppose you are an IELTS teacher that comes up with good ideas for speaking topics. Generate an answer for the following topic that contains around 150 words. Topic: {}".format(message.text)
        response = gpt_api.prompt(prompt)
        bot.reply_to(message, response.choices[0].text)

    bot.reply_to(message, "Please send the topic.")
    bot.register_next_step_handler(message, generate_speaking_idea, bot, gpt_api)
