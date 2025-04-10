from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext

from yd.yd_api import FILE_PATH_IVT, FILE_PATH_IT, FILE_PATH_PIE, get_by_stud_id, format_student_data
from states.states import StudentStates

router = Router()


@router.message(
    StudentStates.waiting_direction,
    F.text.in_(["ИВТ", "ИТ", "ПИЭ"])
)
async def process_direction(message: types.Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await state.set_state(StudentStates.waiting_stud_id)
    await message.answer(
        "Введите 7-значный студенческий номер:",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )


@router.message(
    StudentStates.waiting_stud_id,
    F.text.regexp(r'^\d{7}$')
)
async def process_stud_id(message: types.Message, state: FSMContext):
    data = await state.get_data()
    direction = data['direction']

    direction_map = {
        "ИВТ": FILE_PATH_IVT,
        "ИТ": FILE_PATH_IT,
        "ПИЭ": FILE_PATH_PIE
    }

    result = get_by_stud_id(message.text, direction_map[direction])

    if isinstance(result, str):
        await message.answer("❌ Студент не найден")
    else:
        await message.answer(
            format_student_data(result),
            parse_mode="HTML"
        )

    await state.clear()


@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Действие отменено",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(StudentStates.waiting_stud_id)
async def wrong_stud_id(message: types.Message):
    await message.answer("❌ Введите 7 цифр студенческого номера")
