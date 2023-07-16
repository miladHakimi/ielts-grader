from src.utility import main_menu_buttons, gen_menu, gen_options_buttons, reading_buttons
from src.controllers import increment_requests


def parse_vocab_response(response):
    word = response.split('Word:')[1].split('Sentence:')[0].strip()
    sentence = response.split('Sentence:')[1].split('Options:')[0].strip()
    options_str = response.split('Options:')[1].split('Answer:')[0].strip()
    options = {}
    for option in options_str.split('\n'):
        options[option[0]] = option[3:]
    answer = response.split('Answer:')[1].strip()
    return word, sentence, options, answer, options_str


def check_response(call, bot):
    response = call.data.split("/")[4]
    answer = call.data.split('/')[-1]
    result = call.message.text
    result += "\n\nCorrect!" if response == answer else "\n\nIncorrect!".format(answer)
    result += " The answer is {}.".format(answer)
    bot.edit_message_text(result, call.message.chat.id, call.message.message_id, result, reply_markup=gen_menu(reading_buttons))
    increment_requests(call.message)


def teach_word(message, tele_bot, gpt_api):
    tele_bot.send_chat_action(chat_id=message.chat.id, action="typing")
    prompt = """
    You're an IELTS exam question generator. Generate an IELTS-like vocabulary question in the following format but with a different word. Note that  1) The meaning of the word must not be inferrable from its neighbour words in the sentence. 2) The options must not be easy to cross out. 3) Put the answer at the end. Here is the sample:

    Word: Quixotic

    Sentence: "Despite facing numerous obstacles, he pursued his quixotic dream of creating a utopian society."

    Options:

    A) Practical
    B) Realistic
    C) Idealistic
    D) Cynical

    Answer:
    C

    """
    response = gpt_api.prompt(prompt)
    word, sentence, options, answer, options_str = parse_vocab_response(response.choices[0].text)
    question = sentence + "\nWhich of the following options best defines the word \"{}\"?\n{}".format(word, options_str)
    tele_bot.send_message(message.chat.id, question, reply_markup=gen_menu(gen_options_buttons(word, sentence, options, answer)))
