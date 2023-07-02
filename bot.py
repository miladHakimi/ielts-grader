import os

import telebot
from src.gpt import chatgpt
from src.admin.admin import admin_buttons, extend_user, user_stats, api_stats
from src.controllers import get_or_create_user, create_tables
from src.utility import main_menu_buttons, writing_buttons, gen_menu
from src.writing import generate_topic, grade_writing, check_grammar, rewrite_writing, write_essay

BOT_TOKEN = os.environ.get('BOT_TOKEN')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')
DB_NAME = os.environ.get('DB_NAME')
BOT_NAME = "GrammarlyBot"

bot = telebot.TeleBot(BOT_TOKEN)
gpt_api = chatgpt.ChatGPT()


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


@bot.message_handler(commands=['start', 'hello'],
                     chat_types=['private'],
                     func=get_or_create_user)
def send_welcome(message):
    bot.reply_to(
        message,
        "Hi. Welcome to {}.\nPlease select from the options below. For more information please visit https://grammarlybot.ir."
        .format(BOT_NAME),
        reply_markup=gen_menu(main_menu_buttons))


@bot.message_handler(commands=['help'],
                     chat_types=['private'],
                     func=get_or_create_user)
def send_commands_list(message):
    list_of_functions = \
        "To purchase a premium account, please visit https://grammarlybot.ir."
    bot.send_message(message.chat.id,
                     list_of_functions,
                     reply_markup=gen_menu(main_menu_buttons))


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
    bot.infinity_polling()
