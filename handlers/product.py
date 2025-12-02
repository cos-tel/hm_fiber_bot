import asyncio
import asyncio
from decimal import Decimal
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from create_bot import bot
from db_handler.db_requests import get_product_id_fiber, insert_calc_fiber, get_tg_id
from keybords.all_keybords import gender_kb, check_data_kb, main_kb

class ProductForm(StatesGroup):
    product = State()

product_router = Router()

@product_router.message(F.text == "🖋 Ввести продукт")
async def send_message_to_query(message: Message, state: FSMContext):
    """Ввод количество продукта"""
    await state.clear()
    await message.answer(
        "Введите значение в формате \n'\\продукт\\ \\количество в граммах\\' (например 'банан 200')"
        )
    await state.set_state(ProductForm.product)

@product_router.message(ProductForm.product)
async def map_product_data(message: Message, state: FSMContext):
    """Преобразование введенного значения для двух полей (продукт и количество)"""
    await state.update_data(
        product_amount_list=message.text.lower().strip().split() # получаем словарь со списком
        )
    data = await state.get_data()
    len_list = len(data["product_amount_list"])
    product_name = " ".join(data["product_amount_list"][:(len_list-1)])
    product_id_amount_fiber = get_product_id_fiber(product_name)
    user_id = await get_tg_id(str(message.from_user.id))
    product_dict = {}
    product_dict["user_id"] = user_id["user_id"]
    fiber_per_100 = 0
    for product in product_id_amount_fiber:
        fiber_per_100 = product[1]
        product_dict["product_id"] = product[0]
    product_dict["amount_product"] = Decimal(data["product_amount_list"][-1])
    product_dict["calc_amount_fiber"] = (product_dict["amount_product"] * fiber_per_100) / 100
    await insert_calc_fiber(product_dict)
    await message.answer(f"Количество клетчатки: <b>{product_dict["calc_amount_fiber"]}</b>")
    await state.clear()
