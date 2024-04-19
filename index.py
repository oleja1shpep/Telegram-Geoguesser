import asyncio
import logging
import sys
import os
import json
import traceback

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, Update

import messages
import database
import markups
import bot_functions

from config import TEST_TOKEN
from translation import t, lang_code

USE_DB = True

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

TOKEN_BOT = os.getenv("TOKEN") or TEST_TOKEN
DB_HOST = os.getenv("DB_HOST") or "localhost"
DB_USER = os.getenv("DB_USER") or "mongo"
DB_PASS = os.getenv("DB_PASS") or "mongomongo"

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
    logger.info("Recieved command /start")
    
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
        logger.info("sent answer: Greeting")
    except Exception as e:
        logger.error(e)
    logger.debug("finished <command_start>")

@form_router.message(Form.start, F.text.in_(t["play"]))
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)

    tele_id = message.from_user.id
    username = message.from_user.username
    try:
        if (USE_DB): is_found = await database.find_user(tele_id)
        logger.info("read info from mongodb")
    except Exception as e:
        logger.error(f"Could not access database: {e}")

    is_found = False
        
    try:
        if USE_DB and not(is_found):
            await database.add_user(tele_id, username)
            logger.info("added user \"" + username + "\" to db")
    except Exception as e:
        logger.error(f"Error in smth: {e}")

    try:
        if USE_DB: await database.set_language(message.from_user.id, 'en')
        logger.info("Set language")
    except Exception as e:
        logger.error(e)

    lang = "en"
    
    try:
        if USE_DB: lang = await database.get_language(message.from_user.id)
        logger.info("got lang")
    except Exception as e:
        logger.error("Process_name: {e}")
    markup = await markups.create_menu_markup(lang)

    try:
        if (is_found):            
            await message.answer(
                t['greeting'][lang_code[lang]],
                reply_markup = markup
            )
        else:
            await message.answer(
                t['registration'][lang_code[lang]],
                reply_markup = markup
            )
        logger.info("sent answer: Registration")
    except Exception as e:
        logger.error(e)
    logger.debug("finished <process_name>")

@form_router.message(Form.menu, F.text.in_(t["how to play"]))
async def main_menu(message: Message, state: FSMContext) -> None:
    
    await database.drop_duplicates()
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("got lang from user")
    except Exception as e:
        logger.error(e)
    try: 
        await message.answer(
            text = messages.HOW_TO_PLAY[lang_code[lang]]
        )
        logger.info("sent answer: general rules")
    except Exception as e:
        logger.error(e)


@form_router.message(Form.menu, F.text.in_(t["language"]))
async def change_language(message: Message, state: FSMContext) -> None:
    await database.drop_duplicates()
    await state.set_state(Form.language_menu)
    lang = await database.get_language(message.from_user.id)
    markup = await markups.create_language_menu_markup(lang)
    try:
        await message.answer(
            t['choose the language'][lang_code[lang]],
            reply_markup = markup
        )
        logger.info("sent answer: Выберите язык")
    except Exception as e:
        logger.error(e)

@form_router.message(Form.language_menu, F.text.in_(t["rus_language"]))
async def change_language_rus(message: Message, state: FSMContext) -> None:
    try:
        await database.set_language(message.from_user.id, 'ru')
        logger.info("set language in db : ru")
    except Exception as e:
        logger.error(e)

    markup = await markups.create_language_menu_markup("ru")
    try:
        await message.answer(
            "Выбран Русский язык",
            reply_markup=markup
        )
        logger.info("sent answer: Выбран русский")
    except Exception as e:
        logger.error(e)

@form_router.message(Form.language_menu, F.text.in_(t["eng_language"]))
async def change_language_eng(message: Message, state: FSMContext) -> None:
    try:
        await database.set_language(message.from_user.id, 'en')
        logger.info("set language in db : en")
    except Exception as e:
        logger.error(e)
    markup = await markups.create_language_menu_markup("en")
    try:
        await message.answer(
            "Set English language",
            reply_markup=markup
        )
        logger.info("sent answer: выбран Английский")
    except Exception as e:
        logger.error(e)

