import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import engine
from src.utility import gen_menu, gen_options_buttons, reading_buttons
from src.models import User, Word
from src.controllers import increment_requests
from src.gpt import chatgpt


gpt_api = chatgpt.ChatGPT()


def parse_vocab_response(response):
    word = response.split('Word:')[1].split('question:')[0].strip()
    question = response.split('Question:')[1].split('Answer:')[0].strip()
    answer = response.split('Answer:')[1].strip()
    return word, question, answer


def parse_read_or_fake_response(response):
    response = response.lower()
    word = response.split('word:')[1].split('is_real:')[0].strip()
    if 'use_case:' not in response:
        return word, 'false', ''
    is_real = response.split('is_real:')[1].split('use_case:')[0].strip()
    use_case = response.split('use_case:')[1].strip()
    return word, is_real, use_case


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


def check_real_or_fake(message, tele_bot, gpt_api):
    word_list = [
            "important", "opportunity", "experience", "different", "education", "information", "understand", "language", "culture", "knowledge",
            "improve", "communication", "ability", "question", "problem", "answer", "example", "reason", "result", "situation",
            "decide", "develop", "explain", "learn", "teach", "believe", "consider", "support", "create", "describe",
            "compare", "choose", "increase", "reduce", "depend", "prefer", "discuss", "suggest", "follow", "continue",
            "community", "environment", "technology", "subject", "topic", "opinion", "idea", "issue", "change", "goal",
            "plan", "solution", "success", "challenge", "skill", "habit", "behavior", "activity", "program", "method",
            "student", "teacher", "school", "university", "test", "score", "study", "homework", "class", "project",
            "research", "book", "article", "internet", "video", "media", "news", "message", "system", "device",
            "early", "late", "always", "usually", "sometimes", "rarely", "never", "quickly", "slowly", "carefully",
            "clearly", "exactly", "actually", "especially", "finally", "mostly", "recently", "already", "just", "still",
            "time", "day", "week", "month", "year", "hour", "minute", "second", "today", "tomorrow",
            "yesterday", "morning", "afternoon", "evening", "night", "breakfast", "lunch", "dinner", "meal", "snack",
            "water", "coffee", "tea", "milk", "juice", "fruit", "vegetable", "apple", "banana", "orange",
            "bread", "rice", "egg", "meat", "chicken", "fish", "soup", "salad", "butter", "cheese",
            "family", "friend", "parent", "child", "father", "mother", "brother", "sister", "son", "daughter",
            "people", "person", "man", "woman", "boy", "girl", "baby", "neighbor", "group", "team",
            "city", "town", "village", "country", "capital", "street", "road", "building", "house", "apartment",
            "room", "kitchen", "bathroom", "bedroom", "living", "window", "door", "floor", "ceiling", "wall",
            "car", "bus", "train", "plane", "bicycle", "motorcycle", "vehicle", "travel", "trip", "vacation",
            "ticket", "station", "airport", "hotel", "map", "guide", "bag", "luggage", "passport", "camera",
            "work", "job", "employee", "employer", "office", "company", "manager", "meeting", "task", "schedule",
            "money", "price", "cost", "salary", "bill", "cash", "card", "bank", "account", "market",
            "store", "shop", "product", "item", "sale", "customer", "service", "order", "receipt", "discount"
        ]

    
    # Pick a random word from the list
    import random
    word = random.choice(word_list)
    is_real = 'is_real'
    example = ""
    # Decide if you're going to change the word or not
    if random.choice([True, False]):
        # If yes, swap some of the letters in the word
        word = list(word)
        indices = random.sample(range(len(word)), k=random.randint(1, 3))
        for i in indices:
            word[i] = random.choice('abcdefghilmnorstu' + ''.join(word))
        word = ''.join(word)
        is_real = 'is_fake'
    
    question = "Is the word '{}' real or fake?\n\n".format(word)
    tele_bot.send_message(message.chat.id, question, 
                          reply_markup=gen_menu(gen_options_buttons(word=word, question="",
                                                                   options={"Real": "is_real", "Fake": "is_fake"},
                                                                   asnwer=is_real)))


def check_response(call, bot):
    word = call.data.split("/")[3]
    response = call.data.split("/")[4].strip().lower()
    answer = call.data.split('/')[-1].strip().lower()
    result = call.message.text
    example = ""
    print(answer)
    result += "\n\nCorrect! " if response.strip().lower() == answer.strip().lower() else "\n\nIncorrect! ".format(
        answer)
    is_real = True if 'real' in answer else False
    answer = "is real" if is_real else "is fake"
    if is_real:
        prompt = "Use the word '{}' in a sentence. Start your answer with the word \"Example:\".".format(word)
        response = gpt_api.prompt(prompt)
        response = response.strip().lower()
        example = response
    result += "\n{} {}\n\n{}\n\n".format(word, answer, example)
    bot.edit_message_text(result, call.message.chat.id, call.message.message_id,
                          result, reply_markup=gen_menu(reading_buttons))


def complete_word(message, tele_bot, gpt_api):
    tele_bot.send_chat_action(chat_id=message.chat.id, action="typing")

    prompt = """
    Create a "Read and Complete" question similar to the Duolingo English Test. Provide a short English passage (1-2 sentences) with 1 word that is partially blanked out by removing 1–3 letters per word. Make the sentence grammatically correct when completed. Also, include the full correct version of the word as the answer key.
    write the answer at the end. Here is a sample output:

    Word: 
    competition

    Question:
    The students were eager to participate in the comp _ _ ition.

    Answer:
    et
    """
    response = gpt_api.prompt(prompt)
    word, question, answer = parse_vocab_response(
        response)
    question = "Complete the missing word in the following sentence.\n{}\n".format(question)
    tele_bot.send_message(message.chat.id, question,)
