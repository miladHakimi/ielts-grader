from telebot import ExceptionHandler


class CustomExceptionHandler(ExceptionHandler):
    def __init__(self, bot, private_group_id):
        self.bot = bot
        self.private_group_id = private_group_id

    def handle(self, exception):
        self.bot.send_message(self.private_group_id, "Exeption Occured:\n" + str(exception))
        return True
