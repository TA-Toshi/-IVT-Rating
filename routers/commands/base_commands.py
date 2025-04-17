from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.reply_keyboards import directions_keyboard
from states.states import StudentStates
from yd.db import add_to_db, del_from_db

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(StudentStates.waiting_direction)
    await message.answer(
        "👋 <b>Бот проверки успеваемости</b>\n"
        "Выберите направление:",
        reply_markup=await directions_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(text="Тут будут ниструкции")


@router.message(Command("sub"))
async def cmd_sub(message: types.Message, command: CommandObject):

    await add_to_db(message.from_user.id, command.args)
    await message.answer(text=f"{command.args}")


@router.message(Command("unsub"))
async def cmd_sub(message: types.Message, command: CommandObject):

    await del_from_db(message.from_user.id, command.args)
    await message.answer(text=f"{command.args}")


