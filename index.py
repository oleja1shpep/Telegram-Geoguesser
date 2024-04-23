import asyncio
import logging
import sys
import os
import json
import requests

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, Update
from dotenv import load_dotenv

import messages
import database
import markups
import bot_functions

USE_DB = True
DEBUG_MODE = False

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

load_dotenv()

TOKEN_BOT = os.getenv("TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

with open('translations.json', 'r', encoding='utf-8') as file:
    file = json.load(file)
translation = file['translations']
lang_code = file['lang_code']

form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)

class Form(StatesGroup):
    start = State()
    menu = State()
    language_menu = State()
    gamemodes = State()
    single_game_menu = State()

@form_router.message(CommandStart(), F.chat.type == "private")
async def command_start(message: Message, state: FSMContext) -> None:
    logger.info("In function: command_start: Recieved command /start")
    
    # try:
    #     if (USE_DB): await database.delete_database()
    #     logger.info("deleted db")
    # except Exception as e:
    #     logger.error(f"Error in command_start: {e}")

    await state.set_state(Form.start)
    try:
        await message.answer(
            ('Hello, {}!{}').format(message.from_user.first_name, messages.GREETING[1]),
            reply_markup=await markups.create_start_markup()
        )
        logger.info("In function: command_start: sent answer: Greeting")
    except Exception as e:
        logger.error(e)
    logger.info("In function: command_start: finished <command_start>")
    await message.delete()

@form_router.message(Form.start, F.text.in_(translation['play']))
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)

    tele_id = message.from_user.id
    username = message.from_user.username
    is_found = False
    try:
        if (USE_DB): is_found = await database.find_user(tele_id)
        logger.info("In function: process_name: read info from mongodb")
    except Exception as e:
        logger.error(f"In function: process_name: Could not access database: {e}")


    try:
        if USE_DB and not(is_found):
            await database.add_user(tele_id, username)
            logger.info("In function: process_name: added user \"" + username + "\" to db")
    except Exception as e:
        logger.error(f"In function: process_name: could not add user: {e}")

    try:
        if USE_DB: await database.set_language(message.from_user.id, 'en')
        logger.info("In function: process_name: Set language")
    except Exception as e:
        logger.error(f"In function: process_name: {e}")

    lang = "en"
    
    try:
        if USE_DB: lang = await database.get_language(message.from_user.id)
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

@form_router.message(Form.menu, F.text.in_(translation["how to play"]))
async def main_menu(message: Message, state: FSMContext) -> None:
    
    await database.drop_duplicates()
    try:
        lang = await database.get_language(message.from_user.id)
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


@form_router.message(Form.menu, F.text.in_(translation["settings"]))
async def settings_menu(message: Message, state: FSMContext) -> None:
    await database.drop_duplicates()
    if DEBUG_MODE:
        await database.show_database()
    await state.set_state(Form.language_menu)
    lang = await database.get_language(message.from_user.id)
    markup = await markups.create_settings_menu_markup(lang)
    try:
        await message.answer(
            translation['settings menu'][lang_code[lang]],
            reply_markup = markup
        )
        logger.info("In function: settings_menu: sent answer: Настройки")
    except Exception as e:
        logger.error(f"In function: settings_menu: {e}")
    await message.delete()

@form_router.message(Form.language_menu, F.text.in_(translation["rus_language"]))
async def change_language_rus(message: Message, state: FSMContext) -> None:
    try:
        await database.set_language(message.from_user.id, 'ru')
        logger.info("In function: change_language_rus: set language in db : ru")
    except Exception as e:
        logger.error(f"In function: change_language_rus: {e}")

    markup = await markups.create_settings_menu_markup("ru")
    try:
        await message.answer(
            "Выбран Русский язык",
            reply_markup=markup
        )
        logger.info("In function: change_language_rus: sent answer: Выбран русский")
    except Exception as e:
        logger.error(f"In function: change_language_rus: {e}")
    await message.delete()

@form_router.message(Form.language_menu, F.text.in_(translation["eng_language"]))
async def change_language_eng(message: Message, state: FSMContext) -> None:
    try:
        await database.set_language(message.from_user.id, 'en')
        logger.info("In function: change_language_eng: set language in db : en")
    except Exception as e:
        logger.error(f"In function: change_language_eng: {e}")
    markup = await markups.create_settings_menu_markup("en")
    try:
        await message.answer(
            "Set English language",
            reply_markup=markup
        )
        logger.info("In function: change_language_eng: sent answer: выбран Английский")
    except Exception as e:
        logger.error(f"In function: change_language_eng: {e}")
    await message.delete()

