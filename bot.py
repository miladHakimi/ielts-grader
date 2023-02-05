import os
import openai
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')
openai.api_key = os.environ.get('OPEN_AI_TOKEN')
START_TOKEN = os.environ.get('START_TOKEN')
END_TOKEN = os.environ.get('END_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy. The defualt command is Persian to English translation.")

@bot.message_handler(commands=['grade'])
def send_welcome(message):
    bot.reply_to(message, "Let's grade your homework!")
    m = message.text.split("/grade", 1)[1]
    chat_gpt_request = "suppose you're an IELTS writing reviewer. Please grade the following essay including spelling, grammar, and technical issues. Mention at least 10 things to improve. Start the review by saying: Here are my comments. Essay:\n" + m
    response = openai.Completion.create(model="text-davinci-003", prompt=chat_gpt_request, temperature=1, max_tokens=1000)
    bot.reply_to(message, response.choices[0].text)

@bot.message_handler(commands=['p2e'])
def translate_persian_to_english(message):
    m = message.text.split("/p2e", 1)[1]
    chat_gpt_request = "Translate the following text from Persian to English that resides between {} and {} tokens: ".format(START_TOKEN, END_TOKEN) + START_TOKEN + m + END_TOKEN
    response = openai.Completion.create(model="text-davinci-003", prompt=chat_gpt_request, temperature=1, max_tokens=1000)
    bot.reply_to(message, response.choices[0].text)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    message.text = '/p2e ' + message.text
    translate_persian_to_english(message)
    # bot.reply_to(message, message.text)

bot.infinity_polling()
