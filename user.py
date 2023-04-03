import datetime
import os

import telebot
import sqlite3

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_NAME = os.environ.get('DB_NAME')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')
MAX_REQUESTS = 5

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


# Check if the user's account has expired.
def check_expired_account(message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ? AND expiry_time > ?", (user_id, datetime.datetime.now()))
    result = c.fetchone()
    conn.close()

    if result:
        # User has not expired.
        return True
    return False


def get_num_requests(message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT num_requests FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    if result is not None:
        return result[0]
    conn.close()
    return 100


# Check if the user has exceeded the maximum number of requests.        
def check_can_request(func):
    def wrapper(message):
        remaining_reqs = max(0, MAX_REQUESTS - get_num_requests(message))
        is_expired = check_expired_account(message)
        if remaining_reqs > 0 or not is_expired:
            return func(message)
        bot.reply_to(message, "You have exceeded the maximum number of requests. Please visit https://grammarlybot.ir to purchase subscription for your account.")
    return wrapper


def extend_account(message):
    username = message.split(",")[0].strip()
    if '@' in username:
        username = username.split("@")[1]
    days = int(message.split(",")[1])
    if not username or not days:
        bot.reply_to(message, "Invalid command.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, expiry_time FROM users WHERE username = ?', (username, ))
    result = c.fetchone()
    if result is not None:
        if result[1] is None:
            date = datetime.datetime.now()
        else:
            date = datetime.datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S.%f")
        new_exp_time = max(date, datetime.datetime.now()) + datetime.timedelta(days=days)
        c.execute("UPDATE users SET expiry_time = ? WHERE username = ?", (new_exp_time, username))
        bot.send_message(chat_id=PRIVATE_GROUP_ID, text="Account has been extended for {} day(s).".format(days))
        conn.commit()
    else:
        bot.send_message(chat_id=PRIVATE_GROUP_ID, text="User not found: " + str(username))
    conn.close()
