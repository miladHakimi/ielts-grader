from src.utility import KeyboardButton
from src.models.user import extend_account

admin_buttons = [
    KeyboardButton("Extend user 👩‍💻", "/admin/extend_user",
                   {"en": "Extends the user's subscription."}),
    KeyboardButton("Today's stats 📅", "/admin/today_stats",
                   {"en": "Shows today's stats."}),
    KeyboardButton("Total stats 📈", "/admin/total_stats",
                   {"en": "Shows total stats."}),
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
