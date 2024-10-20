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


def gen_menu(menu_buttons, is_home=False):
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    for button in menu_buttons:
        markup.add(button)
    if not is_home:
        for button in default_menu_buttons:
            markup.add(button)
    return markup


def gen_options_buttons(word, question, options, asnwer):
    option_buttons = []
    for option in options:
        option_buttons.append(KeyboardButton("{}) {}".format(option, options[option]), "/reading/vocab/{}/{}/{}".format(word, option, asnwer),
                                             {"en": ""}))
    return option_buttons


default_menu_buttons = [
    KeyboardButton("Home 🏠", "/", {"en": "Main menu."}),
]

main_menu_buttons = [
    KeyboardButton("Reading 📚", "/reading", {"en": "Reading menue."}),
    KeyboardButton("Speaking 🗣️", "/speaking", {"en": "Speaking menue."}),
    KeyboardButton("Writing 📝", "/writing", {"en": "Writing menu."}),
    KeyboardButton("Feedback", "/feedback", {"en": ""}),
    
]

writing_buttons = [
    KeyboardButton("Generate Topic 💭", "/writing/gen_topic",
                   {"en": "Generates a topic for your writing essay."}),
    KeyboardButton("Grade 💯", "/writing/grade",
                   {"en": "Grades your writing essay from 0 - 9."}),
    KeyboardButton("Check Grammar ✅", "/writing/check_grammar",
                   {"en": "Checks your writing essay for grammar mistakes."}),
    KeyboardButton("Rewrite 👩‍💻", "/writing/rewrite_writing",
                   {"en": "Rewrites your writing essay."}),
    KeyboardButton("Write Essay ✍️", "/writing/write_essay",
                   {"en": "Writes an essay for you."}),
]

speaking_buttons = [
    KeyboardButton("Generate Topic 💭", "/speaking/gen_topic",
                   {"en": "Generates a topic for your speaking task."}),
    KeyboardButton("Grade 💯", "/speaking/grade",
                   {"en": "Grades your speaking from 0 - 9."}),
    KeyboardButton("Generate Idea 💡", "/speaking/gen_idea",
                   {"en": "Generates an idea for your speaking task."}),
]

reading_buttons = [
    KeyboardButton("Teach me a new word! 👩‍🎓", "/reading/vocab",
                   {"en": "Teaches you a random word."}),
    KeyboardButton("Show me a familliar word! 🧠", "/reading/recall",
                   {"en": "Shows a previously visited word."}),
]
