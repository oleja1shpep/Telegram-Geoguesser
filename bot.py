import telebot
import database
from config import TOKEN_BOT
import bot_functions
from time import sleep
import markups
import messages
import datetime

bot = telebot.TeleBot(TOKEN_BOT)

@bot.message_handler(commands=['start', 'reset'], chat_types=['private'])
def hello_message(message):
    markup = markups.create_start_markup()

    send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
    bot.register_next_step_handler(send, start_game)

def start_game(message):
    answer = message.text
    tele_id = message.from_user.id
    tele_username = message.from_user.username

    if answer == 'Играть':
        markup = markups.create_menu_markup()

        if (database.search_tele_id(tele_id=tele_id, tele_username=tele_username)):
            send = bot.send_message(message.chat.id, "Рад увидеть тебя снова в игре!", reply_markup=markup)
        else:
            send = bot.send_message(message.chat.id, "Вы были успешно зарегистрированы", reply_markup=markup)

        bot.register_next_step_handler(send, menu)

    else:
        markup = markups.create_start_markup()
        if answer in ['/start', '/reset']:
            send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
        else:
            send = bot.send_message(message.chat.id, "Выбери что-то из списка", reply_markup=markup)
        bot.register_next_step_handler(send, start_game)

def menu(message):
    database.drop_duplicates()
    answer = message.text
    print(f"{datetime.datetime.now()}, {answer}, {message.from_user.id}, {message.from_user.username}")
    if answer == "Режимы":
        markup = markups.create_gamemodes_markup()
        send = bot.send_message(message.chat.id, "Доступные режимы", reply_markup=markup)
        bot.register_next_step_handler(send, gamemodes_menu)
    elif answer == "Как играть 🤔":
        markup = markups.create_menu_markup()
        send = bot.send_message(message.chat.id, messages.HOW_TO_PLAY, reply_markup=markup)
        bot.register_next_step_handler(send, menu)
    elif answer in ['/start', '/reset']:
        markup = markups.create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    else:
        markup = markups.create_menu_markup()
        send = bot.send_message(message.chat.id, "Выбери что-то из списка", reply_markup=markup)
        bot.register_next_step_handler(send, menu)

def gamemodes_menu(message):
    answer = message.text
    print(f"{datetime.datetime.now()}, {answer}, {message.from_user.id}, {message.from_user.username}")
    if answer == "Назад":
        markup = markups.create_menu_markup()
        send = bot.send_message(message.chat.id, "Главное меню", reply_markup=markup)
        bot.register_next_step_handler(send, menu)
    elif answer in ['/start', '/reset']:
        markup = markups.create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    elif answer == "Одиночный | Москва":
        markup = markups.create_single_game_menu_markup(mode="Moscow")
        send = bot.send_message(message.chat.id, "Одиночный по Москве", reply_markup=markup)
        bot.register_next_step_handler(send, moscow_single_game_menu)
    elif answer == "Одиночный | Санкт-Петербург":
        markup = markups.create_single_game_menu_markup(mode="SPB")
        send = bot.send_message(message.chat.id, "Одиночный по Санкт-Петербургу", reply_markup=markup)
        bot.register_next_step_handler(send, spb_single_game_menu)
    elif answer == "Одиночный | Россия":
        markup = markups.create_single_game_menu_markup(mode="Russia")
        send = bot.send_message(message.chat.id, "Одиночный по России", reply_markup=markup)
        bot.register_next_step_handler(send, russia_single_game_menu)
    elif answer == "Одиночный | Беларусь":
        markup = markups.create_single_game_menu_markup(mode="Belarus")
        send = bot.send_message(message.chat.id, "Одиночный по Беларуси", reply_markup=markup)
        bot.register_next_step_handler(send, belarus_single_game_menu)
    else:
        markup = markups.create_gamemodes_markup()
        send = bot.send_message(message.chat.id, "Выбери что-то из списка", reply_markup=markup)
        bot.register_next_step_handler(send, gamemodes_menu)

