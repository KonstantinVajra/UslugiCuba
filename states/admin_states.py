from aiogram.fsm.state import StatesGroup, State

class AddVehicleAdmin(StatesGroup):
    entering_provider_tg_id = State()
    uploading_photos = State()
    entering_title = State()
    choosing_parameters = State()
    entering_description = State()
    confirming_vehicle = State()