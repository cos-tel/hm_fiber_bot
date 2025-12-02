from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import admins


def main_kb(tg_id: int):
    """Создание клавиатуры Главное меню"""
    kb_list = [
        [KeyboardButton(text="🖋 Ввести продукт")],
        [KeyboardButton(text="📊 Получить данные за текущий день")],
        [KeyboardButton(text="📖 Информация о боте")],
        [KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="📝 Заполнить анкету")],
    ]
    if tg_id in admins:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder="Выберите один из пунктов меню")
    return keyboard

def gender_kb():
    """Создание кнопок выбора пола"""
    kb_list = [
        [KeyboardButton(text="👨‍🦱Мужчина")],
        [KeyboardButton(text="👩‍🦱Женщина")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите пол: "
    )
    return keyboard

def check_data_kb():
    """Инлайн клавиатура для проверки введенных данных"""
    kb_list = [
        [InlineKeyboardButton(text="✅Все верно", callback_data="correct")],
        [InlineKeyboardButton(text="❌Заполнить сначала", callback_data="incorrect")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard
