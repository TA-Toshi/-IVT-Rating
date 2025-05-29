from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext

from keyboards.inline_keyboards import sub_keyboard
from yd.db import add_to_db
from yd.yd_api import get_by_stud_id, format_student_data
from states.states import StudentStates

router = Router()


@router.message(F.text == "📊 Успеваемость")
async def process_direction(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(StudentStates.waiting_stud_id)
    await message.answer(
        "Введите 7-значный студенческий номер:",
        parse_mode="HTML"
    )


@router.message(
    StudentStates.waiting_stud_id,
    F.text.regexp(r'^\d{7}$')
)
async def process_stud_id(message: types.Message, state: FSMContext):
    await state.update_data(student_id=message.text)

    result = get_by_stud_id(message.text)
    if result is False:
        await message.answer("❌ Студент не найден")
    else:
        await message.answer(
            format_student_data(result),
            parse_mode="HTML"
        )
        await message.answer(text="Подписаться на обновления?", reply_markup=sub_keyboard)
        await state.set_state(StudentStates.waiting_sub)


@router.callback_query(F.data.startswith("sub_"), StudentStates.waiting_sub)
async def sub_yes_no(callback: types.CallbackQuery, state: FSMContext):
    approval = callback.data.split("_")[1]
    data = await state.get_data()
    if approval == "yes":
        await add_to_db(callback.from_user.id, data["student_id"])
        await callback.message.edit_text(f"Подписка на студента - {data['student_id']}")
        await state.clear()
    else:
        await callback.message.delete()
        await state.clear()


@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Действие отменено",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(StudentStates.waiting_stud_id)
async def wrong_stud_id(message: types.Message, state: FSMContext):
    await message.answer("❌ Введите 7 цифр студенческого номера")
    await state.set_state(StudentStates.waiting_stud_id)
