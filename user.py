import os

import telebot
import sqlite3

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_NAME = os.environ.get('DB_NAME')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')

bot = telebot.TeleBot(BOT_TOKEN)


# This function is called when the user sends a message to the bot
# It creates the user if it doesn't already exist in the database.
def get_or_create_user(message):
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
    return True


# When a user sends a chatGPT query, number of requests is incremented.
def increment_requests(message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    if result is not None:
        c.execute("UPDATE users SET num_requests = num_requests + 1 WHERE id = ?", (user_id,))
        conn.commit()
    conn.close()
