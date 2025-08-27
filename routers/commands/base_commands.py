from aiogram import types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import or_f
from keyboards.reply_keyboards import directions_keyboard
from states.states import StudentStates
from yd.db import add_to_db, del_from_db, get_by_telegram_id, del_all_by_id
from yd.yd_api import get_by_stud_id, format_student_data

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(StudentStates.waiting_direction)
    await message.answer(
        "👋 <b>Бот проверки успеваемости</b>\n",
        reply_markup=directions_keyboard,
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(text="Тут будут ниструкции")


@router.message(Command("sub"))
async def cmd_sub(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Укажите номер студенческого")
    await state.set_state(StudentStates.pre_sub)


@router.message(Command("unsub"))
async def cmd_sub(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = []
    students = await get_by_telegram_id(message.from_user.id)
    if students:
        for i in range(0, len(students), 2):
            row = students[i:i + 2]
            keyboard_row = [
                InlineKeyboardButton(text=name, callback_data=name)
                for name in row
            ]
            keyboard.append(keyboard_row)
        keyboard.append([InlineKeyboardButton(text="Все", callback_data="all")])
        await message.answer(
            text="От кого выхотите отписаться?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await state.set_state(StudentStates.unsub)
    else:
        await message.answer(text=f"У вас нет подписок.")
        await state.clear()


@router.message(or_f(Command("check"), F.text == "‍👩‍👦 Подписки"))
async def check_by_sub(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = []
    students = await get_by_telegram_id(message.from_user.id)
    if students:
        for i in range(0, len(students), 2):
            row = students[i:i + 2]
            keyboard_row = [
                InlineKeyboardButton(text=name, callback_data=name)
                for name in row
            ]
            keyboard.append(keyboard_row)
        await message.answer(
            text="Чью успеваемость вы хотите посмотреть?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await state.set_state(StudentStates.check)
    else:
        await message.answer(
            text="У вас нет подписок.",
        )


@router.message(StudentStates.pre_sub, F.text.regexp(r'^\d{7}$'))
async def pre_cmd_sub(message: types.Message, state: FSMContext):
    result = get_by_stud_id(message.text)
    if result is False:
        await message.answer(text=f"Студента с №{message.text} нет")
        await state.set_state(StudentStates.pre_sub)
    else:
        await add_to_db(message.from_user.id, message.text)
        await message.answer(text=f"Подписка на обновления студента №{message.text}")
        await state.clear()


@router.message(StudentStates.pre_sub)
async def sub_err(message: types.Message, state: FSMContext):
    await message.answer(text=f"❌ Введите 7 цифр студенческого номера")
    await state.set_state(StudentStates.pre_sub)


@router.callback_query(StudentStates.unsub)
async def unsub_choice(callback: types.CallbackQuery, state: FSMContext):
    student = callback.data
    if student == "all":
        await del_all_by_id(callback.from_user.id)
        await callback.message.edit_text(text=f"Вы отписались от всех")
        await state.clear()
    else:
        await del_from_db(callback.from_user.id, student)
        await callback.message.edit_text(text=f"Вы отписались от {student}")
        await state.clear()


@router.callback_query(StudentStates.check)
async def check_by_sub_choice(callback: types.CallbackQuery, state: FSMContext):
    student = callback.data
    student_data = get_by_stud_id(student)
    await callback.message.edit_text(
        format_student_data(student_data),
        parse_mode="HTML"
    )
    await state.clear()
