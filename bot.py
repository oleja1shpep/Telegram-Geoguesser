import telebot
from telebot import types
import database
from config import TOKEN
from math import cos, sin, asin, sqrt, radians, log

bot = telebot.TeleBot(TOKEN)

URL = "https://oleja1shpep.github.io/Telegram-Geoguesser/"

def calculate_score_and_distance(cords):
    cords = list(map(float, cords.split()))
    lon1 = cords[1]
    lat1 = cords[0]

    lon2 = cords[4]
    lat2 = cords[3]

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    metres = 6371 * c * 1000
    score = max(min(-log(metres / 70, 1.0014) + 5000, 5000) ,0)
    return [int(score), int(metres)]

def create_start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item_1 = types.KeyboardButton("Играть")
    markup.add(item_1)
    return markup

def create_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton("Одиночный режим")
    item_2 = types.KeyboardButton("Топ игроков")
    markup.add(item_1, item_2)
    return markup

def create_standard_single_game_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton(text="Начать игру")
    item_2 = types.KeyboardButton("Правила 🤓")
    item_3 = types.KeyboardButton("Назад")
    markup.add(item_1, item_2, item_3)
    return markup

def create_launch_standard_single_game_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton("Запуск!", web_app = types.WebAppInfo(url=URL))
    markup.add(item_1)
    return markup

def get_top10():
    top_10_users = database.get_top10()
    txt = ''
    for i in range(len(top_10_users)):
        mean = 0 if top_10_users[i][2] == 0 else top_10_users[i][1] / top_10_users[i][2]
        txt += f'{i+1}. {top_10_users[i][0]} - очков : {top_10_users[i][1]} | матчей : {top_10_users[i][2]} | среднее : {round(mean,2)}\n'
    print(top_10_users)
    return txt

@bot.message_handler(commands=['start', 'reset'])
def hello_message(message):
    markup = create_start_markup()

    send = bot.send_message(message.chat.id,f'Привет, {message.from_user.username}, я геогесср бот',reply_markup=markup)
    bot.register_next_step_handler(send, start_game)

def start_game(message):
    answer = message.text
    tele_id = message.from_user.id
    tele_username = message.from_user.username

    if answer == 'Играть' or answer in ['Меню', 'меню']:
        markup = create_menu_markup()

        if (database.search_tele_id(tele_id=tele_id, tele_username=tele_username)):
            send = bot.send_message(message.chat.id,"Рад увидеть тебя снова в игре!",reply_markup=markup)
        else:
            send = bot.send_message(message.chat.id,"Вы были успешно зарегистрированы",reply_markup=markup)
        
        bot.register_next_step_handler(send, menu)
        
    else:
        markup = create_start_markup()
        if answer in ['/start', '/reset']:
            send = bot.send_message(message.chat.id, f'Привет, {message.from_user.username}, я геогесср бот', reply_markup=markup)
        else:
            send = bot.send_message(message.chat.id,"Выбери что-то из списка",reply_markup=markup)
        bot.register_next_step_handler(send, start_game)

def menu(message):
    answer = message.text
    if answer == "Топ игроков":
        print(f"топ, {message.from_user.id}, {message.from_user.username}")
        top_10_text = get_top10()
        send = bot.send_message(message.chat.id, top_10_text)
        bot.register_next_step_handler(send, menu)

    elif answer == "Одиночный режим":
        markup = create_standard_single_game_menu_markup()
        print(f"одиночный, {message.from_user.id}, {message.from_user.username}")
        send = bot.send_message(message.chat.id, "Одиночный стандартный режим", reply_markup=markup)
        bot.register_next_step_handler(send, standard_single_game_menu)

    elif answer in ['/start', '/reset']:
        markup = create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.username}, я геогесср бот',reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    else:
        markup = create_menu_markup()
        send = bot.send_message(message.chat.id,"Выбери что-то из списка", reply_markup=markup)
        bot.register_next_step_handler(send, menu)

def standard_single_game_menu(message):
    answer = message.text
    if answer == "Назад":
        markup = create_menu_markup()
        send = bot.send_message(message.chat.id,"Главное меню", reply_markup=markup)
        bot.register_next_step_handler(send, menu)
    elif answer == "Правила 🤓":
        print(answer, message.from_user.id, message.from_user.username)
        markup = create_standard_single_game_menu_markup()
        send = bot.send_message(message.chat.id,"Дается неограниченное количество времени на ответ\nМожно перемещаться по улицам в любых направлениях", reply_markup=markup)
        bot.register_next_step_handler(send, standard_single_game_menu)
    elif answer == "Начать игру":
        print(answer, message.from_user.id, message.from_user.username)
        markup = create_launch_standard_single_game_markup()
        send = bot.send_message(message.chat.id, "Чтобы начать нажмите на кнопку", reply_markup=markup)
    else:
        print(answer, message.from_user.id, message.from_user.username)
        markup = create_standard_single_game_menu_markup()
        send = bot.send_message(message.chat.id,"Выбери что-то из списка", reply_markup=markup)
        bot.register_next_step_handler(send, standard_single_game_menu)

@bot.message_handler(content_types=['web_app_data'])
def web_app_recieve(message):
    cords = message.web_app_data.data
    score, metres = calculate_score_and_distance(cords=cords)

    print(score, metres, message.from_user.username)
    database.add_results(message.from_user.id, score)

    markup = create_standard_single_game_menu_markup()
    send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {metres} метров", reply_markup=markup)
    bot.register_next_step_handler(send, standard_single_game_menu)

@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=="Тык" or  message.text=="тык":
        bot.send_message(message.chat.id,"Зачем тыкнул??")
    elif (message.text).lower() == "amogus" or (message.text).lower() == "amongus":
        bot.send_message(message.chat.id,"when the imposter is sus")
    else:
        bot.send_message(message.chat.id, "Чтобы перезапустить отправьте /reset")
            

@bot.message_handler(content_types='dice')
def dice_reply(message):
    bot.send_message(message.chat.id, f'Выпадет число {message.dice.value}')

bot.polling(none_stop=True, interval=0)