@form_router.message(Form.language_menu, F.text.in_(t["back"]))
async def change_language_back(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("Got language from user")
    except Exception as e:
        logger.error(e)

    markup = await markups.create_menu_markup(lang)
    try:
        await message.answer(
            t['main menu'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info("sent answer: главное меню")
    except Exception as e:
        logger.error(e)

@form_router.message(Form.menu, F.text.in_(t["modes"]))
async def gamemodes(message: Message, state: FSMContext) -> None:
    await database.drop_duplicates()
    await state.set_state(Form.gamemodes)
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("Got language from user")
    except Exception as e:
        logger.error(e)

    markup = await markups.create_gamemodes_markup(lang)
    try:
        await message.answer(
            t['available modes'][lang_code[lang]],
            reply_markup = markup
        )
        logger.info("sent answer: Доступные режимы")
    except Exception as e:
        logger.error(e)

@form_router.message(Form.gamemodes, F.text.in_(t["back"]))
async def gamemodes_back(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("Got language from user")
    except Exception as e:
        logger.error(e)

    markup = await markups.create_menu_markup(lang)
    try:
        await message.answer(
            t['main menu'][lang_code[lang]],
            reply_markup= markup
        )
        logger.info("sent answer: Главное меню")
    except Exception as e:
        logger.error(e)


@form_router.message(Form.gamemodes, F.text.split()[0].in_(t["single"]))
async def signle_game(message: Message, state: FSMContext) -> None:
    answer = message.text
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("Got language from user")
    except Exception as e:
        logger.error(e)
    mode = "Moscow"
    if (answer == t["gamemodes"][lang_code[lang]][0]):
        mode = "Moscow"
        markup = await markups.create_single_game_menu_markup(mode, lang)
        try:
            await message.answer(
                t['single msk'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("sent answer: Одиночный по москве")
        except Exception as e:
            logger.error(e)
    elif (answer == t["gamemodes"][lang_code[lang]][1]):
        mode = "SPB"
        markup = await markups.create_single_game_menu_markup(mode, lang)
        try:
            await message.answer(
                t['single spb'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("sent answer: Одиночный по Санкт-Петербургу")
        except Exception as e:
            logger.error(e)
    elif (answer == t["gamemodes"][lang_code[lang]][2]):
        mode = "Russia"
        markup = await markups.create_single_game_menu_markup(mode, lang)
        try:
            await message.answer(
                t['single rus'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("sent answer: Одиночный по России")
        except Exception as e:
            logger.error(e)
    elif (answer == t["gamemodes"][lang_code[lang]][3]):
        mode = "Belarus"
        markup = await markups.create_single_game_menu_markup(mode, lang)
        try:
            await message.answer(
                t['single bel'][lang_code[lang]],
                reply_markup = markup
            )
            logger.info("sent answer: Одиночный по Беларуси")
        except Exception as e:
            logger.error(e)

    await state.set_state(Form.single_game_menu)
    await state.update_data(gamemodes = mode)
    

@form_router.message(Form.single_game_menu)
async def single_game_menu(message: Message, state: FSMContext) -> None:
    mode = await state.get_data()
    mode = mode["gamemodes"]
    try:
        lang = await database.get_language(message.from_user.id)
        logger.info("Got language from user")
    except Exception as e:
        logger.error(e)

    answer = message.text
    if (answer == t['rules'][lang_code[lang]]):
        if (mode == "Moscow"):
            try:
                await message.answer(
                    messages.MOSCOW_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("sent rules moscow")
            except Exception as e:
                logger.error(e)
        elif (mode == "SPB"):
            try:
                await message.answer(
                    messages.SPB_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("sent rules spb")
            except Exception as e:
                logger.error(e)
        elif (mode == "Russia"):
            try:
                await message.answer(
                    messages.RUSSIA_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("sent rules russia")
            except Exception as e:
                logger.error(e)
        elif (mode == "Belarus"):
            try:
                await message.answer(
                    messages.BELARUS_SINGLE_PLAYER_RULES[lang_code[lang]]
                )
                logger.info("sent rules belarus")
            except Exception as e:
                logger.error(e)

    elif (answer == t['top players'][lang_code[lang]]):
        top_10_text = ''
        try:
            top_10_text = await bot_functions.get_top10_single(mode=mode, lang=lang)
            logger.info("got top 10 players in single " + mode)
        except Exception as e:
            logger.error(e)
        try:
            await message.answer(
                top_10_text
            )
            logger.info("sent top 10 players in single " + mode)
        except Exception as e:
            logger.error(e)
        
    elif (answer == t['last 5 games'][lang_code[lang]]):
        try:
            last_5_games = await bot_functions.get_last5_results_single(message.from_user.id, mode, lang)
            logger.info("got last 5 games in single " + mode)
        except Exception as e:
            logger.error(e)
        try:
            await message.answer(
                last_5_games
            )
            logger.info("sent top 10 players in single " + mode)
        except Exception as e:
            logger.error(e)
    elif (answer == t['back'][lang_code[lang]]):
        await state.set_state(Form.gamemodes)
        markup = await markups.create_gamemodes_markup(lang)
        try:
            await message.answer(
                t['available modes'][lang_code[lang]],
                reply_markup= markup
            )
            logger.info("sent answer: Доступные режимы")
        except Exception as e:
            logger.error(e)
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                logger.info("Got answer from " + message.from_user.username)
                #print("ответ получен", message.from_user.id, message.from_user.username)
                cords = message.web_app_data.data
                if (mode == "SPB" or mode == "Moscow"):
                    score, metres = await bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
                elif (mode == "Russia" or mode == "Belarus"):
                    score, metres = await bot_functions.calculate_score_and_distance_russia(cords=cords)

                photo_url = await bot_functions.get_url(cords=cords)
                logger.info("got photo url")

                # print(score, metres, message.from_user.username)
                try:
                    await database.add_results_single(message.from_user.id, score, mode)
                    logger.info("added results to single: {}, score = {}, name = {}".format(mode, score, message.from_user.username))
                except Exception as e:
                    logger.error(e)
                try:
                    await database.add_game_single(tele_id=message.from_user.id, score=score, metres=metres, mode=mode)
                    logger.info("added game to single: {}, score = {}, metres = {}, name = {}".format(mode, score, metres, message.from_user.username))
                except Exception as e:
                    logger.error(e)


                txt = await bot_functions.create_result_text(score=score, metres=metres,lang = lang)
                try:
                    await message.answer_photo(photo_url, caption=txt)
                    logger.info("sent photo answer")
                except Exception as e:
                    logger.error(e)
                # send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {
                #                         metres} метров", reply_markup=markup)

@form_router.message(F.text)
async def idk_bugs_or_smth(message: Message, state: FSMContext) -> None:
    is_found = False
    try:
        is_found = await database.find_user(message.from_user.id)
        logger.info("successfully connected to db")
    except Exception as e:
        logger.error(f"In function: idk_bugs_or_smth:{e}")
    if is_found:
        try:
            lang = await database.get_language(message.from_user.id)
            logger.info("Got language from user")
        except Exception as e:
            lang = "en"
            logger.error(e)
    else:
        lang = "en"
    try:
        await message.answer(
            t['error'][lang_code[lang]]
        )
        logger.info("someting broke or bot was restarted")
    except Exception as e:
        logger.error(e)

async def process_event(event, bot: Bot):
    try:
        body = json.loads(event['body'])
        update = Update(**body)
        result = await dp.feed_update(bot=bot, update=update)
        logger.info(f"handeled event: {body}")
    except Exception as e:
        logger.error(e)

async def handler(event, context):
    #raise Exception({'event':event,'conext':context})
    # print(event['body'])
    logger.info("recieved event") 
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
