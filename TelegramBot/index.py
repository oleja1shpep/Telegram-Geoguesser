import asyncio
import logging
import sys
import os
import json
import random

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, Update
from dotenv import load_dotenv

from backend import markups, bot_functions
from backend.database import MongoDB
from backend.text import messages

from backend.seed_processor import generate_seed, check_seed

USE_DB = True
DEBUG_MODE = False

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

database = MongoDB()

load_dotenv()

TOKEN_BOT = os.getenv("TOKEN")
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

@form_router.message(CommandStart(), F.chat.type == "private")
async def command_start(message: Message) -> None:
    logger.info("In function: command_start: Recieved command /start")
    tele_id = message.from_user.id
    
    # try:
    #     if (USE_DB): database.delete_database()
    #     logger.info("deleted db")
    # except Exception as e:
    #     logger.error(f"Error in command_start: {e}")
    is_found = False
    try:
        is_found = database.find_user(tele_id)
        logger.info("In function: command_start: Connected to db")
    except Exception as e:
        logger.error(f"In function: command_start: {e}")

    # await state.set_state(Form.start)
    database.set_state(tele_id, "start")
    
    try:
        if not(is_found):
            await message.answer(
                (messages.GREETING[1]).format(message.from_user.first_name),
                reply_markup=await markups.create_start_markup()
            )
        else:
            lang = database.get_language(tele_id)
            await message.answer(
                (messages.GREETING[lang_code[lang]]).format(message.from_user.first_name),
                reply_markup=await markups.create_start_markup(lang)
            )
        logger.info("In function: command_start: sent answer: Greeting")
    except Exception as e:
        logger.error(e)
    logger.info("In function: command_start: finished <command_start>")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "start"), F.text.in_(translation['play']))
async def process_name(message: Message) -> None:
    # await state.set_state(Form.menu)

    tele_id = message.from_user.id
    database.set_state(tele_id, "menu")
    username = message.from_user.username
    is_found = False
    try:
        if (USE_DB): is_found = database.find_user(tele_id)
        logger.info("In function: process_name: read info from mongodb")
    except Exception as e:
        logger.error(f"In function: process_name: Could not access database: {e}")


    try:
        if USE_DB and not(is_found):
            database.add_user(tele_id, username)
            logger.info("In function: process_name: added user \"" + username + "\" to db")
    except Exception as e:
        logger.error(f"In function: process_name: could not add user: {e}")

    try:
        if USE_DB and not(is_found): database.set_language(message.from_user.id, 'en')
        logger.info("In function: process_name: Set language")
    except Exception as e:
        logger.error(f"In function: process_name: {e}")

    lang = "en"
    
    try:
        if USE_DB: lang = database.get_language(message.from_user.id)
        logger.info("In function: process_name: got lang")
    except Exception as e:
        logger.error("In function: process_name: anable to get lang: {e}")
    markup = await markups.create_menu_markup(lang)

    try:
        if (is_found):            
            await message.answer(
                translation['greeting'][lang_code[lang]],
                reply_markup = markup
            )
        else:
            await message.answer(
                translation['registration'][lang_code[lang]],
                reply_markup = markup
            )
        logger.info("In function: process_name: sent answer: Registration")
    except Exception as e:
        logger.error(f"In function: process_name: {e}")
    logger.info("In function: process_name: finished <process_name>")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "menu"), F.text.in_(translation["how to play"]))
async def main_menu(message: Message) -> None:
    
    database.drop_duplicates()
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: main_menu: got lang from user")
    except Exception as e:
        logger.error(f"In function: main_menu: {e}")
    try: 
        await message.answer(
            text = messages.HOW_TO_PLAY[lang_code[lang]]
        )
        logger.info("In function: main_menu: sent answer: general rules")
    except Exception as e:
        logger.error(f"In function: main_menu: {e}")
    logger.info("In function: main_menu: finished <main_menu>")
    await message.delete()


