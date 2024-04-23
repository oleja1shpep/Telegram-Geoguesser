import os
import logging
import json

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import database
from coords_generator import generate_seed, coordinates_from_seed, MODE_TO_RADIUS
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('GEOGESSER')
logger.setLevel(logging.DEBUG)

load_dotenv()

URL_SITE = os.getenv("URL_SITE")

with open('translations.json', 'r', encoding='utf-8') as file:
    file = json.load(file)
translation = file['translations']
lang_code = file['lang_code']

async def create_start_markup():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Play"),
            ]
        ],
        resize_keyboard=True,
    )

async def create_menu_markup(lang = "en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=translation["modes"][lang_code[lang]]),
                KeyboardButton(text=translation["how to play"][lang_code[lang]]),
                KeyboardButton(text=translation["settings"][lang_code[lang]]),
            ]
        ],
        resize_keyboard=True,
    )

async def create_settings_menu_markup(lang, use_gpt):
    text_en = (lang == "en") * "✅" + translation["eng_language"][lang_code[lang]]
    text_ru = (lang == "ru") * "✅" + translation["rus_language"][lang_code[lang]]
    text_use_gpt = use_gpt * "✅" + (1 - use_gpt) * "🚫" + translation["use_gpt"][lang_code[lang]]
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=text_ru),
                KeyboardButton(text=text_en),
                KeyboardButton(text=text_use_gpt),
                KeyboardButton(text=translation["back"][lang_code[lang]]),
            ]
        ],
        resize_keyboard=True,
    )

async def create_gamemodes_markup(lang = "en"):
    builder = ReplyKeyboardBuilder()
    keyboard = translation['gamemodes'][lang_code[lang]]
    for i in range(6):
        builder.button(text = keyboard[i])
    builder.adjust(1,2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

async def create_single_game_menu_markup(mode, lang, tele_id):
    builder = ReplyKeyboardBuilder()
    keyboard = translation["single game modes"][lang_code[lang]]

    await database.init_game(tele_id, mode)
    seed = await database.get_seed(tele_id, mode)
    logger.debug(f" seed: {seed} | mode: {mode}")
    # new seed generation
    coords = coordinates_from_seed(seed, mode)
    builder.button(text = keyboard[0], web_app= WebAppInfo(url=URL_SITE + "#" + mode + '|' + '|'.join(map(str, coords)) + '|' + str(MODE_TO_RADIUS[mode])))
    for i in range(1,5):
        builder.button(text = keyboard[i])

    builder.adjust(2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
