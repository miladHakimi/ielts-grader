import os
import re

import telebot

from src.gpt import chatgpt
from src.models.user import get_or_create_user, check_can_request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
gpt_api = chatgpt.ChatGPT()


def generate_topic(message):
    chat_gpt_request = "Suppose that you are an IELTS teacher that creates random IELTS writing essay topics. Produce a random writing topic that is formatted like a IELTS writing topic. Start the topic with 'Topic:'"
    response = gpt_api.prompt(chat_gpt_request)
    if 'Topic:' in response.choices[0].text:
        response.choices[0].text = response.choices[0].text.split('Topic:')[1]
    bot.reply_to(message, response.choices[0].text)


def grade_writing(message):
    bot.reply_to(message, "Please send the topic.")
    bot.register_next_step_handler(message, recieve_topic)


def recieve_topic(message):
    bot.reply_to(message, "Please send your essay.")
    bot.register_next_step_handler(message, grade_essay, "Topic: " + message.text)


def grade_essay(message, topic):
    m = message.text
    if len(re.findall(r'\w+', topic)) < 5:
        topic = "Infer the topic from essay."
    word_count = len(re.findall(r'\w+', m))
    if (word_count < 10 or word_count > 800):
        bot.reply_to(
            message,
            "The essay must contain between 10 and 500 words. Please try again."
        )
        return
    bot.reply_to(message,
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
    bot.reply_to(message, response.choices[0].text)


def check_grammar(message):
    bot.reply_to(message, "Please send the text.")
    bot.register_next_step_handler(message, extract_grammar)


def extract_grammar(message):
    chat_gpt_request = "Suppose you're an IELTS writing teacher. Check the grammar mistakes and list them in bullet points. Here is my essay:\n{}".format(
        message.text)
    bot.reply_to(message,
                      "Please wait while we are processing your query.")
    response = gpt_api.prompt(chat_gpt_request)
    bot.reply_to(message, response.choices[0].text)


def revise_writing(message):
    bot.reply_to(message, "Please send the text.")
    bot.register_next_step_handler(message, rewrite)


def rewrite(message):
    chat_gpt_request = "Suppose you're an IELTS writing expert. Revise the following essay.:\n{}".format(
        message.text)
    bot.reply_to(message,
                      "Please wait while we are processing your query.")
    response = gpt_api.prompt(chat_gpt_request)
    bot.reply_to(message, response.choices[0].text)


def write_essay(message):

    def generate_essay(message):
        chat_gpt_request = "Suppose you're an advanced IELTS expert. Write an academic IELTS essay with the following topic.:\n{}".format(
            message.text)
        bot.reply_to(message,
                          "Please wait while we are processing your query.")
        response = gpt_api.prompt(chat_gpt_request)
        bot.reply_to(message, response.choices[0].text)

    bot.reply_to(message, "Please send the topic.")
    bot.register_next_step_handler(message, generate_essay)
