from telebot import types
from config import URL

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
    item_2 = types.KeyboardButton("Одиночный | Мир")
    item_3 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3)
    return markup

def create_moscow_single_game_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.InlineKeyboardButton(text="Начать игру", web_app = types.WebAppInfo(url=URL))
    item_2 = types.KeyboardButton("Правила 🤓")
    item_3 = types.KeyboardButton("Топ игроков")
    item_4 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3, item_4)
    return markup

def create_world_single_game_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton(text="Начать игру")
    item_2 = types.KeyboardButton("Правила 🤓")
    item_3 = types.KeyboardButton("Топ игроков")
    item_4 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3, item_4)
    return markup