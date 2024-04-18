from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import URL_SITE
from translation import t, lang_code

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
                KeyboardButton(text=t["modes"][lang_code[lang]]),
                KeyboardButton(text=t["how to play"][lang_code[lang]]),
                KeyboardButton(text=t["language"][lang_code[lang]]),
            ]
        ],
        resize_keyboard=True,
    )

async def create_language_menu_markup(lang = "en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t["rus_language"][lang_code[lang]]),
                KeyboardButton(text=t["eng_language"][lang_code[lang]]),
                KeyboardButton(text=t["back"][lang_code[lang]]),
            ]
        ],
        resize_keyboard=True,
    )

async def create_gamemodes_markup(lang = "en"):
    builder = ReplyKeyboardBuilder()
    keyboard = t['gamemodes'][lang_code[lang]]
    for i in range(5):
        builder.button(text = keyboard[i])
    builder.adjust(2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

async def create_single_game_menu_markup(mode, lang = 'en'):
    builder = ReplyKeyboardBuilder()
    keyboard = t["single game modes"][lang_code[lang]]
    builder.button(text = keyboard[0], web_app= WebAppInfo(url=URL_SITE + "#" + mode))
    for i in range(1,5):
        builder.button(text = keyboard[i])

    builder.adjust(2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
