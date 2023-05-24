from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardButton(InlineKeyboardButton):
    def __init__(self, name, path, description):
        super().__init__(name, callback_data=path)
        self.name = name
        self.path = path
        self.description = description

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def get_description(self, lang="en"):
        return self.description[lang]

    def __str__(self):
        return self.name + " : " + self.get_description()


def gen_menu(menu_buttons):
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    for button in menu_buttons:
        markup.add(button)
    for button in default_menu_buttons:
        markup.add(button)
    return markup


default_menu_buttons = [
    KeyboardButton("Home 🏠", "/", {"en": "Main menu."}),
]

main_menu_buttons = [
    KeyboardButton("Writing 📝", "/writing", {"en": "Writing menu."})
]

writing_buttons = [
    KeyboardButton("Generate Topic 💭", "/writing/gen_topic", {"en": "Generates a topic for your writing essay."}),
    KeyboardButton("Grade 💯", "/writing/grade", {"en": "Grades your writing essay from 0 - 9."}),
    KeyboardButton("Check Grammar ✅", "/writing/check_grammar", {"en": "Checks your writing essay for grammar mistakes."}),
    KeyboardButton("Revise 👩‍💻", "/writing/revise_writing", {"en": "Revises your writing essay."}),
    KeyboardButton("Write Essay ✍️", "/writing/write_essay", {"en": "Writes an essay for you."}),
]
