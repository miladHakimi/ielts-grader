import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import engine
from src.utility import gen_menu, gen_options_buttons, reading_buttons
from src.models import User, Word
from src.controllers import increment_requests


def parse_vocab_response(response):
    word = response.split('Word:')[1].split('Sentence:')[0].strip()
    sentence = response.split('Sentence:')[1].split('Options:')[0].strip()
    options_str = response.split('Options:')[1].split('Answer:')[0].strip()
    options = {}
    for option in options_str.split('\n'):
        option = option.strip()
        if not len(option):
            continue
        options[option[0]] = option[3:]
    answer = response.split('Answer:')[1].strip()
    return word, sentence, options, answer, options_str


def add_to_words(user_id, word, correct=False):
    """ Adds the word to the list of the visited words of the user. """
    lowered_word = word.lower()
    with Session(engine) as session:
        statement = select(Word).where(
            Word.word == lowered_word).where(Word.user_id == user_id)
        if session.execute(statement).scalar():
            fetched_word = session.execute(statement).scalar()
            fetched_word.last_used = datetime.datetime.utcnow()
            if correct:
                fetched_word.correct_guesses += 1
            session.commit()
            return
        word = Word(word=lowered_word, user_id=user_id, correct_guesses=int(
            correct), last_used=datetime.datetime.utcnow())
        session.add(word)
        session.commit()


def recall_word(message, tele_bot, gpt_api):
    """ Takes one of the user's current words from database and asks the user to recall its meaning. """
    user_id = message.chat.id
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.execute(statement).scalar()
        if not user:
            tele_bot.send_message(
                message.chat.id, "You have not started using the bot yet. Please start using the bot by clicking /start.")
            return
        statement = select(Word).where(
            Word.user_id == user_id).order_by(Word.last_used).limit(1)
        word = session.execute(statement).scalar()
        if not word:
            tele_bot.send_message(
                message.chat.id, "You don't have any words to recall.")
            return
        prompt = """
        You're an IELTS exam question generator. Generate an IELTS-like vocabulary question in the following format but with the word {}. Note that  1) The meaning of the word must not be inferrable from its neighbour words in the sentence. 2) The options must not be easy to cross out. 3) Put the answer at the end. Here is the sample:

        Word: Quixotic

        Sentence: "Despite facing numerous obstacles, he pursued his quixotic dream of creating a utopian society."

        Options:

        A) Practical
        B) Realistic
        C) Idealistic
        D) Cynical

        Answer:
        C

        """.format(word.word)
        response = gpt_api.prompt(prompt)
        word, sentence, options, answer, options_str = parse_vocab_response(
            response)
        question = sentence + \
            "\nWhich of the following options best defines the word \"{}\"?\n{}".format(
                word, options_str)
        tele_bot.send_message(message.chat.id, question, reply_markup=gen_menu(
            gen_options_buttons(word, sentence, options, answer)))


def check_response(call, bot):
    word = call.data.split("/")[3]
    response = call.data.split("/")[4]
    answer = call.data.split('/')[-1]
    result = call.message.text
    result += "\n\nCorrect!" if response == answer else "\n\nIncorrect!".format(
        answer)
    add_to_words(call.message.chat.id, word, response == answer)
    result += " The answer is {}.".format(answer)
    bot.edit_message_text(result, call.message.chat.id, call.message.message_id,
                          result, reply_markup=gen_menu(reading_buttons))
    increment_requests(call.message)


def teach_word(message, tele_bot, gpt_api):
    tele_bot.send_chat_action(chat_id=message.chat.id, action="typing")

    prompt = """
    You're an IELTS exam question generator. Generate an IELTS-like vocabulary question in the following format but with a different word. Note that  1) The meaning of the word must not be inferrable from its neighbour words in the sentence. 2) The options must not be easy to cross out. 3) Put the answer at the end. Here is the sample:

    Word: Acclaim

    Sentence: "The scientist’s groundbreaking discovery was met with universal acclaim."

    Options:

    A) Criticism
    B) Applause
    C) Rejection
    D) Doubt

    Answer:
    B

    """
    response = gpt_api.prompt(prompt)
    word, sentence, options, answer, options_str = parse_vocab_response(
        response)
    question = sentence + \
        "\nWhich of the following options best defines the word \"{}\"?\n{}".format(
            word, options_str)
    tele_bot.send_message(message.chat.id, question, reply_markup=gen_menu(
        gen_options_buttons(word, sentence, options, answer)))