def moscow_single_game_menu(message):
    answer = message.text
    print(f"{datetime.datetime.now()}, {answer}, {message.from_user.id}, {message.from_user.username}")
    if answer == "Назад":
        markup = markups.create_gamemodes_markup()
        send = bot.send_message(message.chat.id, "Доступные режимы", reply_markup=markup)
        bot.register_next_step_handler(send, gamemodes_menu)
    elif answer in ['/start', '/reset']:
        markup = markups.create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    elif answer == "Правила 🤓":
        markup = markups.create_single_game_menu_markup(mode="Moscow")
        send = bot.send_message(message.chat.id, messages.MOSCOW_SINGLE_PLAYER_RULES, reply_markup=markup)
        bot.register_next_step_handler(send, moscow_single_game_menu)
    elif answer == "Топ игроков":
        top_10_text = bot_functions.get_top10_single(mode="Moscow")
        send = bot.send_message(message.chat.id, top_10_text)
        bot.register_next_step_handler(send, moscow_single_game_menu)
    elif answer == "Прошлые 5 игр":
        last_5_games = bot_functions.get_last5_results_single(message.from_user.id, "Moscow")
        send = bot.send_message(message.chat.id, last_5_games)
        bot.register_next_step_handler(send, moscow_single_game_menu)
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                print("ответ получен", message.from_user.id,
                      message.from_user.username)
                markup = markups.create_single_game_menu_markup(mode="Moscow")
                cords = message.web_app_data.data
                score, metres = bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
                photo_url = bot_functions.get_url(cords=cords)

                print(score, metres, message.from_user.username)
                database.add_results_moscow_single(message.from_user.id, score)
                database.add_game_moscow_single(tele_id=message.from_user.id, score=score, metres=metres)
                txt = bot_functions.create_result_text(score=score, metres=metres)
                send = bot.send_photo(message.chat.id, photo_url, caption=txt, reply_markup=markup)
                # send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {
                #                         metres} метров", reply_markup=markup)
                
                bot.register_next_step_handler(send, moscow_single_game_menu)
        else:
            markup = markups.create_single_game_menu_markup(mode="Moscow")
            send = bot.send_message(
                message.chat.id, "Выбери что-то из списка", reply_markup=markup)
            bot.register_next_step_handler(send, moscow_single_game_menu)

def spb_single_game_menu(message):
    answer = message.text
    print(f"{datetime.datetime.now()}, {answer}, {message.from_user.id}, {message.from_user.username}")
    if answer == "Назад":
        markup = markups.create_gamemodes_markup()
        send = bot.send_message(message.chat.id, "Доступные режимы", reply_markup=markup)
        bot.register_next_step_handler(send, gamemodes_menu)
    elif answer in ['/start', '/reset']:
        markup = markups.create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    elif answer == "Правила 🤓":
        markup = markups.create_single_game_menu_markup(mode="SPB")
        send = bot.send_message( message.chat.id, messages.SPB_SINGLE_PLAYER_RULES, reply_markup=markup)
        bot.register_next_step_handler(send, spb_single_game_menu)
    elif answer == "Топ игроков":
        top_10_text = bot_functions.get_top10_single(mode="SPB")
        send = bot.send_message(message.chat.id, top_10_text)
        bot.register_next_step_handler(send, spb_single_game_menu)
    elif answer == "Прошлые 5 игр":
        last_5_games = bot_functions.get_last5_results_single(message.from_user.id, "SPB")
        send = bot.send_message(message.chat.id, last_5_games)
        bot.register_next_step_handler(send, spb_single_game_menu)
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                print("ответ получен", message.from_user.id,
                      message.from_user.username)
                markup = markups.create_single_game_menu_markup(mode="SPB")
                cords = message.web_app_data.data
                score, metres = bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
                photo_url = bot_functions.get_url(cords=cords)

                print(score, metres, message.from_user.username)
                database.add_results_spb_single(message.from_user.id, score)
                database.add_game_spb_single(tele_id=message.from_user.id, score=score, metres=metres)
                txt = bot_functions.create_result_text(score=score, metres=metres)
                send = bot.send_photo(message.chat.id, photo_url, caption=txt, reply_markup=markup)
                # send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {
                #                         metres} метров", reply_markup=markup)
                
                bot.register_next_step_handler(send, spb_single_game_menu)
        else:
            markup = markups.create_single_game_menu_markup(mode="SPB")
            send = bot.send_message(
                message.chat.id, "Выбери что-то из списка", reply_markup=markup)
            bot.register_next_step_handler(send, spb_single_game_menu)

