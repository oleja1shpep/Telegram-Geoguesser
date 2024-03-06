from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import URL_SITE

def create_start_markup():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Играть"),
            ]
        ],
        resize_keyboard=True,
    )

def create_menu_markup():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Режимы"),
                KeyboardButton(text="Как играть 🤔"),
            ]
        ],
        resize_keyboard=True,
    )

def create_gamemodes_markup():
    builder = ReplyKeyboardBuilder()
    keyboard = [
        "Одиночный | Москва",
        "Одиночный | Санкт-Петербург",
        "Одиночный | Россия",
        "Одиночный | Беларусь",
        "Назад",
    ]
    for i in range(5):
        builder.button(text = keyboard[i])
    builder.adjust(2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

def create_single_game_menu_markup(mode):
    builder = ReplyKeyboardBuilder()
    keyboard = [
        "Начать игру",
        "Правила 🤓",
        "Топ игроков",
        "Прошлые 5 игр",
        "Назад",
    ]
    builder.button(text = keyboard[0], web_app= WebAppInfo(url=URL_SITE + "#" + mode))
    for i in range(1,5):
        builder.button(text = keyboard[i])

    builder.adjust(2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
