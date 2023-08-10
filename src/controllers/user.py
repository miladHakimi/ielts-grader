import os

import telebot
import sqlite3
import datetime

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from src.models.user import User, Pending
from . import engine

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
    user_id = int(message.from_user.id)
    username = message.from_user.username
    with Session(engine) as session:
        statement = select(User.id).where(User.id == user_id)
        if session.scalar(statement):
            return True
        user = User(id=user_id, username=username, start_date=datetime.datetime.now())
        session.add(user)
        session.commit()
    bot.send_message(chat_id=PRIVATE_GROUP_ID,
                         text="New User: " + str(message.from_user.id) + ",@" +
                         str(message.from_user.username))
    return True


# When a user sends a chatGPT query, number of requests is incremented.
def increment_requests(message):
    user_id = message.from_user.id
    if user_id == BOT_ID:
        user_id = message.chat.id
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.execute(statement).scalar_one()
        if not user:
            return
        user.num_requests += 1
        session.commit()


# Check if the user's account has expired.
def check_expired_account(message):
    user_id = message.from_user.id
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id).where(User.expiry_time > datetime.datetime.now())
        user = session.execute(statement).scalar()
        return user is None


def get_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


# Check if the user's start date is more than TRIAL_DAYS ago.
def check_in_trial(user_id):
    with Session(engine) as session:
        statement = select(User.start_date).where(User.id == user_id)
        result = session.execute(statement).scalar_one()
        if not result:
            return True
        start_date = result
        if start_date > datetime.datetime.now() - datetime.timedelta(days=TRIAL_DAYS):
            return True
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


def update_username(message):
    """" Updates the username if it has changed. """
    user_id = message.from_user.id
    username = message.from_user.username
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.execute(statement).scalar_one_or_none()
        if not user:
            return
        if user.username != username:
            user.username = username
            session.commit()


def update_expiry_time(message):
    """" Scans the pending expiry requests for this user name and updates the expiry time. """
    user_id = message.from_user.id
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.execute(statement).scalar_one_or_none()
        if not user:
            return
        if user.username:
            statement = select(Pending).where(Pending.username == user.username)
            pending = session.execute(statement).scalar_one_or_none()
            if pending:
                user.expiry_time = pending.expiry_time
                # remove the pending request
                session.delete(pending)
                session.commit()
                bot.send_message(chat_id=PRIVATE_GROUP_ID, text="Expiry update for user " + user.username)


def check_can_request(func):
    def wrapper(message):
        update_username(message)
        update_expiry_time(message)
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

    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        # Check if the user exists.
        user = session.execute(statement).scalar_one_or_none()
        if not user:
            bot.send_message(chat_id=PRIVATE_GROUP_ID,
                             text="User @{} not found. Added the extension to the pending table.".format(username))
            # TODO(@milad): Fix this. The date must be maxed beteween the current expiry date and now.
            # Add the extension to the pending table.
            pending = Pending(username=username, expiry_time=datetime.datetime.now() + datetime.timedelta(days=days))
            session.add(pending)
            session.commit()
            return
        if user.expiry_time is None:
            date = datetime.datetime.now()
        else:
            date = user.expiry_time
        new_exp_time = max(
            date, datetime.datetime.now()) + datetime.timedelta(days=days)
        user.expiry_time = new_exp_time
        bot.send_message(chat_id=PRIVATE_GROUP_ID,
                    text="Account @{} has been extended for {} day(s).".format(username, days))
        session.commit()


def count_joined_users(from_date=datetime.datetime.min, to_date=datetime.datetime.max):
    with Session(engine) as session:
        statement = select(func.count()).select_from(User).where(User.start_date > from_date).where(User.start_date < to_date)
        result = session.execute(statement).scalar()
        return result


def count_requests():
    with Session(engine) as session:
        statement = select(func.sum(User.num_requests))
        result = session.execute(statement).scalar()
        return result