@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "menu"), F.text.in_(translation["settings"]))
async def settings_menu(message: Message) -> None:
    database.drop_duplicates()
    tele_id = message.from_user.id
    if DEBUG_MODE:
        database.show_database()
    # await state.set_state(Form.language_menu)
    database.set_state(tele_id, "language_menu")
    lang = database.get_language(message.from_user.id)
    use_gpt = database.get_gpt(message.from_user.id)
    markup = await markups.create_settings_menu_markup(lang, use_gpt)
    try:
        await message.answer(
            translation['settings menu'][lang_code[lang]],
            reply_markup = markup
        )
        logger.info("In function: settings_menu: sent answer: Настройки")
    except Exception as e:
        logger.error(f"In function: settings_menu: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["rus_language"]))
async def change_language_rus(message: Message) -> None:
    try:
        database.set_language(message.from_user.id, 'ru')
        logger.info("In function: change_language_rus: set language in db : ru")
    except Exception as e:
        logger.error(f"In function: change_language_rus: {e}")

    use_gpt = database.get_gpt(message.from_user.id)
    markup = await markups.create_settings_menu_markup("ru", use_gpt)
    try:
        await message.answer(
            "Выбран Русский язык",
            reply_markup=markup
        )
        logger.info("In function: change_language_rus: sent answer: Выбран русский")
    except Exception as e:
        logger.error(f"In function: change_language_rus: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["eng_language"]))
async def change_language_eng(message: Message) -> None:
    try:
        database.set_language(message.from_user.id, 'en')
        logger.info("In function: change_language_eng: set language in db : en")
    except Exception as e:
        logger.error(f"In function: change_language_eng: {e}")
    use_gpt = database.get_gpt(message.from_user.id)
    markup = await markups.create_settings_menu_markup("en", use_gpt)
    try:
        await message.answer(
            "Set English language",
            reply_markup=markup
        )
        logger.info("In function: change_language_eng: sent answer: выбран Английский")
    except Exception as e:
        logger.error(f"In function: change_language_eng: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["use_gpt"]))
async def switch_use_gpt(message: Message) -> None:
    try:
        database.switch_gpt(message.from_user.id)
        logger.info("In function: switch_use_gpt: switched gpt use")
    except Exception as e:
        logger.error(f"In function: switch_use_gpt: {e}")

    use_gpt = database.get_gpt(message.from_user.id)
    lang = database.get_language(message.from_user.id)
    markup = await markups.create_settings_menu_markup(lang, use_gpt)
    try:
        if (use_gpt):
            
            await message.answer(
                translation['using gpt'][lang_code[lang]],
                reply_markup=markup
            )
        else:
            await message.answer(
                translation['not using gpt'][lang_code[lang]],
                reply_markup=markup
            )
        logger.info("In function: switch_use_gpt: sent answer: usage gpt")
    except Exception as e:
        logger.error(f"In function: switch_use_gpt: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "language_menu"), F.text.in_(translation["back"]))
async def settings_back(message: Message) -> None:
    # await state.set_state(Form.menu)
    tele_id = message.from_user.id
    database.set_state(tele_id, "menu")
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: settings_back: Got language from user")
    except Exception as e:
        logger.error(f"In function: settings_back: {e}")

    markup = await markups.create_menu_markup(lang)
    try:
        await message.answer(
            translation['main menu'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info("In function: change_language_back: sent answer: главное меню")
    except Exception as e:
        logger.error(f"In function: change_language_back: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "menu"), F.text.in_(translation["modes"]))
async def gamemodes(message: Message) -> None:
    database.drop_duplicates()
    # await state.set_state(Form.gamemodes)
    tele_id = message.from_user.id
    database.set_state(tele_id, "gamemodes")
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: gamemodes: Got language from user")
    except Exception as e:
        logger.error(f"In function: gamemodes: {e}")

    markup = await markups.create_gamemodes_markup(lang)
    try:
        await message.answer(
            translation['available modes'][lang_code[lang]],
            reply_markup = markup
        )
        logger.info("In function: gamemodes: sent answer: Доступные режимы")
    except Exception as e:
        logger.error(f"In function: gamemodes: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "gamemodes"), F.text.in_(translation["back"]))
async def gamemodes_back(message: Message) -> None:
    # await state.set_state(Form.menu)
    tele_id = message.from_user.id
    database.set_state(tele_id, "menu")
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: gamemodes_back: Got language from user")
    except Exception as e:
        logger.error(f"In function: gamemodes_back: {e}")

    markup = await markups.create_menu_markup(lang)
    try:
        await message.answer(
            translation['main menu'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info("In function: gamemodes_back: sent answer: Главное меню")
    except Exception as e:
        logger.error(f"In function: gamemodes_back: {e}")
    await message.delete()


@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "gamemodes"), F.text.split()[0].in_(translation["single"]))
async def single_game(message: Message) -> None:
    tele_id = message.from_user.id
    answer = message.text
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game: {e}")
    mode = "msk"
    if (answer == translation["gamemodes"][lang_code[lang]][0]):
        mode = "wrld"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single wrld'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: single_game: sent answer: Одиночный по миру")
        except Exception as e:
            logger.error(f"In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][1]):
        mode = "msk"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single msk'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: single_game: sent answer: Одиночный по москве")
        except Exception as e:
            logger.error(f"In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][2]):
        mode = "spb"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single spb'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: single_game: sent answer: Одиночный по Санкт-Петербургу")
        except Exception as e:
            logger.error(f"In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][3]):
        mode = "rus"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single rus'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: single_game: sent answer: Одиночный по России")
        except Exception as e:
            logger.error(f"In function: single_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][4]):
        mode = "usa"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single usa'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: single_game: sent answer: Одиночный по Беларуси")
        except Exception as e:
            logger.error(f"In function: single_game: {e}")

    database.set_state(tele_id, "single_game_menu")
    database.set_state_data(tele_id, mode)
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['rules']))
async def single_game_menu_rules(message: Message) -> None:
    # mode = await state.get_data()
    tele_id = message.from_user.id
    mode = database.get_state_data(tele_id)
    # mode = mode["gamemodes"]
    
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu_rules: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu_rules: {e}")

    if (mode == "msk"):
        try:
            await message.answer(
                messages.MOSCOW_SINGLE_PLAYER_RULES[lang_code[lang]]
            )
            logger.info("In function: single_game_menu_rules: sent rules moscow")
        except Exception as e:
            logger.error(f"In function: single_game_menu_rules: {e}")

    elif (mode == "spb"):
        try:
            await message.answer(
                messages.SPB_SINGLE_PLAYER_RULES[lang_code[lang]]
            )
            logger.info("In function: single_game_menu_rules: sent rules spb")
        except Exception as e:
            logger.error(f"In function: single_game_menu_rules: {e}")
    elif (mode == "rus"):
        try:
            await message.answer(
                messages.RUSSIA_SINGLE_PLAYER_RULES[lang_code[lang]]
            )
            logger.info("In function: single_game_menu_rules: sent rules russia")
        except Exception as e:
            logger.error(f"In function: single_game_menu_rules: {e}")
    elif (mode == "usa"):
        try:
            await message.answer(
                messages.USA_SINGLE_PLAYER_RULES[lang_code[lang]]
            )
            logger.info("In function: single_game_menu_rules: sent rules USA")
        except Exception as e:
            logger.error(f"In function: single_game_menu_rules: {e}")
    elif (mode == "wrld"):
        try:
            await message.answer(
                messages.WORLD_SINGLE_PLAYER_RULES[lang_code[lang]]
            )
            logger.info("In function: single_game_menu_rules: sent rules world")
        except Exception as e:
            logger.error(f"In function: single_game_menu_rules: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['top players']))
async def single_game_menu_top_10_players(message: Message) -> None:
    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    tele_id = message.from_user.id
    mode = database.get_state_data(tele_id)
    
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu_top_10_players: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu_top_10_players: {e}")

    top_10_text = ''
    try:
        top_10_text = await bot_functions.get_top10_single(mode=mode, lang=lang)
        logger.info("In function: single_game_menu_top_10_players: got top 10 players in single " + mode)
    except Exception as e:
        logger.error(f"In function: single_game_menu_top_10_players: {e}")
    try:
        await message.answer(
            top_10_text
        )
        logger.info("In function: single_game_menu_top_10_players: sent top 10 players in single " + mode)
    except Exception as e:
        logger.error(f"In function: single_game_menu_top_10_players: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['last 5 games']))
async def single_game_menu_last_5_games(message: Message) -> None:
    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    tele_id = message.from_user.id
    mode = database.get_state_data(tele_id)
    
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu_last_5_games: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu_last_5_games: {e}")

    try:
        last_5_games = await bot_functions.get_last5_results_single(message.from_user.id, mode, lang)
        logger.info("In function: single_game_menu_last_5_games: got last 5 games in single " + mode)
    except Exception as e:
        logger.error(f"In function: single_game_menu_last_5_games: {e}")
    try:
        await message.answer(
            last_5_games
        )
        logger.info("In function: single_game_menu_last_5_games: sent last 5 games in single " + mode)
    except Exception as e:
        logger.error(f"In function: single_game_menu_last_5_games: {e}")
    await message.delete()


@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['back']))
async def single_game_menu_back(message: Message) -> None:
    tele_id = message.from_user.id
    mode = database.get_state_data(tele_id)
    
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu_back: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu_back: {e}")

    database.set_state(tele_id, "gamemodes")
    # await state.set_state(Form.gamemodes)

    markup = await markups.create_gamemodes_markup(lang)
    try:
        await message.answer(
            translation['available modes'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info("In function: single_game_menu_back: sent answer: Доступные режимы")
    except Exception as e:
        logger.error(f"In function: single_game_menu_back: {e}")
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text.in_(translation['generate seed']))
async def single_game_menu_generate_seed(message: Message) -> None:
    tele_id = message.from_user.id
    mode = database.get_state_data(tele_id)
    
    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu_generate_seed: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu_generate_seed: {e}")

    seed = generate_seed()
    
    try:
        await message.answer(
            (messages.GENERATE_SEED[lang_code[lang]]).format(mode + "_" + seed),
            parse_mode="Markdown"
        )
        logger.info(f"In function: single_game_menu_generate_seed: sent answer: seed")
    except Exception as e:
        logger.error(f"In function: single_game_menu_generate_seed: {e}")
    
    await message.delete()

@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.func(lambda F: hasattr(F, "web_app_data") and hasattr(F.web_app_data, "data") and F.web_app_data.data))
async def single_game_menu_recieve_answer(message: Message) -> None:
    tele_id = message.from_user.id
    username = message.from_user.username
    logger.info("In function: single_game_menu_recieve_answer: Got answer from " + username)
    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    mode = database.get_state_data(tele_id)

    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu_recieve_answer: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu_recieve_answer: {e}")

    try:
        seed = database.get_seed(tele_id, mode)
        logger.info("In function: single_game_menu_recieve_answer: got seed from db")
    except Exception as e:
        logger.error(f"In function: single_game_menu_recieve_answer: {e}")
    seed = mode + "_" + seed

    cords = message.web_app_data.data

    if (mode == "spb" or mode == "msk"):
        score, metres = await bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
    elif (mode == "rus" or mode == "usa" or mode == "wrld"):
        score, metres = await bot_functions.calculate_score_and_distance_russia(cords=cords)
    elif (mode == "wrld"):
        score, metres = await bot_functions.calculate_score_and_distance_world(cords=cords)
    
    photo_url = await bot_functions.get_url(cords=cords)
    logger.info("In function: single_game_menu_recieve_answer: got photo url")

    try:
        track_changes = database.get_track_changes(tele_id, mode)
        logger.info("In function: single_game_menu_recieve_answer: connected to db and got track changes")
    except Exception as e:
        logger.error(f"In function: single_game_menu_recieve_answer: {e}")
    if (track_changes):
        try:
            database.add_results_single(tele_id, score, mode)
            logger.info("In function: single_game_menu_recieve_answer: added results to single: {}, score = {}, name = {}".format(mode, score, username))
        except Exception as e:
            logger.error(f"In function: single_game_menu_recieve_answer: unable to add results: {e}")
        try:
            database.add_game_single(tele_id, score=score, metres=metres, mode=mode)
            logger.info("In function: single_game_menu_recieve_answer: added game to single: {}, score = {}, metres = {}, name = {}".format(mode, score, metres, username))
        except Exception as e:
            logger.error(f"In function: single_game_menu_recieve_answer: unable to add game: {e}")
        database.end_game(tele_id, mode)
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
    else:
        try:
            markup = await markups.create_single_game_menu_markup(mode, lang, tele_id, seed)
            seed = database.get_multiplayer_seed(tele_id, mode)
            seed = mode + "_" + seed
            logger.info("In function: single_game_menu_recieve_answer: got multuplayer seed")
        except Exception as e:
            logger.error(f"In function: single_game_menu_recieve_answer: {e}")

    try:
        database.set_track_changes(tele_id, mode, True)
        logger.info("In function: single_game_menu_recieve_answer: set track changes to true")
    except Exception as e:
        logger.error(f"In function: single_game_menu_recieve_answer: {e}")
    
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
        logger.info("In function: single_game_menu_recieve_answer: sent photo answer")
    except Exception as e:
        logger.error(f"In function: single_game_menu_recieve_answer: {e}")

    if (database.get_gpt(tele_id)):
        msg = await message.answer(
            translation['wait for gpt'][lang_code[lang]],
        )

        language = ''
        if lang == 'en':
            language = 'english'
        else:
            language = "russian"
        fact = await bot_functions.gpt_request(cords, language)
        await msg.delete()
        await message.answer(
            fact
        )

    await message.delete()


@form_router.message(F.func(lambda F: database.get_state(F.from_user.id)== "single_game_menu"), F.text)
async def single_game_menu_set_seed(message: Message) -> None:

    # mode = await state.get_data()
    # mode = mode["gamemodes"]
    tele_id = message.from_user.id
    mode = database.get_state_data(tele_id)

    try:
        lang = database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu_set_seed: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu_set_seed: {e}")


    string = message.text
    
    if not(check_seed(string, mode)):
        try:
            await message.answer(
                translation["not a seed"][lang_code[lang]]
            )
            logger.info("In function: single_game_menu_set_seed: sent answer: not a seed")
        except Exception as e:
            logger.error(f"In function: single_game_menu_set_seed: {e}")
        
        await message.delete()
        return
    try:
        database.set_track_changes(tele_id, mode, False)
        logger.info("In function: single_game_menu_set_seed: sent answer: set track changes in db")
    except Exception as e:
        logger.info(f"In function: single_game_menu_set_seed: {e}")


    seed = string.split('_')[1]
    markup = await markups.create_single_game_menu_markup(mode, lang, tele_id, seed)
    try:
        database.set_multiplayer_seed(tele_id, seed, mode)
        logger.info("In function: single_game_menu_set_seed: set multiplayer seed")
    except Exception as e:
        logger.error(f"In function: single_game_menu_set_seed: {e}")
        
    await message.answer(
            (translation["set seed"][lang_code[lang]]).format(string),
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    await message.delete()

@form_router.message(F.text)
async def idk_bugs_or_smth(message: Message) -> None:
    is_found = False
    try:
        is_found = database.find_user(message.from_user.id)
        logger.info("In function: idk_bugs_or_smth: successfully connected to db")
    except Exception as e:
        logger.error(f"In function: idk_bugs_or_smth: unable to connect to db: {e}")
    if is_found:
        try:
            lang = database.get_language(message.from_user.id)
            logger.info("In function: idk_bugs_or_smth: Got language from user")
        except Exception as e:
            lang = "en"
            logger.error(f"In function: idk_bugs_or_smth: unable to get lang: {e}")
    else:
        lang = "en"
    try:
        await message.answer(
            translation['error'][lang_code[lang]]
        )
        logger.info("In function: idk_bugs_or_smth: someting broke or bot was restarted")
    except Exception as e:
        logger.error(f"In function: idk_bugs_or_smth: {e}")
    await message.delete()

async def process_event(event, bot: Bot):
    try:
        body = json.loads(event['body'])
        update = Update(**body)
        result = await dp.feed_update(bot=bot, update=update)
        logger.info(f"In function: process_event: handeled event: {body}")
    except Exception as e:
        logger.error(f"In function: process_event: {e}")

async def handler(event, context):
    number = random.randint(1000, 9999)
    logger.info(f"In function: handler: recieved event, code = {number}")
    logger.debug(event)
    bot = Bot(token=TOKEN_BOT)
    await process_event(event, bot)
    return {'statusCode': 200, 'body': 'ok',}

async def main():
    bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # database.delete_database()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
