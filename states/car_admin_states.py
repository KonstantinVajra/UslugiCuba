from aiogram.fsm.state import StatesGroup, State

class CarAdmin(StatesGroup):
    add_car_name = State()
    add_car_brand = State()
    add_car_model = State()
    add_car_year = State()
    add_car_color = State()
    add_car_engine = State()
    add_car_transmission = State()
    add_car_fuel = State()
    add_car_price = State()
    add_car_image_url = State()
    add_car_description = State()
    add_car_confirm = State()