"""Хендлер и вопросы для анкеты"""
import asyncio
from decimal import Decimal
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from create_bot import bot
from db_handler.db_requests import insert_user
from keybords.all_keybords import gender_kb, check_data_kb, main_kb


class Form(StatesGroup):
    """Форма для анкеты"""
    daily_calorie_intake = State()
    daily_fiber_requirement = State()
    user_sex = State()
    check_state = State()

info_template_router = Router()

@info_template_router.message(F.text == "📝 Заполнить анкету")
async def input_user_sex(message: Message, state: FSMContext):
    """Получить суточную норму калориев пользователя"""
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.answer("Выберите свой пол", reply_markup=gender_kb())
    await state.set_state(Form.user_sex)

@info_template_router.message(
        (F.text.lower().contains("мужчина")) | F.text.lower().contains("женщина"),
        Form.user_sex
        )
async def input_calorie(message: Message, state: FSMContext):
    """Проверка количества калориев и просьба ввести предполагаемую норму клетчатки"""
    await state.update_data(
        user_sex=message.text.replace("👨‍🦱", "").replace("👩‍🦱", ""),
        tg_id=str(message.from_user.id),
        user_name=message.from_user.username
        )
    await message.answer("Введите примерную норму потребляемых калорий в сутки")
    await state.set_state(Form.daily_calorie_intake)

@info_template_router.message(
        Form.daily_calorie_intake,
        lambda message: message.text.isdigit()
        )
async def input_fiber_requirement(message: Message, state: FSMContext):
    """Проверка калорий и выдача предварительно заполненных данных"""
    if  Decimal(message.text) < 0 or Decimal(message.text) > 10000:
        await message.answer("Пожалуйста, введите корректное значение больше нуля")
        return
    await state.update_data(daily_calorie_intake=Decimal(message.text))
    await message.answer("Теперь введите примерную суточную норму клетчатки")
    await state.set_state(Form.daily_fiber_requirement)

@info_template_router.message(
        Form.daily_fiber_requirement,
        lambda message: message.text.isdigit()
        )
async def check_input_date(message: Message, state: FSMContext):
    """Проверка клетчатки и всех введенных данных"""
    if  Decimal(message.text) < 0 or Decimal(message.text) > 10000:
        await message.answer("Пожалуйста, введите корректное значение больше нуля")
        return
    await state.update_data(daily_fiber_requirement=Decimal(message.text))
    data = await state.get_data() # Это словарь с ключами из update_data
    msg = f"""
Пожалуйста, проверьте введенные данные\nВаш никнейм: <b>{data.get("user_name")}</b>\n
Ваш пол: <b>{data.get("user_sex")}</b>\n
Примерная суточная норма потребляемых калорий: <b>{data.get("daily_calorie_intake")}</b> ккл\n
Желаемая суточная норма потребляемой клетчатки: <b>{data.get("daily_fiber_requirement")}</b> г
"""
    await message.answer(msg, reply_markup=check_data_kb())
    await state.set_state(Form.check_state)

@info_template_router.callback_query(F.data == "correct", Form.check_state)
async def save_input_data(call: CallbackQuery, state: FSMContext):
    """Сохранение данных"""
    data = await state.get_data()
    print(data)
    await insert_user(data)
    await call.answer("Данные сохранены")
    #await call.message.edit_reply_markup(reply_markup=None)
    await call.answer("Спасибо за регистрацию. Удачи!")
    await state.clear()
    await call.message.answer("Выберите действие: ", reply_markup=main_kb(int(data.get("tg_id"))))

@info_template_router.callback_query(F.data == "incorrect", Form.check_state)
async def input_data_again(call: CallbackQuery, state: FSMContext):
    """Запуск ввода данных заново"""
    await call.answer("Запускаем ввод данных заново")
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Введите пол", reply_markup=gender_kb())
    await state.set_state(Form.user_sex)
