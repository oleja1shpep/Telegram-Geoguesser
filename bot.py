import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import messages
import database
import markups
import bot_functions
from config import TOKEN_BOT

form_router = Router()

class Form(StatesGroup):
    start = State()
    menu = State()
    gamemodes = State()
    single_game_menu = State()

@form_router.message(CommandStart(), F.chat.type == "private")
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.start)
    await message.answer(
        f'Привет, {message.from_user.first_name}!' + messages.GREETING,
        reply_markup = markups.create_start_markup()
    )


@form_router.message(Form.start, F.text == "Играть")
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)

    tele_id = message.from_user.id
    tele_username = message.from_user.username
    markup = markups.create_menu_markup()

    if (database.search_tele_id(tele_id=tele_id, tele_username=tele_username)):
        await message.answer(
            "Рад увидеть тебя снова в игре!",
            reply_markup= markup
        )
    else:
        await message.answer(
            "Вы были успешно зарегистрированы",
            reply_markup= markup
        )

@form_router.message(Form.menu, F.text[:-2] == "Как играть")
async def process_name(message: Message, state: FSMContext) -> None:
    database.drop_duplicates()
    await message.answer(
        messages.HOW_TO_PLAY
    )

@form_router.message(Form.menu, F.text == "Режимы")
async def process_name(message: Message, state: FSMContext) -> None:
    database.drop_duplicates()
    await state.set_state(Form.gamemodes)
    markup = markups.create_gamemodes_markup()
    await message.answer(
        "Доступные режимы",
        reply_markup= markup
    )

@form_router.message(Form.gamemodes, F.text == "Назад")
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    markup = markups.create_menu_markup()
    await message.answer(
        "Главное меню",
        reply_markup= markup
    )


@form_router.message(Form.gamemodes, F.text[:9] == "Одиночный")
async def process_name(message: Message, state: FSMContext) -> None:
    answer = message.text
    mode = "Moscow"
    if (answer == "Одиночный | Москва"):
        mode = "Moscow"
        markup = markups.create_single_game_menu_markup(mode)
        await message.answer(
            "Одиночный по москве",
            reply_markup= markup
        )
    elif (answer == "Одиночный | Санкт-Петербург"):
        mode = "SPB"
        markup = markups.create_single_game_menu_markup(mode)
        await message.answer(
            "Одиночный по Санкт-Петербургу",
            reply_markup= markup
        )
    elif (answer == "Одиночный | Россия"):
        mode = "Russia"
        markup = markups.create_single_game_menu_markup(mode)
        await message.answer(
            "Одиночный по России",
            reply_markup= markup
        )
    elif (answer == "Одиночный | Беларусь"):
        mode = "Belarus"
        markup = markups.create_single_game_menu_markup(mode)
        await message.answer(
            "Одиночный по Беларуси",
            reply_markup= markup
        )

    await state.set_state(Form.single_game_menu)
    await state.update_data(gamemodes = mode)
    

@form_router.message(Form.single_game_menu)
async def process_name(message: Message, state: FSMContext) -> None:
    mode = await state.get_data()
    mode = mode["gamemodes"]
    answer = message.text
    if (answer == "Правила 🤓"):
        if (mode == "Moscow"):
            await message.answer(
                messages.MOSCOW_SINGLE_PLAYER_RULES
            )
        elif (mode == "SPB"):
            await message.answer(
                messages.SPB_SINGLE_PLAYER_RULES
            )
        elif (mode == "Russia"):
            await message.answer(
                messages.RUSSIA_SINGLE_PLAYER_RULES
            )
        elif (mode == "Belarus"):
            await message.answer(
                messages.BELARUS_SINGLE_PLAYER_RULES
            )
    elif (answer == "Топ игроков"):
        top_10_text = bot_functions.get_top10_single(mode=mode)
        await message.answer(
            top_10_text
        )
    elif (answer == "Прошлые 5 игр"):
        last_5_games = bot_functions.get_last5_results_single(message.from_user.id, mode)
        await message.answer(
            last_5_games
        )
    elif (answer == "Назад"):
        await state.set_state(Form.gamemodes)
        markup = markups.create_gamemodes_markup()
        await message.answer(
            "Доступные режимы",
            reply_markup= markup
        )
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                print("ответ получен", message.from_user.id,
                      message.from_user.username)
                cords = message.web_app_data.data
                if (mode == "SPB" or mode == "Moscow"):
                    score, metres = bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
                elif (mode == "Russia" or mode == "Belarus"):
                    score, metres = bot_functions.calculate_score_and_distance_russia(cords=cords)

                photo_url = bot_functions.get_url(cords=cords)

                print(score, metres, message.from_user.username)
                database.add_results_single(message.from_user.id, score, mode)
                database.add_game_single(tele_id=message.from_user.id, score=score, metres=metres, mode=mode)
                txt = bot_functions.create_result_text(score=score, metres=metres)
               
                await message.answer_photo(photo_url, caption=txt)
                # send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {
                #                         metres} метров", reply_markup=markup)

async def main():
    bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())