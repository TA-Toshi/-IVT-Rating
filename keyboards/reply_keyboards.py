from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

directions_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Успеваемость"),
         KeyboardButton(text="‍👩‍👦 Подписки")],
    ],
    resize_keyboard=True
)
