import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from repositories import user_repo, vehicle_repo

router = Router()
log = logging.getLogger(__name__)

class AddVehicle(StatesGroup):
    entering_make = State()
    entering_model = State()
    entering_year = State()
    entering_color = State()
    entering_engine = State()
    entering_transmission = State()
    entering_fuel = State()
    entering_price = State()
    entering_photo_url = State()
    entering_description = State()
    confirming = State()


@router.callback_query(F.data == "add_vehicle")
async def start_add_vehicle(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс добавления нового автомобиля."""
    user = await user_repo.get_user_by_tg_id(callback.from_user.id)
    if not user or user.get('role') != 'provider':
        await callback.answer("Эта функция доступна только для поставщиков.", show_alert=True)
        return

    await state.set_state(AddVehicle.entering_make)
    await callback.message.edit_text("Начинаем добавление автомобиля. Введите марку (например, 'Mercedes').\n\nВы можете отменить в любой момент, отправив /cancel.")
    await callback.answer()


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    """Позволяет пользователю отменить любое действие."""
    current_state = await state.get_state()
    if current_state is None:
        return

    log.info("Cancelling state %r for user %d", current_state, message.from_user.id)
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())


@router.message(AddVehicle.entering_make)
async def process_make(message: Message, state: FSMContext):
    await state.update_data(make=message.text)
    await state.set_state(AddVehicle.entering_model)
    await message.answer("Отлично. Теперь введите модель (например, 'E-Cabrio').")

# ... (здесь будут остальные шаги FSM) ...

@router.message(AddVehicle.entering_model)
async def process_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(AddVehicle.entering_year)
    await message.answer("Введите год выпуска.")

@router.message(AddVehicle.entering_year)
async def process_year(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (1900 < int(message.text) <= 2025):
        await message.answer("Пожалуйста, введите корректный год (число от 1901 до 2025).")
        return
    await state.update_data(year=int(message.text))
    await state.set_state(AddVehicle.entering_color)
    await message.answer("Введите цвет автомобиля.")

@router.message(AddVehicle.entering_color)
async def process_color(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await state.set_state(AddVehicle.entering_engine)
    await message.answer("Введите характеристики двигателя (например, '3.0L V6').")

@router.message(AddVehicle.entering_engine)
async def process_engine(message: Message, state: FSMContext):
    await state.update_data(engine=message.text)
    await state.set_state(AddVehicle.entering_transmission)
    await message.answer("Введите тип трансмиссии (АКПП, МКПП).")

@router.message(AddVehicle.entering_transmission)
async def process_transmission(message: Message, state: FSMContext):
    await state.update_data(transmission=message.text)
    await state.set_state(AddVehicle.entering_fuel)
    await message.answer("Введите тип топлива (бензин, дизель).")

@router.message(AddVehicle.entering_fuel)
async def process_fuel(message: Message, state: FSMContext):
    await state.update_data(fuel=message.text)
    await state.set_state(AddVehicle.entering_price)
    await message.answer("Введите цену за час аренды в USD (только число).")

@router.message(AddVehicle.entering_price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Цена должна быть числом. Пожалуйста, попробуйте еще раз.")
        return
    await state.update_data(price=price)
    await state.set_state(AddVehicle.entering_photo_url)
    await message.answer("Отправьте прямую ссылку (URL) на главное фото автомобиля.")

@router.message(AddVehicle.entering_photo_url, F.text.startswith("http"))
async def process_photo_url(message: Message, state: FSMContext):
    await state.update_data(photo_url=message.text)
    await state.set_state(AddVehicle.entering_description)
    await message.answer("И последнее: введите краткое описание автомобиля.")

@router.message(AddVehicle.entering_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    vehicle_data = await state.get_data()

    summary = "<b>Проверьте данные автомобиля:</b>\n\n"
    summary += f"<b>Марка:</b> {vehicle_data.get('make')}\n"
    summary += f"<b>Модель:</b> {vehicle_data.get('model')}\n"
    summary += f"<b>Год:</b> {vehicle_data.get('year')}\n"
    summary += f"<b>Цвет:</b> {vehicle_data.get('color')}\n"
    summary += f"<b>Двигатель:</b> {vehicle_data.get('engine')}\n"
    summary += f"<b>Трансмиссия:</b> {vehicle_data.get('transmission')}\n"
    summary += f"<b>Топливо:</b> {vehicle_data.get('fuel')}\n"
    summary += f"<b>Цена:</b> ${vehicle_data.get('price'):.2f}/час\n"
    summary += f"<b>Описание:</b> {vehicle_data.get('description')}\n"
    summary += f"<b>Фото:</b> <a href=\"{vehicle_data.get('photo_url')}\">ссылка</a>\n\n"
    summary += "Все верно? Сохраняем?"

    await message.answer(
        summary,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, сохранить", callback_data="confirm_add_vehicle")],
            [InlineKeyboardButton(text="❌ Нет, отменить", callback_data="cancel_add_vehicle")]
        ])
    )
    await state.set_state(AddVehicle.confirming)

@router.callback_query(F.data == "confirm_add_vehicle", AddVehicle.confirming)
async def confirm_vehicle_addition(callback: CallbackQuery, state: FSMContext):
    """Сохраняет автомобиль в БД после подтверждения провайдером."""
    user = await user_repo.get_user_by_tg_id(callback.from_user.id)
    provider = await user_repo.get_provider_by_user_id(user['id'])

    if not provider:
        await callback.message.edit_text("Ошибка: не удалось найти ваш профиль поставщика.")
        await state.clear()
        return

    vehicle_data = await state.get_data()
    new_vehicle = await vehicle_repo.add_vehicle(provider['id'], vehicle_data)

    if new_vehicle:
        await callback.message.edit_text(
            "✅ Ваш автомобиль успешно добавлен и отправлен на модерацию.\n"
            "Вы получите уведомление, когда он будет одобрен."
        )
    else:
        await callback.message.edit_text("❌ Произошла ошибка при добавлении автомобиля. Пожалуйста, попробуйте снова.")

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_add_vehicle", AddVehicle.confirming)
async def cancel_vehicle_addition(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Добавление автомобиля отменено.")
    await callback.answer()