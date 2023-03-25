import os
import re

import telebot
import sqlite3

import chatgpt

BOT_TOKEN = os.environ.get('BOT_TOKEN')
START_TOKEN = os.environ.get('START_TOKEN')
END_TOKEN = os.environ.get('END_TOKEN')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')
DB_NAME = os.environ.get('DB_NAME')

bot = telebot.TeleBot(BOT_TOKEN)
gpt_api = chatgpt.ChatGPT()


# user id to username
user_lists = {}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message,
                 "Hi. The defualt response is Persian to English translation. Send /help to see the list of commands.")
    user_id = message.from_user.id
    username = message.from_user.username
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()

    if result is None:
        bot.send_message(chat_id=PRIVATE_GROUP_ID, text="New User: " + str(message.from_user.id) + ",@" + str(message.from_user.username))
        c.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

    conn.close()

@bot.message_handler(commands=['grade'])
def grade(message):
    m = message.text.split("/grade", 1)[1]
    word_count = len(re.findall(r'\w+', m))
    if (word_count < 100 or word_count > 500):
        bot.reply_to(
            message,
            "The essay must contain between 100 and 500 words. Please try again."
        )
        return
    bot.reply_to(message, "Please wait while we are processing your query.")
    chat_gpt_request = "Suppose you're an IELTS writing reviewer. Please grade the following essay that resides between {} and {} tokens. Categorize the result into grammar, spelling, and technical issues. In case of an issue, point out specifically what it is and how to solve it. At the end, give the writing a grade from 0 to 30 and justify the mark. Start the review by saying: Here are my comments. Essay:{}, {}, {}\n".format(
        START_TOKEN, END_TOKEN, START_TOKEN, m, END_TOKEN)
    response = gpt_api.prompt(chat_gpt_request)
    bot.reply_to(message, response.choices[0].text)


@bot.message_handler(commands=['rewrite'])
def rewrite(message):
    m = message.text.split("/rewrite", 1)[1]
    word_count = len(re.findall(r'\w+', m))
    if (word_count < 100 or word_count > 500):
        bot.reply_to(
            message,
            "The essay must contain between 100 and 500 words. Please try again."
        )
        return
    bot.reply_to(message, "Please wait while we are processing your query.")
    chat_gpt_request = "Between the tokens {} and {}, there is a TOEFL essay. Find its errors and rewrite it with those errors fixed. Try using more sophisticated collocations. Start the answer by saying: \"Here is my answer:\". At the end, in bullet points, state what has been changed by saying: \"Here are the changes:\". {} {} {}\n".format(
        START_TOKEN, END_TOKEN, START_TOKEN, m, END_TOKEN)
    response = gpt_api.prompt(chat_gpt_request)
    bot.reply_to(message, response.choices[0].text)


@bot.message_handler(commands=['p2e'])
def translate_persian_to_english(message):
    m = message.text.split("/p2e", 1)[1]
    chat_gpt_request = "Translate the following text from Persian to English that resides between {} and {} tokens: {}\n{}\n.{}  ".format(
        START_TOKEN, END_TOKEN, START_TOKEN, m, END_TOKEN)
    response = gpt_api.prompt(chat_gpt_request)
    bot.reply_to(message, response.choices[0].text)


@bot.message_handler(commands=['help'])
def send_commands_list(message):
    list_of_functions = \
        "/grade: Grade an essay.\n" + \
        "/rewrite: Rewrite an essay."
    bot.reply_to(message, list_of_functions)


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    if (message.chat.type == 'private'):
        message.text = '/p2e ' + message.text
        translate_persian_to_english(message)


bot.infinity_polling()
