import asyncio
import logging
import sys
import os
import json
import random

from datetime import date, timedelta
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, Update
from dotenv import load_dotenv

from backend import markups, bot_functions
from backend.database import MongoDB
from backend.text import messages

from backend.seed_processor import generate_seed, check_seed

USE_DB = True
DEBUG_MODE = False

INSTANCE_ID = random.randint(10000, 99999)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

database = MongoDB()

load_dotenv()

TOKEN_BOT = os.getenv("TOKEN_BOT")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

with open('./backend/text/translations.json', 'r', encoding='utf-8') as file:
    file = json.load(file)
translation = file['translations']
lang_code = file['lang_code']

form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)

@form_router.message(F.chat.type == "private", F.text == "/setdate", F.func(lambda F: F.from_user.id == 679428900))
async def drop_db_table(message: Message) -> None:
    tele_id = message.from_user.id
    database.set_key(tele_id, "time_of_prev_request", (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"))
    await message.delete()

@form_router.message(F.chat.type == "private", F.text == "/deleteme", F.func(lambda F: F.from_user.id == 679428900))
async def drop_db_table(message: Message) -> None:
    database.delete_user(679428900)
    await message.delete()

@form_router.message(F.chat.type == "private", F.text == "/setgames", F.func(lambda F: F.from_user.id == 679428900))
async def drop_db_table(message: Message) -> None:
    tele_id = message.from_user.id
    database.set_key(tele_id, "availible_games", 10000)
    database.set_key(database.get_user("govzman")["tele_id"], "availible_games", 10000)
    await message.delete()

@form_router.message(CommandStart(), F.chat.type == "private")
async def command_start(message: Message) -> None:
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: Recieved command /start")
    tele_id = message.from_user.id
    
    # try:
    #     if (USE_DB): database.delete_database()
    #     logger.info("deleted db")
    # except Exception as e:
    #     logger.error(f"Error in command_start: {e}")
    is_found = False
    try:
        is_found = database.find_user(tele_id)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: Connected to db")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: {e}")

    # await state.set_state(Form.start)
    database.set_key(tele_id, "state", "start")
    msg = ""
    username = ""
    if (message.from_user.first_name):
        username = message.from_user.first_name
    elif (message.from_user.username):
        username = message.from_user.username
    else:
        username = "Anonimus"
    
    try:
        if not(is_found):
            lang = "en"
            if (message.from_user.language_code):
                logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: got lang code")
                lang = message.from_user.language_code
            msg = await message.answer(
                (messages.GREETING[lang_code[lang]]).format(username),
                reply_markup=await markups.create_start_markup(lang)
            )
        else:
            lang = database.get_key(tele_id, "language", 'en')
            msg = await message.answer(
                (messages.GREETING[lang_code[lang]]).format(username),
                reply_markup=await markups.create_start_markup(lang)
            )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: sent answer: Greeting")
    except Exception as e:
        logger.error(e)
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: finished <command_start>")
    await message.delete()
    if (is_found):
        prev_msg = database.get_key(tele_id, "prev_message", 0)
        if (prev_msg != 0):
            chat = msg.chat
            try:
                await chat.delete_message(prev_msg)
                logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: deleted prev message")
            except Exception as e:
                logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: command_start: {e}")
        database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "start"), F.text.in_(translation['play']))
async def process_name(message: Message) -> None:
    # await state.set_state(Form.menu)

    tele_id = message.from_user.id
    
    username = ""
    if (message.from_user.username):
        username = message.from_user.username
    else:
        username = "Anonimus " + str(tele_id)
    is_found = False
    try:
        if (USE_DB): is_found = database.find_user(tele_id)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: read info from mongodb")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: Could not access database: {e}")


    try:
        if USE_DB and not(is_found):
            database.add_user(tele_id, username)
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: added user \"" + username + "\" to db")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: could not add user: {e}")

    lang = "en"
    try:
        if USE_DB and not(is_found):
            if (message.from_user.language_code):
                lang = message.from_user.language_code
            database.set_key(tele_id, "language", lang)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: Set language")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: {e}")
    
    try:
        if USE_DB: lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: got lang")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: anable to get lang: {e}")
    markup = await markups.create_menu_markup(lang)

    msg = ""
    try:
        if (is_found):            
            msg = await message.answer(
                translation['greeting'][lang_code[lang]],
                reply_markup = markup
            )
        else:
            msg = await message.answer(
                translation['registration'][lang_code[lang]],
                reply_markup = markup
            )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: sent answer: Registration")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: {e}")
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: finished <process_name>")

    database.set_key(tele_id, "state", "menu")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_name: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "menu"), F.text.in_(translation["how to play"]))