def russia_single_game_menu(message):
    answer = message.text
    print(f"{datetime.datetime.now()}, {answer}, {message.from_user.id}, {message.from_user.username}")
    if answer == "Назад":
        markup = markups.create_gamemodes_markup()
        send = bot.send_message(message.chat.id, "Доступные режимы", reply_markup=markup)
        bot.register_next_step_handler(send, gamemodes_menu)
    elif answer in ['/start', '/reset']:
        markup = markups.create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, { message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    elif answer == "Правила 🤓":
        markup = markups.create_single_game_menu_markup(mode="Russia")
        send = bot.send_message(message.chat.id, messages.RUSSIA_SINGLE_PLAYER_RULES, reply_markup=markup)
        bot.register_next_step_handler(send, russia_single_game_menu)
    elif answer == "Топ игроков":
        top_10_text = bot_functions.get_top10_single(mode="Russia")
        send = bot.send_message(message.chat.id, top_10_text)
        bot.register_next_step_handler(send, russia_single_game_menu)
    elif answer == "Прошлые 5 игр":
        last_5_games = bot_functions.get_last5_results_single(message.from_user.id, "Russia")
        send = bot.send_message(message.chat.id, last_5_games)
        bot.register_next_step_handler(send, russia_single_game_menu)
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                print("ответ получен", message.from_user.id,
                      message.from_user.username)
                markup = markups.create_single_game_menu_markup(mode="Russia")
                cords = message.web_app_data.data
                score, metres = bot_functions.calculate_score_and_distance_russia(cords=cords)
                photo_url = bot_functions.get_url(cords=cords)

                print(score, metres, message.from_user.username)
                database.add_results_russia_single(message.from_user.id, score)
                database.add_game_russia_single(tele_id=message.from_user.id, score=score, metres=metres)
                txt = bot_functions.create_result_text(score=score, metres=metres)
                send = bot.send_photo(message.chat.id, photo_url, caption=txt, reply_markup=markup)
                # send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {
                #                         metres} метров", reply_markup=markup)
                
                bot.register_next_step_handler(send, russia_single_game_menu)
        else:
            markup = markups.create_single_game_menu_markup(mode="Russia")
            send = bot.send_message(message.chat.id, "Выбери что-то из списка", reply_markup=markup)
            bot.register_next_step_handler(send, russia_single_game_menu)

def belarus_single_game_menu(message):
    answer = message.text
    print(f"{datetime.datetime.now()}, {answer}, {message.from_user.id}, {message.from_user.username}")
    if answer == "Назад":
        markup = markups.create_gamemodes_markup()
        send = bot.send_message(message.chat.id, "Доступные режимы", reply_markup=markup)
        bot.register_next_step_handler(send, gamemodes_menu)
    elif answer in ['/start', '/reset']:
        markup = markups.create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, { message.from_user.first_name}' + messages.GREETING, reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    elif answer == "Правила 🤓":
        markup = markups.create_single_game_menu_markup(mode="Belarus")
        send = bot.send_message(message.chat.id, messages.BELARUS_SINGLE_PLAYER_RULES, reply_markup=markup)
        bot.register_next_step_handler(send, belarus_single_game_menu)
    elif answer == "Топ игроков":
        top_10_text = bot_functions.get_top10_single(mode="Belarus")
        send = bot.send_message(message.chat.id, top_10_text)
        bot.register_next_step_handler(send, belarus_single_game_menu)
    elif answer == "Прошлые 5 игр":
        last_5_games = bot_functions.get_last5_results_single(message.from_user.id, "Belarus")
        send = bot.send_message(message.chat.id, last_5_games)
        bot.register_next_step_handler(send, belarus_single_game_menu)
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                print("ответ получен", message.from_user.id,
                      message.from_user.username)
                markup = markups.create_single_game_menu_markup(mode="Belarus")
                cords = message.web_app_data.data
                score, metres = bot_functions.calculate_score_and_distance_russia(cords=cords)
                photo_url = bot_functions.get_url(cords=cords)

                print(score, metres, message.from_user.username)
                database.add_results_belarus_single(message.from_user.id, score)
                database.add_game_belarus_single(tele_id=message.from_user.id, score=score, metres=metres)
                txt = bot_functions.create_result_text(score=score, metres=metres)
                send = bot.send_photo(message.chat.id, photo_url, caption=txt, reply_markup=markup)
                # send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {
                #                         metres} метров", reply_markup=markup)
                
                bot.register_next_step_handler(send, belarus_single_game_menu)
        else:
            markup = markups.create_single_game_menu_markup(mode="Belarus")
            send = bot.send_message(message.chat.id, "Выбери что-то из списка", reply_markup=markup)
            bot.register_next_step_handler(send, belarus_single_game_menu)

@bot.message_handler(content_types='text', chat_types=['private'])
def message_reply(message):
    if message.text == "Тык" or message.text == "тык":
        bot.send_message(message.chat.id, "Зачем тыкнул??")
    elif (message.text).lower() == "amogus" or (message.text).lower() == "amongus":
        bot.send_message(message.chat.id, "when the imposter is sus")
    else:
        bot.send_message(
            message.chat.id, "Чтобы перезапустить отправьте /reset")

@bot.message_handler(chat_types=["group", "supergroup", "channel"])
def message_reply_not_private(message):
    bot.send_message(message.chat.id, "Бот работает только в личной переписке")

while True:
    try:
        bot.polling(none_stop=True, timeout=500, long_polling_timeout=500)
    except Exception as e:
        print(datetime.datetime.now(), e)
        sleep(3)
