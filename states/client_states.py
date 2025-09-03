from aiogram.fsm.state import StatesGroup, State

class OrderServiceState(StatesGroup):
    choosing_service = State()
    entering_pickup = State()
    entering_dropoff = State()
    entering_date = State()
    entering_hour = State()
    entering_minute = State()
    confirming_datetime = State()
    confirming_order = State()
