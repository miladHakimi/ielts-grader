import os
import re

import telebot
import chatgpt

from user import get_or_create_user, increment_requests, check_expired_account, get_num_requests, check_can_request, extend_account

BOT_TOKEN = os.environ.get('BOT_TOKEN')
START_TOKEN = os.environ.get('START_TOKEN')
END_TOKEN = os.environ.get('END_TOKEN')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')
DB_NAME = os.environ.get('DB_NAME')

MAX_REQUESTS = 5

bot = telebot.TeleBot(BOT_TOKEN)
gpt_api = chatgpt.ChatGPT()

# user id to username
user_lists = {}


@bot.message_handler(commands=['start', 'hello'],
                     chat_types=['private'],
                     func=get_or_create_user)
def send_welcome(message):
    remaining_reqs = max(0, MAX_REQUESTS - get_num_requests(message))
    bot.reply_to(message, "Hi. Send /help to see the list of commands. Number of free requests left: {}".format(remaining_reqs))


@bot.message_handler(commands=['grade'],
                     chat_types=['private'],
                     func=get_or_create_user)
@check_can_request
def grade(message):
    m = message.text.split("/grade", 1)[1]
    word_count = len(re.findall(r'\w+', m))
    if (word_count < 10 or word_count > 500):
        bot.reply_to(
            message,
            "The essay must contain between 10 and 500 words. Please try again."
        )
        return
    bot.reply_to(message, "Please wait while we are processing your query.")
    chat_gpt_request = "Suppose you're an TOEFL writing reviewer. Grade the following essay between {} and {} tokens. Categorize the result into grammar, spelling, and technical issues. In case of an issue, point out specifically what it is and how to solve it. At the end, give the writing a grade from 0 to 30 and justify the mark. Start the review by saying: Here are my comments. Essay:{}, {}, {}\n".format(
        START_TOKEN, END_TOKEN, START_TOKEN, m, END_TOKEN)
    response = gpt_api.prompt(chat_gpt_request)
    bot.reply_to(message, response.choices[0].text)
    increment_requests(message)


@bot.message_handler(commands=['rewrite'],
                     chat_types=['private'],
                     func=get_or_create_user)
@check_can_request
def rewrite(message):
    m = message.text.split("/rewrite", 1)[1]
    word_count = len(re.findall(r'\w+', m))
    if (word_count < 10 or word_count > 500):
        bot.reply_to(
            message,
            "The essay must contain between 10 and 500 words. Please try again."
        )
        return
    bot.reply_to(message, "Please wait while we are processing your query.")
    chat_gpt_request = "Between the tokens {} and {}, there is a TOEFL essay. Find its errors and rewrite it with those errors fixed. Try using more sophisticated collocations. Start the answer by saying: \"Here is my answer:\". At the end, in bullet points, state what has been changed by saying: \"Here are the changes:\". {} {} {}\n".format(
        START_TOKEN, END_TOKEN, START_TOKEN, m, END_TOKEN)
    response = gpt_api.prompt(chat_gpt_request)
    bot.reply_to(message, response.choices[0].text)
    increment_requests(message)


@bot.message_handler(commands=['help'],
                     chat_types=['private'],
                     func=get_or_create_user)
def send_commands_list(message):
    list_of_functions = \
        "Here is the list of valid commands:\n" \
        "/grade: Grade an essay.\n" \
        "/rewrite: Rewrite an essay.\n" \
        "Copy and paste the essay after the command, then send it.\n" \
        "Example: /rewrite I am a student. I am studying at the university.\n\n" \
        "To purchase a premium account, please visit https://grammarlybot.ir."
    bot.reply_to(message, list_of_functions)


def extend_user(message):
    data = message.text.split("/extend_user", 1)[1]
    print(data)
    extend_account(data)


@bot.message_handler(func=get_or_create_user)
def echo_all(message):
    if (message.chat.id == int(PRIVATE_GROUP_ID)):
        if '/extend_user' in message.text:
            extend_user(message)
    if (message.chat.type == 'private'):
        return send_commands_list(message)



bot.infinity_polling()
