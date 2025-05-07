from aiogram.fsm.state import StatesGroup, State


class StudentStates(StatesGroup):
    waiting_direction = State()
    waiting_stud_id = State()
    waiting_sub = State()
    unsub = State()
    check = State()
