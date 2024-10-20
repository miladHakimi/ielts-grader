import datetime
import os

from src.utility import KeyboardButton
from src.controllers import extend_account, count_joined_users, count_requests, get_writing_stats


PRIVATE_GROUP_ID = os.environ.get('PRIVATE_GROUP_ID')


admin_buttons = [
    KeyboardButton("Extend user 👩‍💻", "/admin/extend_user",
                   {"en": "Extends the user's subscription."}),
    KeyboardButton("User stats 📈", "/admin/user_stats",
                   {"en": "Shows user stats."}),
    KeyboardButton("API stats 📊", "/admin/api_stats",
                   {"en": "Shows API stats."}),
]


def extend_user(message, tele_bot):

    def get_duration(message, username):
        extend_account("{}, {}".format(username, message.text.strip()))

    def get_username(message):
        tele_bot.reply_to(message, "Please send the duration.")
        tele_bot.register_next_step_handler(message, get_duration,
                                            message.text.strip())
    tele_bot.reply_to(message, "Please send the username.")
    tele_bot.register_next_step_handler(message, get_username)


def user_stats(message, tele_bot):
    today = datetime.datetime.today()
    start_of_today = datetime.datetime(today.year, today.month, today.day)
    today_count = count_joined_users(from_date=start_of_today)
    total_count = count_joined_users()
    total_requests = count_requests()
    tele_bot.reply_to(message, "Today's joined users: {}\nTotal joined users: {}\nTotal Requests: {}".format(
        today_count, total_count, total_requests))


def api_stats(message, tele_bot):
    writing_stats = get_writing_stats()
    # Format must be like this: Topic: Count
    result = ""
    for i in writing_stats:
        result += "{}: {}\n".format(i[1].split("/")[1], i[2])
    tele_bot.reply_to(message, result)


def feedback_handler(message, tele_bot):
    def send_feedback(message):
        tele_bot.reply_to(
            message, "Thank you for your feedback. We will process it ASAP!")
        tele_bot.send_message(int(
            PRIVATE_GROUP_ID), f"Feedback from {message.from_user.id} (@{ message.from_user.username})\n: {message.text}")

    tele_bot.reply_to(message, "Please send your feedback.")
    tele_bot.register_next_step_handler(message, send_feedback)
