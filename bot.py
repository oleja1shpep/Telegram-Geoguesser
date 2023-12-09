import telebot
from telebot import types
import database
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

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

def get_top10():
    top10 = database.get_top10()
    return 0

@bot.message_handler(commands=['start', 'reset'])
def hello_message(message):
    markup = create_start_markup()

    send = bot.send_message(message.chat.id,f'Привет, {message.from_user.username}, я геогесср бот',reply_markup=markup)
    bot.register_next_step_handler(send, start_game)

def start_game(message):
    answer = message.text
    tele_id = message.from_user.id
    tele_username = message.from_user.username

    if answer == 'Играть':
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
        print(f"топ, {message.from_user.id}")
        top10 = get_top10()

        bot.register_next_step_handler(message, menu)

    elif answer == "Одиночный режим":
        print(f"одиночный, {message.from_user.id}")
        bot.register_next_step_handler(message, menu)

    elif answer in ['/start', '/reset']:
        markup = create_start_markup()
        send = bot.send_message(message.chat.id, f'Привет, {message.from_user.username}, я геогесср бот',reply_markup=markup)
        bot.register_next_step_handler(send, start_game)
    else:
        markup = create_menu_markup()
        send = bot.send_message(message.chat.id,"Выбери что-то из списка", reply_markup=markup)
        bot.register_next_step_handler(send, menu)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=="Тык" or  message.text=="тык":
        bot.send_message(message.chat.id,"Зачем тыкнул??")
    elif (message.text).lower() == "amogus" or (message.text).lower() == "amongus":
        bot.send_message(message.chat.id,"when the imposter is sus")
    elif message.text=="Меню" or message.text=="меню":
        if (database.search_tele_id(tele_id = message.from_user.id)):
            markup = create_menu_markup()
            bot.send_message(message.chat.id, "Главное меню",reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Перед заходом в меню, пожалуйста, зарегестрируйтесь")
            

@bot.message_handler(content_types='dice')
def dice_reply(message):
    bot.send_message(message.chat.id, f'Выпадет число {message.dice.value}')


bot.polling(none_stop=True, interval=0)