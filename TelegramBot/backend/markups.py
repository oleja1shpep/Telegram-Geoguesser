import os
import logging
import json

from datetime import date, timedelta
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from backend.database import MongoDB
from backend.seed_processor import coordinates_from_seed, coordinates_and_landmark_from_seed_easy_mode, MODE_TO_RADIUS
from dotenv import load_dotenv

database = MongoDB()

DEFAULT_AVAILIBLE_GAMES = 20

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

load_dotenv()

URL_SITE = os.getenv("URL_SITE")

with open("./backend/text/translations.json", 'r', encoding='utf-8') as file:
    file = json.load(file)
translation = file['translations']
lang_code = file['lang_code']

async def create_start_markup(lang = 'en'):
    builder = ReplyKeyboardBuilder()
    builder.button(text=translation["play"][lang_code[lang]])
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

async def create_menu_markup(lang = "en"):
    builder = ReplyKeyboardBuilder()
    builder.button(text=translation["modes"][lang_code[lang]])
    builder.button(text=translation["how to play"][lang_code[lang]])
    builder.button(text=translation["settings"][lang_code[lang]])
    builder.button(text=translation["credits"][lang_code[lang]])
    builder.adjust(1,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

async def create_settings_menu_markup(lang, use_gpt):
    text_en = (lang == "en") * "✅" + translation["eng_language"][lang_code[lang]]
    text_ru = (lang == "ru") * "✅" + translation["rus_language"][lang_code[lang]]
    text_use_gpt = use_gpt * "✅" + (1 - use_gpt) * "🚫" + translation["use_gpt"][lang_code[lang]]
    builder = ReplyKeyboardBuilder()
    builder.button(text=text_ru)
    builder.button(text=text_en)
    builder.button(text=text_use_gpt)
    builder.button(text=translation["back"][lang_code[lang]])
    builder.adjust(2,1,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

async def create_gamemodes_markup(lang = "en"):
    builder = ReplyKeyboardBuilder()
    keyboard = translation['gamemodes'][lang_code[lang]]
    for i in range(len(keyboard)):
        builder.button(text = keyboard[i])
    builder.adjust(1,2,2,2)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

async def create_single_game_menu_markup(mode, lang, tele_id, seed = ''):
    builder = ReplyKeyboardBuilder()
    keyboard = translation["single game modes"][lang_code[lang]]

    if not(seed):
        try:
            database.init_game(tele_id, mode)
            logger.info("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.init_game\"}")
        except Exception as e:
            logger.error("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.init_game\", \"Error\" : \"" + f"{e}" + "\"}")
        try:
            seed = database.get_key(tele_id, "seed_" + mode, "")
            logger.info("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.get_seed\"}")
        except Exception as e:
            logger.error("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.get_seed\", \"Error\" : \"" + f"{e}" + "\"}")
    logger.debug("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Info\" : {" + f"\"seed\" : \"{seed}\", \"mode\" : \"{mode}\"" + "}}")
    # new seed generation
    if mode == 'easy':
        x, y, landmark = coordinates_and_landmark_from_seed_easy_mode(seed)
        coords = [x, y, 0, 0, 1]
    else:
        coords = coordinates_from_seed(seed, mode)
    allowed_to_play = False
    
    prev_date = date.fromisoformat(database.get_key(tele_id, "time_of_prev_request", (date.today()).strftime('%Y-%m-%d')))
    difference = (date.today() - prev_date).days

    logger.debug("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"Difference in date\", \"Info\" : {" + f"\"today\" : {date.today()}, \"prev_date\" : {prev_date}" + "}}")
    game_count = database.get_key(tele_id, "game_counter", 0)
    logger.debug("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"Game_count\", \"Info\" : " + f"{game_count}" + "}")
    if difference >= 1:
        try:
            database.set_key(tele_id, "time_of_prev_request", (date.today()).strftime("%Y-%m-%d"))
            logger.info("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.set_time_of_prev_request\"}")
        except Exception as e:
            logger.error("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.set_time_of_prev_request\", \"Error\" : \"" + f"{e}" + "\"}")
        try:
            database.set_key(tele_id, "game_counter", 0)
            logger.info("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.set_game_counter = 0\"}")
        except Exception as e:
            logger.error("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"database.set_game_counter\", \"Error\" : \"" + f"{e}" + "\"}")
        
        allowed_to_play = True
    else:
        current_game_count = database.get_key(tele_id, "game_counter", 0)
        availible_games_count = database.get_key(tele_id, "availible_games", DEFAULT_AVAILIBLE_GAMES)
        logger.debug("{\"File\" : \"markups.py\", \"Function\" : \"create_single_game_menu_markup\", \"Action\" : \"Compare\", \"Info\" : {" + f"\"current_game_count\" : {current_game_count}, \"availible_games_count\" : {availible_games_count}" + "}}")

        if (current_game_count < availible_games_count):
            allowed_to_play = True
            
    if allowed_to_play:
        builder.button(text = keyboard[0], web_app= WebAppInfo(url=URL_SITE + "#" + mode + '&' + '&'.join(map(str, coords)) + '&' + str(MODE_TO_RADIUS[mode])))
    else:
        builder.button(text = keyboard[0])

    for i in range(1,len(keyboard)):
        builder.button(text = keyboard[i])

    builder.adjust(2,2,2)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
