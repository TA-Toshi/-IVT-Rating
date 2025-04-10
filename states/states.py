from aiogram.fsm.state import StatesGroup, State


class StudentStates(StatesGroup):
    waiting_direction = State()
    waiting_stud_id = State()