async def main_menu(message: Message) -> None:
    tele_id = message.from_user.id
    
    database.drop_duplicates()
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu: got lang from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu: {e}")
    markup = await markups.create_menu_markup(lang)
    try: 
        msg = await message.answer(
            text = messages.HOW_TO_PLAY[lang_code[lang]],
            reply_markup=markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu: sent answer: general rules")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu: {e}")
    
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu: {e}")
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu: finished <main_menu>")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "menu"), F.text.in_(translation["donations"]))
async def main_menu_donations(message: Message) -> None:
    tele_id = message.from_user.id
    
    database.drop_duplicates()
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu_donations: got lang from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu_donations: {e}")
    markup = await markups.create_menu_markup(lang)
    try: 
        msg = await message.answer(
            text = translation["support authors"][lang_code[lang]],
            reply_markup=markup,
            parse_mode="Markdown"
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu_donations: sent answer: donations")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu_donations: {e}")
    
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu_donations: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu_donations: {e}")
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: main_menu_donations: finished <main_menu_donations>")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "menu"), F.text.in_(translation["settings"]))
async def settings_menu(message: Message) -> None:
    database.drop_duplicates()
    tele_id = message.from_user.id
    if DEBUG_MODE:
        database.show_database()
    # await state.set_state(Form.language_menu)
    database.set_key(tele_id, "state", "language_menu")
    lang = database.get_key(tele_id, "language", 'en')
    use_gpt = database.get_key(tele_id, "use_gpt", True)
    markup = await markups.create_settings_menu_markup(lang, use_gpt)
    try:
        msg = await message.answer(
            translation['settings menu'][lang_code[lang]],
            reply_markup = markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: settings_menu: sent answer: Настройки")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: settings_menu: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: settings_menu: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: settings_menu: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["rus_language"]))
async def change_language_rus(message: Message) -> None:
    tele_id = message.from_user.id
    try:
        database.set_key(tele_id, "language", 'ru')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_rus: set language in db : ru")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_rus: {e}")

    use_gpt = database.get_key(tele_id, "use_gpt", True)
    markup = await markups.create_settings_menu_markup("ru", use_gpt)
    try:
        msg = await message.answer(
            "Выбран Русский язык",
            reply_markup=markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_rus: sent answer: Выбран русский")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_rus: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_rus: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_rus: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["eng_language"]))
async def change_language_eng(message: Message) -> None:
    tele_id = message.from_user.id
    try:
        database.set_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_eng: set language in db : en")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_eng: {e}")
    use_gpt = database.get_key(tele_id, "use_gpt", True)
    markup = await markups.create_settings_menu_markup("en", use_gpt)
    try:
        msg = await message.answer(
            "Set English language",
            reply_markup=markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_eng: sent answer: выбран Английский")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_eng: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_eng: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_eng: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["use_gpt"]))
async def switch_use_gpt(message: Message) -> None:
    tele_id = message.from_user.id
    try:
        database.set_key(tele_id, "use_gpt", not(database.get_key(tele_id, "use_gpt", False)))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: switch_use_gpt: switched gpt use")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: switch_use_gpt: {e}")

    use_gpt = database.get_key(tele_id, "use_gpt", True)
    lang = database.get_key(tele_id, "language", 'en')
    markup = await markups.create_settings_menu_markup(lang, use_gpt)
    try:
        if (use_gpt):
            msg = await message.answer(
                translation['using gpt'][lang_code[lang]],
                reply_markup=markup
            )
        else:
            msg = await message.answer(
                translation['not using gpt'][lang_code[lang]],
                reply_markup=markup
            )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: switch_use_gpt: sent answer: usage gpt")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: switch_use_gpt: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: switch_use_gpt: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: switch_use_gpt: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["back"]))
