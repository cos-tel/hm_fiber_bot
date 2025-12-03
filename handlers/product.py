from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from db_handler.db_requests import (
    get_product_id_fiber,
    insert_calc_amount_fiber,
)

PRODUCT_REQUEST = """
<b>Введите значение в формате:</b>
<em>[продукт] [количество в граммах]</em>
(например 'банан 200')
"""


class ProductForm(StatesGroup):
    product = State()


product_router = Router()


@product_router.message(F.text == "🖋 Ввести продукт")
async def send_message_to_query(message: Message, state: FSMContext, product_dict=None):
    """Ввод количество продукта"""
    await state.clear()
    await message.answer(PRODUCT_REQUEST)
    await state.set_state(ProductForm.product)


@product_router.message(ProductForm.product)
async def map_product_data(message: Message, state: FSMContext, product_dict=None):
    """Преобразование введенного значения для двух полей (продукт и количество)"""
    await state.update_data(product_amount_list=message.text.lower().strip().split())  # type: ignore
    dict_enter_data = await state.get_data()
    product_name = " ".join(dict_enter_data["product_amount_list"][:-1])
    try:
        amount_product = Decimal(
            dict_enter_data["product_amount_list"][-1].replace(",", ".")
        )
    except InvalidOperation:
        await message.answer("Неправильный формат запроса")
        await message.answer(PRODUCT_REQUEST)
        return
    product_id_amount_fiber_by_name = get_product_id_fiber(product_name)
    if not product_id_amount_fiber_by_name:
        await message.answer("Продукт не найден")
        await message.answer(PRODUCT_REQUEST)
        return
    product_id, amount_fiber_per_100 = product_id_amount_fiber_by_name[0]  # type: ignore
    tg_id = str(message.from_user.id)  # type: ignore
    calc_amount_fiber = (amount_product * amount_fiber_per_100) / 100
    params = (product_id, tg_id, amount_product, calc_amount_fiber)
    insert_calc_amount_fiber(params)
    await message.answer(f"Количество клетчатки: <b>{calc_amount_fiber}</b>")
    await state.clear()
