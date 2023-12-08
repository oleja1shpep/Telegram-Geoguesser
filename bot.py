import telebot
from telebot import types
from random import seed, randrange

TOKEN = '6844158621:AAFk18qL8jvvqrpnguZgUH3PU7U8oOtryGE'

bot = telebot.TeleBot(TOKEN) 

@bot.message_handler(commands=['start', 'reset'])
def hello_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_1 = types.KeyboardButton("Зарегистрироваться")
    item_2 = types.KeyboardButton("Войти")
    markup.add(item_1, item_2)
    send = bot.send_message(message.chat.id,"Привет я геогесср бот",reply_markup=markup)
    bot.register_next_step_handler(send, login_or_register)

def login_or_register(message):
    answer = message.text
    if answer == 'Войти':
        send = bot.send_message(message.chat.id,"Введите логин")
        bot.register_next_step_handler(send, login)
    elif answer == "Зарегистрироваться":
        send = bot.send_message(message.chat.id,"Введите логин")
        bot.register_next_step_handler(send, register)

def login(message):
    user_login = message.text
    print(user_login)
    send = bot.send_message(message.chat.id,f'{user_login} - очень крутой логин!')


def register(message):
    user_login = message.text
    print(user_login)
    send = bot.send_message(message.chat.id,f'{user_login} - очень крутой логин!')

@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=="Тык" or  message.text=="тык":
        bot.send_message(message.chat.id,"Зачем тыкнул??")
    elif (message.text).lower() == "amogus" or (message.text).lower() == "amongus":
        bot.send_message(message.chat.id,"when the imposter is sus")

@bot.message_handler(content_types='dice')
def dice_reply(message):
    bot.send_message(message.chat.id, f'Выпадет число {message.dice.value}')


bot.polling(none_stop=True, interval=0)