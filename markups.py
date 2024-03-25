from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from config import URL_SITE

async def create_start_markup():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Играть")),
            ]
        ],
        resize_keyboard=True,
    )

async def create_menu_markup():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Режимы")),
                KeyboardButton(text=_("Как играть")),
                KeyboardButton(text=_("Язык")),
            ]
        ],
        resize_keyboard=True,
    )

async def create_language_menu_markup():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Русский")),
                KeyboardButton(text=_("Английский")),
                KeyboardButton(text=_("Назад")),
            ]
        ],
        resize_keyboard=True,
    )

async def create_gamemodes_markup():
    builder = ReplyKeyboardBuilder()
    keyboard = [
        _("Одиночный | Москва"),
        _("Одиночный | Санкт-Петербург"),
        _("Одиночный | Россия"),
        _("Одиночный | Беларусь"),
        _("Назад"),
    ]
    for i in range(5):
        builder.button(text = keyboard[i])
    builder.adjust(2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup

async def create_single_game_menu_markup(mode):
    builder = ReplyKeyboardBuilder()
    keyboard = [
        _("Начать игру"),
        _("Правила"),
        _("Топ игроков"),
        _("Прошлые 5 игр"),
        _("Назад"),
    ]
    builder.button(text = keyboard[0], web_app= WebAppInfo(url=URL_SITE + "#" + mode))
    for i in range(1,5):
        builder.button(text = keyboard[i])

    builder.adjust(2,2,1)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    return markup
