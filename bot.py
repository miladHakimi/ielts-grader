import os
import re

import telebot
from src.gpt import chatgpt
from src.admin.admin import admin_buttons, extend_user, user_stats
from src.models.user import get_or_create_user, increment_requests, check_can_request
from src.utility import main_menu_buttons, writing_buttons, gen_menu
from src.writing import generate_topic, grade_writing, check_grammar, revise_writing, write_essay

BOT_TOKEN = os.environ.get('BOT_TOKEN')
START_TOKEN = os.environ.get('START_TOKEN')
END_TOKEN = os.environ.get('END_TOKEN')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')
DB_NAME = os.environ.get('DB_NAME')
BOT_NAME = "GrammarlyBot"

MAX_REQUESTS = 5

bot = telebot.TeleBot(BOT_TOKEN)
gpt_api = chatgpt.ChatGPT()

# user id to username
user_lists = {}


def writing_handler(call):
    data = call.data.split("/writing/")
    if len(data) == 1:
        help_message = '\n'.join(str(button) for button in writing_buttons)
        bot.edit_message_text(
            "Please select from the options below.\n{}".format(help_message),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=gen_menu(writing_buttons))
    elif data[1] == "gen_topic":
        generate_topic(call.message, bot, gpt_api)
    elif data[1] == "grade":
        grade_writing(call.message, bot, gpt_api)
    elif data[1] == "check_grammar":
        check_grammar(call.message, bot, gpt_api)
    elif data[1] == "revise":
        revise_writing(call.message, bot, gpt_api)
    elif data[1] == "write_essay":
        write_essay(call.message, bot, gpt_api)


def admin_handler(call):
    data = call.data.split("/admin/")
    if len(data) == 1:
        help_message = '\n'.join(str(button) for button in writing_buttons)
        bot.edit_message_text(
            "Please select from the options below.\n{}".format(help_message),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=gen_menu(admin_buttons))
    elif data[1] == "extend_user":
        extend_user(call.message, bot)
    elif data[1] == "user_stats":
        user_stats(call.message, bot)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "/":
        bot.edit_message_text("Please select from the options below.",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=gen_menu(main_menu_buttons))
    if "/writing" in call.data:
        return writing_handler(call)
    if "/admin" in call.data:
        return admin_handler(call)
    elif call.data == "/reading":
        bot.send_message(call.message.chat.id, "Answer is No")


@bot.message_handler(commands=['start', 'hello'],
                     chat_types=['private'],
                     func=get_or_create_user)
def send_welcome(message):
    bot.reply_to(
        message,
        "Hi. Welcome to {}.\nPlease select from the options below. For more information please visit https://grammarlybot.ir."
        .format(BOT_NAME),
        reply_markup=gen_menu(main_menu_buttons))


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
    chat_gpt_request = "Suppose you're an IELTS writing reviewer. Grade the following essay between {} and {} tokens. Categorize the result into grammar, spelling, and technical issues. In case of an issue, point out specifically what it is and how to solve it. At the end, give the writing a grade from 0 to 30 and justify the mark. Start the review by saying: Here are my comments. Essay:{}, {}, {}\n".format(
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
    bot.send_message(message.chat.id,
                     list_of_functions,
                     reply_markup=gen_menu(main_menu_buttons))


@bot.message_handler(func=get_or_create_user)
def echo_all(message):
    if (message.chat.id == int(PRIVATE_GROUP_ID)):
        return bot.send_message(message.chat.id,
                                "Here are the list of commands:",
                                reply_markup=gen_menu(admin_buttons))
    if (message.chat.type == 'private'):
        return send_commands_list(message)


bot.infinity_polling()
