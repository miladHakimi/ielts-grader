import re

from src.models import increment_requests, increment_api_count


def generate_topic(message, tele_bot, gpt_api):
    chat_gpt_request = "Suppose that you are an IELTS teacher that creates random IELTS writing essay topics. Produce a random writing topic that is formatted like a IELTS writing topic. Start the topic with 'Topic:'"
    response = gpt_api.prompt(chat_gpt_request)
    if 'Topic:' in response.choices[0].text:
        response.choices[0].text = response.choices[0].text.split('Topic:')[1]
    tele_bot.reply_to(message, response.choices[0].text)
    increment_requests(message)
    increment_api_count("writing/Generate Topic")


def grade_writing(message, tele_bot, gpt_api):
    tele_bot.reply_to(message, "Please send the topic.")
    tele_bot.register_next_step_handler(message, recieve_topic, tele_bot,
                                        gpt_api)


def recieve_topic(message, tele_bot, gpt_api):
    tele_bot.reply_to(message, "Please send your essay.")
    tele_bot.register_next_step_handler(message, grade_essay, tele_bot,
                                        gpt_api, "Topic: " + message.text)


def grade_essay(message, tele_bot, gpt_api, topic):
    m = message.text
    if len(re.findall(r'\w+', topic)) < 5:
        topic = "Infer the topic from essay."
    word_count = len(re.findall(r'\w+', m))
    if (word_count < 10 or word_count > 800):
        tele_bot.reply_to(
            message,
            "The essay must contain between 10 and 500 words. Please try again."
        )
        return
    tele_bot.reply_to(message,
                      "Please wait while we are processing your query.")
    chat_gpt_request = "Suppose you're an IELTS writing reviewer. Qualitatively assess my ielts writing task base on this factors: " \
                    "Task Response:\n"\
                    "Coherence and Cohesion:\n"\
                    "Lexical Resource: \n"\
                    "Grammatical Range and Accuracy: \n"\
                    "Task Achievement: \n"\
                    "Vocabulary: \n"\
                    "Grammar: \n"\
                    "Sentence Structure: \n"\
                    "Spelling and Punctuation: \n"\
                    "Development of Ideas: \n"\
                    "Examples: \n"\
                    "Transition Words: \n"\
                    "Clarifying Phrases \n"\
                    "Overall \n"\
                    "Finally, give it a grade range base on academic ielts grading system form 0 to 9. "\
                    "The min and max in the grade range must be 1 point apart.\n{}\n{}".format(topic, m)
    response = gpt_api.prompt(chat_gpt_request)
    tele_bot.reply_to(message, response.choices[0].text)
    increment_requests(message)
    increment_api_count("writing/Grade Writing")


def check_grammar(message, tele_bot, gpt_api):
    tele_bot.reply_to(message, "Please send the text.")
    tele_bot.register_next_step_handler(message, extract_grammar, tele_bot,
                                        gpt_api)


def extract_grammar(message, tele_bot, gpt_api):
    chat_gpt_request = "Suppose you're an IELTS writing teacher. Check the grammar mistakes and list them in bullet points. Here is my essay:\n{}".format(
        message.text)
    tele_bot.reply_to(message,
                      "Please wait while we are processing your query.")
    response = gpt_api.prompt(chat_gpt_request)
    tele_bot.reply_to(message, response.choices[0].text)
    increment_requests(message)
    increment_api_count("writing/Check Grammar")


def revise_writing(message, tele_bot, gpt_api):
    tele_bot.reply_to(message, "Please send the text.")
    tele_bot.register_next_step_handler(message, rewrite, tele_bot, gpt_api)


def rewrite(message, tele_bot, gpt_api):
    chat_gpt_request = "Suppose you're an IELTS writing expert. Revise the following essay.:\n{}".format(
        message.text)
    tele_bot.reply_to(message,
                      "Please wait while we are processing your query.")
    response = gpt_api.prompt(chat_gpt_request)
    tele_bot.reply_to(message, response.choices[0].text)
    increment_requests(message)
    increment_api_count("writing/Revise Writing")


def write_essay(message, tele_bot, gpt_api):

    def generate_essay(message):
        chat_gpt_request = "Suppose you're an advanced IELTS expert. Write an academic IELTS essay with the following topic.:\n{}".format(
            message.text)
        tele_bot.reply_to(message,
                          "Please wait while we are processing your query.")
        response = gpt_api.prompt(chat_gpt_request)
        tele_bot.reply_to(message, response.choices[0].text)
        increment_requests(message)
        increment_api_count("writing/Write Essay")

    tele_bot.reply_to(message, "Please send the topic.")
    tele_bot.register_next_step_handler(message, generate_essay)
