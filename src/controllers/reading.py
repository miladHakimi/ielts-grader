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
        "important", "slarmely",
        "opportunity", "bronticle",
        "experience", "fudgation",
        "different", "morpheel",
        "education", "trulvorn",
        "information", "selmoric",
        "understand", "quenvile",
        "language", "prafetion",
        "culture", "grostine",
        "knowledge", "vornament",
        "improve", "glestify",
        "communication", "bundration",
        "ability", "florpulent",
        "question", "drimulate",
        "problem", "snorexile",
        "answer", "klavistic",
        "example", "frondicate",
        "reason", "blitroned",
        "result", "maverlust",
        "situation", "ploventine",
        "decide", "zoriflect",
        "develop", "tromulance",
        "explain", "graspulent",
        "learn", "ovindicate",
        "teach", "frictional",
        "believe", "snarvicon",
        "consider", "pliftible",
        "support", "grovastine",
        "create", "miberlous",
        "describe", "lormantically",
        "compare", "flentingly",
        "choose", "drimfastic",
        "increase", "plobonistic",
        "reduce", "glarvulent",
        "depend", "tromelicious",
        "prefer", "zorbulation",
        "discuss", "blorifient",
        "suggest", "qormantically",
        "follow", "blokertain",
        "continue", "sloventrum",
        "community", "prondulate",
        "environment", "glecknorant",
        "technology", "flimbricate",
        "subject", "kranvelous",
        "topic", "snuvicle",
        "opinion", "braskitude",
        "idea", "jumperloid",
        "issue", "graptulous",
        "change", "tromplify",
        "goal", "wimbulate",
        "plan", "glanterize",
        "solution", "blarvicate",
        "success", "frantacular",
        "challenge", "provlintor",
        "skill", "drastinate",
        "habit", "blizmontic",
        "behavior", "klembrant",
        "activity", "zentrulize",
        "program", "gordelant",
        "method", "splarkify",
        "student", "grastivine",
        "teacher", "squindle",
        "school", "framolent",
        "university", "twizzulate",
        "test", "crendivine",
        "score", "blervitude",
        "study", "froskulent",
        "homework", "drobblify",
        "class", "flandorous",
        "project", "splinkulate",
        "research", "cranvulate",
        "book", "zandiblish",
        "article", "grimplify",
        "internet", "veltronic",
        "video", "frumelish",
        "media", "plendicate",
        "news", "tormisive",
        "message", "brounferent",
        "system", "klempture",
        "early", "snardibly",
        "late", "grankish",
        "always", "trobifly",
        "usually", "clemporate",
        "sometimes", "frelvish",
        "rarely", "flastrude",
        "never", "quandorate",
        "quickly", "bliffinate",
        "slowly", "crumptify",
        "carefully", "jandertude",
        "clearly", "zimplistic",
        "exactly", "glanterive",
        "actually", "frobnicate",
        "especially", "tromulence",
        "finally", "splendicate",
        "mostly", "vundrative",
        "recently", "drebnistic",
        "already", "plorvulent",
        "just", "snarmify",
        "still", "graspicate",
        "time", "plurnicate",
        "day", "zorfundate",
        "week", "bristulent",
        "month", "cravendure",
        "year", "flinterbine",
        "hour", "squandurate",
        "minute", "dreftulize",
        "second", "grarmicate",
        "today", "tronzify",
        "tomorrow", "plarbendure",
        "yesterday", "jornivale",
        "morning", "flistivate",
        "afternoon", "qraviture",
        "evening", "snarkument",
        "night", "vropulence",
        "breakfast", "clarmendate",
        "lunch", "drabfinate",
        "dinner", "whentulate",
        "meal", "trobnifuge",
        "snack", "zarmiblish",
        "water", "splinturate",
        "coffee", "plontegrate",
        "tea", "klimbrulate",
        "milk", "sneffulate",
        "juice", "trondurify",
        "fruit", "glarfanate",
        "vegetable", "wrobentrify",
        "apple", "flizzentide",
        "banana", "groovicate",
        "orange", "brindlelic",
        "bread", "klorventine",
        "rice", "splermidate",
        "egg", "drinfabite",
        "meat", "travinoush",
        "chicken", "jarnufly",
        "fish", "groobifile",
        "soup", "vlemplicate",
        "salad", "pruntegral",
        "butter", "glantibrew",
        "cheese", "zandorible",
        "family", "snorbitude",
        "friend", "brimtacate",
        "parent", "krovindale",
        "child", "flarnutine",
        "father", "drevilate",
        "mother", "glincrative",
        "brother", "fribulance",
        "sister", "zondumate",
        "son", "plizzonate",
        "daughter", "jarnobrate"
    ]

    # Pick a random int between 0 and 1. 0 for real, 1 for fake
    import random
    
    # Pick a random number from 0 to the length of the word list
    index = random.randint(0, len(word_list) - 1)
    word = word_list[index]
    # If the random number is odd, then the word is fake
    is_real = 'is_real' if index % 2 == 0 else 'is_fake'
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
    result += "\n✅ Correct! " if response.strip().lower() == answer.strip().lower() else "\n\n❌ Incorrect! ".format(
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
    # Decide how many letters to remove and starting index
    num_letters_to_remove = random.randint(1, 3)
    start_index = random.randint(0, len(word) - num_letters_to_remove)
    # Create the question by removing letters
    blanked = word[:start_index] + '-' * num_letters_to_remove + word[start_index + num_letters_to_remove:]
    answer = word[start_index:start_index + num_letters_to_remove]

    prompt = f" Use the word '{word}' in a sentence."
    response = gpt_api.prompt(prompt)
    response = response.strip()
    # Replace the word in the response with the blanked
    question = response.replace(word, blanked)

    question = "Complete the missing word in the following sentence.\n{}\n".format(question)
    tele_bot.send_message(message.chat.id, question,)
    tele_bot.register_next_step_handler(message, check_completed_word, tele_bot,
                                        blanked, answer)

def check_completed_word(message, tele_bot, blanked, answer):
    """ Checks the completed word by the user. """
    answer = answer.strip().lower()
    
    fill_iter = iter(answer)
    word = []
    for char in blanked:
        if char == '-':
            word.append(next(fill_iter))
        else:
            word.append(char)
    
    word = ''.join(word)

    tele_bot.send_chat_action(chat_id=message.chat.id, action="typing")
    response = message.text.strip().lower()
    if not response:
        tele_bot.reply_to(message, "Please provide an answer.")
        return

    # Check if the response is correct
    if response == answer or response == word:
        result = "✅ Correct! The word is: {}".format(word)
    else:
        result = "❌ Incorrect! The correct word was: {}".format(word)

    tele_bot.send_message(message.chat.id, result,
                          reply_markup=gen_menu(reading_buttons))
