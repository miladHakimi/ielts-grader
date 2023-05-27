import datetime
import os

import telebot
import sqlite3

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_NAME = os.environ.get('DB_NAME')
PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')
MAX_REQUESTS = 5
TRIAL_DAYS = 5
BOT_ID = int(BOT_TOKEN.split(':')[0].strip())

bot = telebot.TeleBot(BOT_TOKEN)


# This function is called when the user sends a message to the bot
# It creates the user if it doesn't already exist in the database.
def get_or_create_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id, ))
    result = c.fetchone()

    if result is None:
        bot.send_message(chat_id=PRIVATE_GROUP_ID,
                         text="New User: " + str(message.from_user.id) + ",@" +
                         str(message.from_user.username))
        c.execute("INSERT INTO users (id, username, start_date) VALUES (?, ?, ?)",
                  (user_id, username, datetime.datetime.now()))
        conn.commit()
    conn.close()
    return True


# When a user sends a chatGPT query, number of requests is incremented.
def increment_requests(message):
    user_id = message.from_user.id
    if user_id == BOT_ID:
        user_id = message.chat.id
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id, ))
    result = c.fetchone()
    if result is not None:
        c.execute(
            "UPDATE users SET num_requests = num_requests + 1 WHERE id = ?",
            (user_id, ))
        conn.commit()
    conn.close()


# Check if the user's account has expired.
def check_expired_account(message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ? AND expiry_time > ?",
              (user_id, datetime.datetime.now()))
    result = c.fetchone()
    conn.close()
    if result:
        # User has not expired.
        return False
    return True


def get_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


# Check if the user's start date is more than TRIAL_DAYS ago.
def check_in_trial(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT start_date FROM users WHERE id = ?", (user_id, ))
    result = c.fetchone()
    # If start_date is none it means the user hasn't submitted any request yet. Hence, the user is in trial period.
    if not result[0]:
        conn.close()
        return True
    start_date = get_date(result[0])
    # If start_date is more than 5 days ago, the user is not in trial period anymore.
    if start_date > datetime.datetime.now() - datetime.timedelta(
            days=TRIAL_DAYS):
        conn.close()
        return True
    conn.close()
    return False


# If start date was not set, set the start date to now.
def set_start_date(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT start_date FROM users WHERE id = ?", (user_id, ))
    result = c.fetchone()
    if result[0] is None:
        c.execute("UPDATE users SET start_date = ? WHERE id = ?",
                  (datetime.datetime.now(), user_id))
        conn.commit()
    conn.close()


# Check if the user has exceeded the maximum number of requests.
def check_can_request(func):
    def wrapper(message):
        in_trial = check_in_trial(message.from_user.id)
        is_expired = check_expired_account(message)
        if in_trial or not is_expired:
            func(message)
            set_start_date(message.from_user.id)
            return
        if type(message) is telebot.types.CallbackQuery:
            message = message.message
        bot.reply_to(
            message,
            "Your trial period is over. Please visit https://grammarlybot.ir to purchase subscription for your account."
        )

    return wrapper


# The format of the message is: username, days
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
    c.execute('SELECT id, expiry_time FROM users WHERE username = ?',
              (username, ))
    result = c.fetchone()
    if result is not None:
        if result[1] is None:
            date = datetime.datetime.now()
        else:
            date = get_date(result[1])
        new_exp_time = max(
            date, datetime.datetime.now()) + datetime.timedelta(days=days)
        c.execute("UPDATE users SET expiry_time = ? WHERE username = ?",
                  (new_exp_time, username))
        bot.send_message(
            chat_id=PRIVATE_GROUP_ID,
            text="Account has been extended for {} day(s).".format(days))
        conn.commit()
    else:
        bot.send_message(chat_id=PRIVATE_GROUP_ID,
                         text="User @{} not found: ".format(username))
    conn.close()


def count_joined_users(from_date=datetime.datetime.min, to_date=datetime.datetime.max):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM users WHERE start_date BETWEEN ? AND ?",
        (from_date, to_date))
    
    result = c.fetchone()
    conn.close()
    return result[0]


def count_requests():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT SUM(num_requests) FROM users")
    result = c.fetchone()
    conn.close()
    return result[0]