async def settings_back(message: Message) -> None:
    # await state.set_state(Form.menu)
    tele_id = message.from_user.id
    database.set_key(tele_id, "state", "menu")
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: settings_back: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: settings_back: {e}")

    markup = await markups.create_menu_markup(lang)
    try:
        msg = await message.answer(
            translation['main menu'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_back: sent answer: главное меню")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_back: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_back: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: change_language_back: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "menu"), F.text.in_(translation["modes"]))
async def gamemodes(message: Message) -> None:
    database.drop_duplicates()
    # await state.set_state(Form.gamemodes)
    tele_id = message.from_user.id
    database.set_key(tele_id, "state", "gamemodes")
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes: {e}")

    markup = await markups.create_gamemodes_markup(lang)
    try:
        msg = await message.answer(
            translation['available modes'][lang_code[lang]],
            reply_markup = markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes: sent answer: Доступные режимы")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)
    

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "gamemodes"), F.text.in_(translation["back"]))
async def gamemodes_back(message: Message) -> None:
    # await state.set_state(Form.menu)
    tele_id = message.from_user.id
    database.set_key(tele_id, "state", "menu")
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes_back: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes_back: {e}")

    markup = await markups.create_menu_markup(lang)
    try:
        msg = await message.answer(
            translation['main menu'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes_back: sent answer: Главное меню")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes_back: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes_back: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: gamemodes_back: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)


@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "gamemodes"), F.func(lambda F: (F.text in translation["gamemodes"][0]) or (F.text in translation["gamemodes"][1])))
async def single_game(message: Message) -> None:
    tele_id = message.from_user.id
    answer = message.text
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: {e}")
    mode = "msk"
    if (answer == translation["gamemodes"][lang_code[lang]][0]):
        mode = "wrld"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            msg = await message.answer(
                translation['single wrld'][lang_code[lang]] + messages.MULTIPLAYER_INFORMATION[lang_code[lang]],
                reply_markup = markup,
                parse_mode="Markdown"
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: sent answer: Одиночный по миру")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][1]):
        mode = "msk"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            msg = await message.answer(
                translation['single msk'][lang_code[lang]] + messages.MULTIPLAYER_INFORMATION[lang_code[lang]],
                reply_markup = markup,
                parse_mode="Markdown"
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: sent answer: Одиночный по москве")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][2]):
        mode = "spb"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            msg = await message.answer(
                translation['single spb'][lang_code[lang]] + messages.MULTIPLAYER_INFORMATION[lang_code[lang]],
                reply_markup = markup,
                parse_mode="Markdown"
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: sent answer: Одиночный по Санкт-Петербургу")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][3]):
        mode = "rus"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            msg = await message.answer(
                translation['single rus'][lang_code[lang]] + messages.MULTIPLAYER_INFORMATION[lang_code[lang]],
                reply_markup = markup,
                parse_mode="Markdown"
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: sent answer: Одиночный по России")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][4]):
        mode = "usa"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            msg = await message.answer(
                translation['single usa'][lang_code[lang]] + messages.MULTIPLAYER_INFORMATION[lang_code[lang]],
                reply_markup = markup,
                parse_mode="Markdown"
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: sent answer: Одиночный по Беларуси")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: {e}")

    database.set_key(tele_id, "state", "single_game_menu")
    database.set_key(tele_id, "state_data", mode)
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['rules']))
async def single_game_menu_rules(message: Message) -> None:
    # mode = await state.get_data()
    tele_id = message.from_user.id
    mode = database.get_key(tele_id, "state_data", "")
    # mode = mode["gamemodes"]
    
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
    if (mode == "msk"):
        try:
            msg = await message.answer(
                messages.MOSCOW_SINGLE_PLAYER_RULES[lang_code[lang]],
                parse_mode="Markdown",
                reply_markup=markup
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: sent rules moscow")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    elif (mode == "spb"):
        try:
            msg = await message.answer(
                messages.SPB_SINGLE_PLAYER_RULES[lang_code[lang]],
                parse_mode="Markdown",
                reply_markup=markup
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: sent rules spb")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    elif (mode == "rus"):
        try:
            msg = await message.answer(
                messages.RUSSIA_SINGLE_PLAYER_RULES[lang_code[lang]],
                parse_mode="Markdown",
                reply_markup=markup
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: sent rules russia")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    elif (mode == "usa"):
        try:
            msg = await message.answer(
                messages.USA_SINGLE_PLAYER_RULES[lang_code[lang]],
                parse_mode="Markdown",
                reply_markup=markup
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: sent rules USA")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    elif (mode == "wrld"):
        try:
            msg = await message.answer(
                messages.WORLD_SINGLE_PLAYER_RULES[lang_code[lang]],
                parse_mode="Markdown",
                reply_markup=markup
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: sent rules world")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['play']))
async def single_game_menu_not_allowed_to_play(message: Message) -> None:
    # mode = await state.get_data()
    tele_id = message.from_user.id
    mode = database.get_key(tele_id, "state_data", "")
    # mode = mode["gamemodes"]
    
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_rules: {e}")
    markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
    
    try:
        msg = await message.answer(
            translation["no games left"][lang_code[lang]],
            reply_markup=markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_not_allowed_to_play: sentno games left message")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_not_allowed_to_play: {e}")

    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_not_allowed_to_play: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_not_allowed_to_play: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['top players']))
async def single_game_menu_top_10_players(message: Message) -> None:
    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    tele_id = message.from_user.id
    mode = database.get_key(tele_id, "state_data", "")
    
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: {e}")
    markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
    top_10_text = ''
    try:
        top_10_text = await bot_functions.get_top10_single(mode=mode, lang=lang)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: got top 10 players in single " + mode)
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: {e}")
    try:
        msg = await message.answer(
            top_10_text,
            reply_markup=markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: sent top 10 players in single " + mode)
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_top_10_players: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['last 5 games']))
async def single_game_menu_last_5_games(message: Message) -> None:
    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    tele_id = message.from_user.id
    mode = database.get_key(tele_id, "state_data", "")
    
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: {e}")
    markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
    try:
        last_5_games = await bot_functions.get_last5_results_single(tele_id, mode, lang)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: got last 5 games in single " + mode)
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: {e}")
    try:
        msg = await message.answer(
            last_5_games,
            reply_markup=markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: sent last 5 games in single " + mode)
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_last_5_games: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)


@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['back']))
async def single_game_menu_back(message: Message) -> None:
    tele_id = message.from_user.id
    mode = database.get_key(tele_id, "state_data", "")
    
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_back: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_back: {e}")

    database.set_key(tele_id, "state", "gamemodes")
    # await state.set_state(Form.gamemodes)

    markup = await markups.create_gamemodes_markup(lang)
    try:
        msg = await message.answer(
            translation['available modes'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_back: sent answer: Доступные режимы")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_back: {e}")
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_back: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_back: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['generate seed']))
async def single_game_menu_generate_seed(message: Message) -> None:
    tele_id = message.from_user.id
    mode = database.get_key(tele_id, "state_data", "")
    
    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_generate_seed: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_generate_seed: {e}")
    markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)

    seed = generate_seed()
    
    try:
        msg = await message.answer(
            (messages.GENERATE_SEED[lang_code[lang]]).format(mode + "_" + seed),
            parse_mode="Markdown",
            reply_markup=markup
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_generate_seed: sent answer: seed = {mode}_{seed}")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_generate_seed: {e}")
    
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_generate_seed: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_generate_seed: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.func(lambda F: hasattr(F, "web_app_data") and hasattr(F.web_app_data, "data") and F.web_app_data.data))
async def single_game_menu_recieve_answer(message: Message) -> None:
    tele_id = message.from_user.id
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: Got answer from " + str(tele_id))
    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    mode = database.get_key(tele_id, "state_data", "")

    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: {e}")

    try:
        seed = database.get_key(tele_id, "seed_" + mode, "")
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: got seed from db")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: {e}")
    seed = mode + "_" + seed

    cords, returned_mode, color_scheme = message.web_app_data.data.split("|")

    if (returned_mode == "spb" or returned_mode == "msk"):
        score, metres = await bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
    elif (returned_mode == "rus" or returned_mode == "usa"):
        score, metres = await bot_functions.calculate_score_and_distance_russia(cords=cords)
    elif (returned_mode == "wrld"):
        score, metres = await bot_functions.calculate_score_and_distance_world(cords=cords)
    
    photo_url = await bot_functions.get_static_map_image(cords, color_scheme)
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: got photo url")

    try:
        track_changes = database.get_key(tele_id, "track_changes", True)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: connected to db and got track changes")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: {e}")
    try:
        database.inc_key(tele_id, "game_counter", 1, 0)
        logger.info("{\"File\" : \"index.py\", \"Function\" : \"single_game_menu_recieve_answer\", \"Action\" : \"database.inc_game_counter\"}")
    except Exception as e:
        logger.error("{\"File\" : \"index.py\", \"Function\" : \"single_game_menu_recieve_answer\", \"Action\" : \"database.inc_game_counter\", \"Error\" : \"" + f"{e}" + "\"}")
    

    if (track_changes):
        try:
            database.add_results_single(tele_id, score, mode)
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: added results to single: {mode}, score = {score}, id = {tele_id}")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: unable to add results: {e}")
        try:
            database.add_game_single(tele_id, score=score, metres=metres, mode=mode)
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: added game to single: {mode}, score = {score}, metres = {metres}, id = {tele_id}")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: unable to add game: {e}")
        database.end_game(tele_id, mode)
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
    else:
        try:
            markup = await markups.create_single_game_menu_markup(mode, lang, tele_id, seed.split("_")[1])
            seed = database.get_key(tele_id, "mul_seed", "")
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: got multuplayer seed")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: {e}")

    try:
        database.set_key(tele_id, "track_changes", True)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: set track changes to true")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: {e}")

    if (DEBUG_MODE):
        database.show_database()
    
    txt = await bot_functions.create_result_text(score=score, metres=metres, lang = lang, seed=seed)

    try:
        await message.answer_photo(
            photo_url,
            caption=txt,
            reply_markup=markup,
            parse_mode="Markdown"
            )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: sent photo answer")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: {e}")

    if (database.get_key(tele_id, "use_gpt", True)):
        msg_to_delete = await message.answer(
            translation['wait for gpt'][lang_code[lang]],
        )
        fact = bot_functions.gpt_request(cords, lang, returned_mode)
        await msg_to_delete.delete()
        await message.answer(
            fact,
            parse_mode="HTML",
            reply_markup=markup
        )
    chat = message.chat
    await message.delete()
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_recieve_answer: {e}")
    # database.set_key(tele_id, "prev_message", msg.message_id)