@form_router.message(Form.language_menu, F.text.in_(translation["use_gpt"]))
async def switch_use_gpt(message: Message, state: FSMContext) -> None:
    try:
        await database.switch_gpt(message.from_user.id)
        logger.info("In function: switch_use_gpt: switched gpt use")
    except Exception as e:
        logger.error(f"In function: switch_use_gpt: {e}")

    use_gpt = await database.get_gpt(message.from_user.id)
    lang = await database.get_language(message.from_user.id)
    try:
        if (use_gpt):
            await message.answer(
                translation['using gpt'][lang_code[lang]],
            )
        else:
            await message.answer(
                translation['not using gpt'][lang_code[lang]],
            )
        logger.info("In function: switch_use_gpt: sent answer: usage gpt")
    except Exception as e:
        logger.error(f"In function: switch_use_gpt: {e}")
    await message.delete()

@form_router.message(Form.language_menu, F.text.in_(translation["back"]))
async def settings_back(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    try:
        lang = await database.get_language(message.from_user.id)
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

@form_router.message(Form.menu, F.text.in_(translation["modes"]))
async def gamemodes(message: Message, state: FSMContext) -> None:
    await database.drop_duplicates()
    await state.set_state(Form.gamemodes)
    try:
        lang = await database.get_language(message.from_user.id)
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

@form_router.message(Form.gamemodes, F.text.in_(translation["back"]))
async def gamemodes_back(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    try:
        lang = await database.get_language(message.from_user.id)
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


@form_router.message(Form.gamemodes, F.text.split()[0].in_(translation["single"]))
async def signle_game(message: Message, state: FSMContext) -> None:
    tele_id = message.from_user.id
    answer = message.text
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("In function: signle_game: Got language from user")
    except Exception as e:
        logger.error(f"In function: signle_game: {e}")
    mode = "msk"
    if (answer == translation["gamemodes"][lang_code[lang]][0]):
        mode = "wrld"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single wrld'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: signle_game: sent answer: Одиночный по миру")
        except Exception as e:
            logger.error(f"In function: signle_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][1]):
        mode = "msk"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single msk'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: signle_game: sent answer: Одиночный по москве")
        except Exception as e:
            logger.error(f"In function: signle_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][2]):
        mode = "spb"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single spb'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: signle_game: sent answer: Одиночный по Санкт-Петербургу")
        except Exception as e:
            logger.error(f"In function: signle_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][3]):
        mode = "rus"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single rus'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: signle_game: sent answer: Одиночный по России")
        except Exception as e:
            logger.error(f"In function: signle_game: {e}")
    elif (answer == translation["gamemodes"][lang_code[lang]][4]):
        mode = "blrs"
        markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
        try:
            await message.answer(
                translation['single bel'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("In function: signle_game: sent answer: Одиночный по Беларуси")
        except Exception as e:
            logger.error(f"In function: signle_game: {e}")

    await state.set_state(Form.single_game_menu)
    await state.update_data(gamemodes = mode)
    await message.delete()
    

@form_router.message(Form.single_game_menu)
async def single_game_menu(message: Message, state: FSMContext) -> None:
    mode = await state.get_data()
    mode = mode["gamemodes"]
    
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("In function: single_game_menu: Got language from user")
    except Exception as e:
        logger.error(f"In function: single_game_menu: {e}")

    answer = message.text
    if (answer == translation['rules'][lang_code[lang]]):
        if (mode == "msk"):
            try:
                await message.answer(
                    messages.MOSCOW_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("In function: single_game_menu: sent rules moscow")
            except Exception as e:
                logger.error(f"In function: single_game_menu: {e}")
        elif (mode == "spb"):
            try:
                await message.answer(
                    messages.SPB_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("In function: single_game_menu: sent rules spb")
            except Exception as e:
                logger.error(f"In function: single_game_menu: {e}")
        elif (mode == "rus"):
            try:
                await message.answer(
                    messages.RUSSIA_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("In function: single_game_menu: sent rules russia")
            except Exception as e:
                logger.error(f"In function: single_game_menu: {e}")
        elif (mode == "blrs"):
            try:
                await message.answer(
                    messages.BELARUS_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("In function: single_game_menu: sent rules belarus")
            except Exception as e:
                logger.error(f"In function: single_game_menu: {e}")
        elif (mode == "wrld"):
            try:
                await message.answer(
                    messages.WORLD_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("In function: single_game_menu: sent rules world")
            except Exception as e:
                logger.error(f"In function: single_game_menu: {e}")

    elif (answer == translation['top players'][lang_code[lang]]):
        top_10_text = ''
        try:
            top_10_text = await bot_functions.get_top10_single(mode=mode, lang=lang)
            logger.info("In function: single_game_menu: got top 10 players in single " + mode)
        except Exception as e:
            logger.error(f"In function: single_game_menu: {e}")
        try:
            await message.answer(
                top_10_text
            )
            logger.info("In function: single_game_menu: sent top 10 players in single " + mode)
        except Exception as e:
            logger.error(f"In function: single_game_menu: {e}")
        
    elif (answer == translation['last 5 games'][lang_code[lang]]):
        try:
            last_5_games = await bot_functions.get_last5_results_single(message.from_user.id, mode, lang)
            logger.info("In function: single_game_menu: got last 5 games in single " + mode)
        except Exception as e:
            logger.error(f"In function: single_game_menu: {e}")
        try:
            await message.answer(
                last_5_games
            )
            logger.info("In function: single_game_menu: sent last 5 games in single " + mode)
        except Exception as e:
            logger.error(f"In function: single_game_menu: {e}")
    elif (answer == translation['back'][lang_code[lang]]):
        await state.set_state(Form.gamemodes)
        markup = await markups.create_gamemodes_markup(lang)
        try:
            await message.answer(
                translation['available modes'][lang_code[lang]],
                reply_markup= markup
            )
            logger.info("In function: single_game_menu: sent answer: Доступные режимы")
        except Exception as e:
            logger.error(f"In function: single_game_menu: {e}")
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                tele_id = message.from_user.id
                username = message.from_user.username

                logger.info("In function: single_game_menu: Got answer from " + username)
                #print("ответ получен", message.from_user.id, message.from_user.username)
                cords = message.web_app_data.data

                if (mode == "spb" or mode == "msk"):
                    score, metres = await bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
                elif (mode == "rus" or mode == "blrs" or mode == "wrld"):
                    score, metres = await bot_functions.calculate_score_and_distance_russia(cords=cords)
                
                photo_url = await bot_functions.get_url(cords=cords)
                logger.info("In function: single_game_menu: got photo url")

                # print(score, metres, message.from_user.username)
                try:
                    await database.add_results_single(tele_id, score, mode)
                    logger.info("In function: single_game_menu: added results to single: {}, score = {}, name = {}".format(mode, score, username))
                except Exception as e:
                    logger.error(f"In function: single_game_menu: unable to add results: {e}")
                try:
                    await database.add_game_single(tele_id, score=score, metres=metres, mode=mode)
                    logger.info("In function: single_game_menu: added game to single: {}, score = {}, metres = {}, name = {}".format(mode, score, metres, username))
                except Exception as e:
                    logger.error(f"In function: single_game_menu: unable to add game: {e}")

                await database.end_game(tele_id, mode)
                markup = await markups.create_single_game_menu_markup(mode, lang, tele_id)
    
                txt = await bot_functions.create_result_text(score=score, metres=metres, lang = lang)

                try:
                    await message.answer_photo(photo_url, caption=txt,reply_markup=markup)
                    logger.info("In function: single_game_menu: sent photo answer")
                except Exception as e:
                    logger.error(f"In function: single_game_menu: {e}")

                if (await database.get_gpt(tele_id)):
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

@form_router.message(F.text)
async def idk_bugs_or_smth(message: Message, state: FSMContext) -> None:
    is_found = False
    try:
        is_found = await database.find_user(message.from_user.id)
        logger.info("In function: idk_bugs_or_smth: successfully connected to db")
    except Exception as e:
        logger.error(f"In function: idk_bugs_or_smth: unable to connect to db: {e}")
    if is_found:
        try:
            lang = await database.get_language(message.from_user.id)
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
    #raise Exception({'event':event,'conext':context})
    # print(event['body'])
    logger.info("In function: handler: recieved event") 
    bot = Bot(token=TOKEN_BOT)
    await process_event(event, bot)
    # await dp.start_polling(bot)
    return {'statusCode': 200, 'body': 'ok',}

async def main():
    bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
