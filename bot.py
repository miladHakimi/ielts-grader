import os

import telebot

from src.gpt import chatgpt, CerebrasGPT
from src.admin.admin import admin_buttons, extend_user, user_stats, api_stats, feedback_handler
from src.controllers import get_or_create_user, create_tables, generate_speaking_topic, grade_speaking, generate_idea, teach_word, check_response, check_can_request, recall_word
from src.utility import main_menu_buttons, writing_buttons, speaking_buttons, gen_menu, reading_buttons, CustomExceptionHandler
from src.writing import generate_topic, grade_writing, check_grammar, rewrite_writing, write_essay


BOT_TOKEN = os.environ.get('BOT_TOKEN')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')
DB_NAME = os.environ.get('DB_NAME')
BOT_NAME = "IELTSBot"

bot = telebot.TeleBot(BOT_TOKEN)
bot.exception_handler = CustomExceptionHandler(bot, PRIVATE_GROUP_ID)

gpt_api = chatgpt.ChatGPT()


def reading_handler(call):
    data = call.data.split("/reading/")
    if len(data) == 1:
        help_message = '\n'.join(str(button) for button in reading_buttons)
        bot.edit_message_text(
            "Please select from the options below.\n{}".format(help_message),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=gen_menu(reading_buttons))
    elif data[1] == "vocab":
        teach_word(call.message, bot, gpt_api)
    elif data[1] == "recall":
        recall_word(call.message, bot, gpt_api)


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
    elif data[1] == "rewrite":
        rewrite_writing(call.message, bot, gpt_api)
    elif data[1] == "write_essay":
        write_essay(call.message, bot, gpt_api)


def speaking_handler(call):
    data = call.data.split("/speaking/")
    if len(data) == 1:
        help_message = '\n'.join(str(button) for button in speaking_buttons)
        bot.edit_message_text(
            "Please select from the options below.\n{}".format(help_message),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=gen_menu(speaking_buttons))
    elif data[1] == "gen_topic":
        generate_speaking_topic(call.message, bot, gpt_api)
    elif data[1] == "grade":
        grade_speaking(call.message, bot, gpt_api)
    elif data[1] == "gen_idea":
        generate_idea(call.message, bot, gpt_api)


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
    elif data[1] == "api_stats":
        api_stats(call.message, bot)


@bot.callback_query_handler(func=lambda call: "reading/vocab/" not in call.data)
@check_can_request
def callback_query(call):
    if call.data == "/":
        bot.edit_message_text("Please select from the options below.",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=gen_menu(main_menu_buttons, True))
    if "/writing" in call.data:
        return writing_handler(call)
    if "/speaking" in call.data:
        return speaking_handler(call)
    if "/reading" in call.data:
        return reading_handler(call)
    if "/admin" in call.data:
        return admin_handler(call)
    if "/feedback" in call.data:
        return feedback_handler(call.message, bot)


@bot.message_handler(commands=['start', 'hello'],
                     chat_types=['private'],
                     func=get_or_create_user)
def send_welcome(message):
    bot.reply_to(
        message,
        "Welcome to {}, the AI-powered Telegram bot designed to boost \
        your IELTS skills! Get expert guidance and personalized support \
        to excel in your IELTS journey. For premium membership, message \
        @rezadorali."
        .format(BOT_NAME),
        reply_markup=gen_menu(main_menu_buttons, True))


@bot.message_handler(commands=['help'],
                     chat_types=['private'],
                     func=get_or_create_user)
def send_commands_list(message):
    list_of_functions = \
        "To purchase a premium account, please visit https://grammarlybot.ir."
    bot.send_message(message.chat.id,
                     list_of_functions,
                     reply_markup=gen_menu(main_menu_buttons, True))


@bot.message_handler(func=get_or_create_user)
def echo_all(message):
    if message.chat.id == int(PRIVATE_GROUP_ID) and message.text == "/start":
        return bot.send_message(message.chat.id,
                                "Here are the list of commands:",
                                reply_markup=gen_menu(admin_buttons))
    if (message.chat.type == 'private'):
        return send_commands_list(message)


if __name__ == '__main__':
    create_tables()
    bot.register_callback_query_handler(
        check_response, func=lambda call: "reading/vocab/" in call.data, pass_bot=True)
    bot.infinity_polling()