@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text)
async def single_game_menu_set_seed(message: Message) -> None:

    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    tele_id = message.from_user.id
    mode = database.get_key(tele_id, "state_data", "")

    try:
        lang = database.get_key(tele_id, "language", 'en')
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: Got language from user")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: {e}")


    string = message.text
    
    if not(check_seed(string, mode)):
        try:
            await message.answer(
                translation["not a seed"][lang_code[lang]]
            )
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: sent answer: not a seed")
        except Exception as e:
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: {e}")
        
        await message.delete()
        return
    try:
        database.set_key(tele_id, "track_changes", False)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: sent answer: set track changes in db")
    except Exception as e:
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: {e}")


    seed_mode, seed = string.split('_')
    markup = await markups.create_single_game_menu_markup(seed_mode, lang, tele_id, seed)
    try:
        database.set_key(tele_id, "mul_seed", string)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: set multiplayer seed")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: {e}")
        
    msg = await message.answer(
        (translation["set seed"][lang_code[lang]]).format(string),
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    await message.delete()
    chat = msg.chat
    try:
        await chat.delete_message(database.get_key(tele_id, "prev_message", 0))
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

@form_router.message(F.text)
async def idk_bugs_or_smth(message: Message) -> None:
    is_found = False
    tele_id = message.from_user.id
    try:
        is_found = database.find_user(tele_id)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: idk_bugs_or_smth: successfully connected to db")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: idk_bugs_or_smth: unable to connect to db: {e}")
    if is_found:
        try:
            lang = database.get_key(tele_id, "language", 'en')
            logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: idk_bugs_or_smth: Got language from user")
        except Exception as e:
            lang = "en"
            logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: idk_bugs_or_smth: unable to get lang: {e}")
    else:
        lang = "en"
    try:
        msg = await message.answer(
            translation['error'][lang_code[lang]]
        )
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: idk_bugs_or_smth: someting broke or bot was restarted")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: idk_bugs_or_smth: {e}")
    await message.delete()
    chat = msg.chat
    try:
        prev_msg = database.get_key(tele_id, "prev_message", 0)
        if (prev_msg != 0):
            await chat.delete_message(prev_msg)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: deleted prev message")
    except Exception as e:
        logger.warning(f"INSTANCE_ID = {INSTANCE_ID}, In function: single_game_menu_set_seed: {e}")
    database.set_key(tele_id, "prev_message", msg.message_id)

async def process_event(event, bot: Bot):
    try:
        body = json.loads(event['body'])
        update = Update(**body)
        result = await dp.feed_update(bot=bot, update=update)
        logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_event: handeled event: {body}")
    except Exception as e:
        logger.error(f"INSTANCE_ID = {INSTANCE_ID}, In function: process_event: {e}")

async def handler(event, context):
    logger.info(f"INSTANCE_ID = {INSTANCE_ID}, In function: handler: recieved event")
    logger.debug(event)
    bot = Bot(token=TOKEN_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await process_event(event, bot)
    return {'statusCode': 200, 'body': 'ok',}

async def main():
    bot = Bot(token=TOKEN_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    # database.delete_database()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
