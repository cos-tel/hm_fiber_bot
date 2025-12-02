"""Хэндлеры"""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db_handler.db_requests import get_daily_amount_fiber, get_tg_id
from keybords.all_keybords import main_kb

# from handlers.info_template import get_daily_calories_intake

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Приветственное сообщение после старта"""
    await state.clear()
    await message.answer(
        "Привет! Я бот, который поможет подсчитать количество клетчатки",
        reply_markup=main_kb(message.from_user.id),
    )  # type: ignore


@start_router.message(F.text == "📖 Информация о боте")
async def get_info_about_bot(message: Message):
    """Кнопка информация о боте выдает информацию"""
    msg = """
Я - бот, который поможет тебе подсчитать количество клетчатки, которое Вы употребили.
Пока я выполняю рассчет из небольшого количества продуктов, которые есть в базе данных.
В дальшейшем планируется модернизация и добавление новых функций: расчет из полного списка
продуктов, рассчет из блюд. В случае, если бот не отвечает, то введите команду /start.
В стартовом меню, выберите пункт "Ввести продукт", после введите продукт и количество в граммах
(в формате "банан 100"). Спасибо, что используете нас, Ваш <b>How much fiber</b>
"""
    await message.answer(msg)


@start_router.message(F.text == "👤 Профиль")
async def get_user_info(message: Message):
    """Кнопка возвращает информацию о пользователе"""
    user_data = await get_tg_id(str(message.from_user.id))  # type: ignore
    msg = f"""
Информация о пользователе\n\nВаш никнейм: <b>{user_data["user_name"]}</b>\n
Ваш пол: <b>{user_data["user_sex"]}</b>\n
Примерная суточная норма потребляемых калорий: <b>{user_data["daily_calorie_intake"]}</b> ккл\n
Желаемая суточная норма потребляемой клетчатки: <b>{user_data["daily_fiber_requirement"]}</b> г
"""
    await message.answer(msg)


@start_router.message(F.text == "📊 Получить данные за текущий день")
async def get_today_info(message: Message):
    """Представление данных за текущий день"""
    result = get_daily_amount_fiber(str(message.from_user.id))
    print(result)
    user = await get_tg_id(str(message.from_user.id))
    print(user["daily_fiber_requirement"])
    if result < user["daily_fiber_requirement"]:
        info_msg = f"""Количество клетчатки на текущий момент: <b>{result}</b> г.
До суточной нормы осталось: <b>{user["daily_fiber_requirement"] - result}</b> г"""
    elif result > user["daily_fiber_requirement"]:
        info_msg = f"""Количество клетчатки на текущий момент: <b>{result}</b> г.
Вы превысили норму на <b>{result - user["daily_fiber_requirement"]}</b>. Отличный результат!"""
    else:
        info_msg = "Супер, Вы достигли суточной нормы!"
    await message.answer(info_msg)
