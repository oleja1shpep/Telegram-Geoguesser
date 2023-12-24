from telebot import types
from config import URL_MOSCOW, URL_SPB, URL_RUSSIA

def create_start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item_1 = types.KeyboardButton("Играть")
    markup.add(item_1)
    return markup

def create_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton("Режимы")
    item_2 = types.KeyboardButton("Как играть 🤔")
    markup.add(item_1, item_2)
    return markup

def create_gamemodes_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    item_1 = types.KeyboardButton("Одиночный | Москва")
    item_2 = types.KeyboardButton("Одиночный | Санкт-Петербург")
    item_3 = types.KeyboardButton("Одиночный | Россия")
    item_4 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3, item_4)
    return markup

def create_moscow_single_game_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.InlineKeyboardButton(text="Начать игру", web_app = types.WebAppInfo(url=URL_MOSCOW))
    item_2 = types.KeyboardButton("Правила 🤓")
    item_3 = types.KeyboardButton("Топ игроков")
    item_4 = types.KeyboardButton("Прошлые 5 игр")
    item_5 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3, item_4, item_5)
    return markup

def create_russia_single_game_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton(text="Начать игру", web_app = types.WebAppInfo(url=URL_RUSSIA))
    item_2 = types.KeyboardButton("Правила 🤓")
    item_3 = types.KeyboardButton("Топ игроков")
    item_4 = types.KeyboardButton("Прошлые 5 игр")
    item_5 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3, item_4, item_5)
    return markup

def create_spb_single_game_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton(text="Начать игру", web_app = types.WebAppInfo(url=URL_SPB))
    item_2 = types.KeyboardButton("Правила 🤓")
    item_3 = types.KeyboardButton("Топ игроков")
    item_4 = types.KeyboardButton("Прошлые 5 игр")
    item_5 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3, item_4, item_5)
    return markup