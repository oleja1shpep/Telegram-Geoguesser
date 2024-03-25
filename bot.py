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
from aiogram.utils.i18n import I18n, ConstI18nMiddleware, I18nMiddleware
from pathlib import Path
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from middlewares import MyI18nMiddleware
form_router = Router()

class Form(StatesGroup):
    start = State()
    menu = State()
    language_menu = State()
    gamemodes = State()
    single_game_menu = State()

@form_router.message(CommandStart(), F.chat.type == "private")
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.start)
    await message.answer(
        _('Привет, {}!{}').format(message.from_user.first_name, _(messages.GREETING)),
        reply_markup=await markups.create_start_markup()
    )


@form_router.message(Form.start, F.text == __("Играть"))
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)

    tele_id = message.from_user.id
    tele_username = message.from_user.username
    markup = await markups.create_menu_markup()

    if (await database.search_tele_id(tele_id=tele_id, tele_username=tele_username)):
        await message.answer(
            _("Рад увидеть тебя снова в игре!"),
            reply_markup = markup
        )
    else:
        await message.answer(
            _("Вы были успешно зарегистрированы"),
            reply_markup = markup
        )

@form_router.message(Form.menu, F.text == __("Как играть"))
async def process_name(message: Message, state: FSMContext) -> None:
    await database.drop_duplicates()
    await message.answer(
        text=_(messages.HOW_TO_PLAY)
    )


@form_router.message(Form.menu, F.text == __("Язык"))
async def process_name(message: Message, state: FSMContext) -> None:
    await database.drop_duplicates()
    await state.set_state(Form.language_menu)
    markup = await markups.create_language_menu_markup()
    await message.answer(
        _("Выберите язык"),
        reply_markup = markup
    )

@form_router.message(Form.language_menu, F.text == __("Русский"))
async def process_name(message: Message, state: FSMContext) -> None:
    await database.set_language(message.from_user.id, 'ru')
    await message.answer(
        _("Выбран Русский язык"),
    )

@form_router.message(Form.language_menu, F.text == __("Английский"))
async def process_name(message: Message, state: FSMContext) -> None:
    await database.set_language(message.from_user.id, 'en')
    await message.answer(
        _("Выбран Английский язык"),
    )

@form_router.message(Form.language_menu, F.text == __("Назад"))
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    markup = await markups.create_menu_markup()
    await message.answer(
        _("Главное меню"),
        reply_markup= markup
    )

@form_router.message(Form.menu, F.text == __("Режимы"))
async def process_name(message: Message, state: FSMContext) -> None:
    await database.drop_duplicates()
    await state.set_state(Form.gamemodes)
    markup = await markups.create_gamemodes_markup()
    await message.answer(
        _("Доступные режимы"),
        reply_markup = markup
    )

@form_router.message(Form.gamemodes, F.text == __("Назад"))
async def process_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    markup = await markups.create_menu_markup()
    await message.answer(
        _("Главное меню"),
        reply_markup= markup
    )


@form_router.message(Form.gamemodes, F.text.split()[0] == __("Одиночный"))
async def process_name(message: Message, state: FSMContext) -> None:
    answer = message.text
    mode = "Moscow"
    if (answer == _("Одиночный | Москва")):
        mode = "Moscow"
        markup = await markups.create_single_game_menu_markup(mode)
        await message.answer(
            _("Одиночный по москве"),
            reply_markup = markup
        )
    elif (answer == _("Одиночный | Санкт-Петербург")):
        mode = "SPB"
        markup = await markups.create_single_game_menu_markup(mode)
        await message.answer(
            _("Одиночный по Санкт-Петербургу"),
            reply_markup = markup
        )
    elif (answer == _("Одиночный | Россия")):
        mode = "Russia"
        markup = await markups.create_single_game_menu_markup(mode)
        await message.answer(
            _("Одиночный по России"),
            reply_markup = markup
        )
    elif (answer == _("Одиночный | Беларусь")):
        mode = "Belarus"
        markup = await markups.create_single_game_menu_markup(mode)
        await message.answer(
            _("Одиночный по Беларуси"),
            reply_markup = markup
        )

    await state.set_state(Form.single_game_menu)
    await state.update_data(gamemodes = mode)
    

@form_router.message(Form.single_game_menu)
async def process_name(message: Message, state: FSMContext) -> None:
    mode = await state.get_data()
    mode = mode["gamemodes"]
    answer = message.text
    if (answer == _("Правила")):
        if (mode == "Moscow"):
            await message.answer(
                _(messages.MOSCOW_SINGLE_PLAYER_RULES)
            )
        elif (mode == "SPB"):
            await message.answer(
                _(messages.SPB_SINGLE_PLAYER_RULES)
            )
        elif (mode == "Russia"):
            await message.answer(
                _(messages.RUSSIA_SINGLE_PLAYER_RULES)
            )
        elif (mode == "Belarus"):
            await message.answer(
                _(messages.BELARUS_SINGLE_PLAYER_RULES)
            )
    elif (answer == _("Топ игроков")):
        top_10_text = await bot_functions.get_top10_single(mode=mode)
        await message.answer(
            top_10_text
        )
    elif (answer == _("Прошлые 5 игр")):
        last_5_games = await bot_functions.get_last5_results_single(message.from_user.id, mode)
        await message.answer(
            last_5_games
        )
    elif (answer == _("Назад")):
        await state.set_state(Form.gamemodes)
        markup = await markups.create_gamemodes_markup()
        await message.answer(
            _("Доступные режимы"),
            reply_markup= markup
        )
    else:
        if (hasattr(message, 'web_app_data')):
            if message.web_app_data.data:
                print(_("ответ получен"), message.from_user.id,
                      message.from_user.username)
                cords = message.web_app_data.data
                if (mode == "SPB" or mode == "Moscow"):
                    score, metres = await bot_functions.calculate_score_and_distance_moscow_spb(cords=cords)
                elif (mode == "Russia" or mode == "Belarus"):
                    score, metres = await bot_functions.calculate_score_and_distance_russia(cords=cords)

                photo_url = await bot_functions.get_url(cords=cords)

                print(score, metres, message.from_user.username)
                await database.add_results_single(message.from_user.id, score, mode)
                await database.add_game_single(tele_id=message.from_user.id, score=score, metres=metres, mode=mode)
                txt = await bot_functions.create_result_text(score=score, metres=metres)
               
                await message.answer_photo(photo_url, caption=txt)
                # send = bot.send_message(message.chat.id, f"Вы набрали {score} очков\nРасстояние {
                #                         metres} метров", reply_markup=markup)

@form_router.message(F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    await message.answer(
        _("Если что-то не работает: /start")
    )

async def main():
    bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)
    i18n = I18n(path=Path(__file__).parent / 'locales', default_locale='en', domain='messages')
    i18n_middleware = MyI18nMiddleware(i18n=i18n)
    i18n_middleware.setup(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
