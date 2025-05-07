from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def directions_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="📊 Успеваемость"),
        types.KeyboardButton(text="‍👩‍👦 Подписки")
    )
    builder.adjust(2)
    return builder.as_markup(
        resize_keyboard=True
    )
