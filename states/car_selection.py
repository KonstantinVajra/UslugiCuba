from aiogram.fsm.state import StatesGroup, State


class CarOrder(StatesGroup):
    name = State()
    phone = State()
    comment = State()