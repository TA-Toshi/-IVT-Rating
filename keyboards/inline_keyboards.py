from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

sub_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ДА", callback_data="sub_yes"),
         InlineKeyboardButton(text="НЕТ", callback_data="sub_no")],
    ]
)
