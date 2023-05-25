import datetime

from src.utility import KeyboardButton
from src.models.user import extend_account, count_joined_users

admin_buttons = [
    KeyboardButton("Extend user 👩‍💻", "/admin/extend_user",
                   {"en": "Extends the user's subscription."}),
    KeyboardButton("User stats 📈", "/admin/user_stats",
                   {"en": "Shows user stats."}),
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
    today_count = count_joined_users(start_of_today)
    total_count = count_joined_users()
    tele_bot.reply_to(message, "Today's joined users: {}\nTotal joined users: {}".format(today_count, total_count))