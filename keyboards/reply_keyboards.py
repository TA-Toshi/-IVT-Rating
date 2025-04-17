from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def directions_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="ИВТ"),
        types.KeyboardButton(text="ИТ"),
        types.KeyboardButton(text="ПИЭ"),
        types.KeyboardButton(text="❌ Отмена")
    )
    builder.adjust(2)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
