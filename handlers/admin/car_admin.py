import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_IDS
from states.car_admin_states import CarAdmin
from repositories.car_repo import add_car

router = Router()
log = logging.getLogger(__name__)

# --- Cancel command ---
@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    """Allow user to cancel any action."""
    current_state = await state.get_state()
    if current_state is None:
        return

    log.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Действие отменено.",
        reply_markup=ReplyKeyboardRemove(),
    )

# --- Add Car FSM ---
@router.message(Command("addcar"))
async def cmd_add_car(message: Message, state: FSMContext):
    """Starts the process of adding a new car."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    await state.set_state(CarAdmin.add_car_name)
    await message.answer("Введите название автомобиля (например, 'Mercedes E-Cabrio, белый').")

@router.message(CarAdmin.add_car_name)
async def process_car_name(message: Message, state: FSMContext):
    """Processes car name and asks for the brand."""
    await state.update_data(name=message.text)
    await state.set_state(CarAdmin.add_car_brand)
    await message.answer("Теперь введите марку автомобиля (например, 'Mercedes').")


@router.message(CarAdmin.add_car_brand)
async def process_car_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await state.set_state(CarAdmin.add_car_model)
    await message.answer("Введите модель (например, 'E-Cabrio').")


@router.message(CarAdmin.add_car_model)
async def process_car_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(CarAdmin.add_car_year)
    await message.answer("Введите год выпуска.")


@router.message(CarAdmin.add_car_year)
async def process_car_year(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Год должен быть числом. Попробуйте еще раз.")
        return
    await state.update_data(year=int(message.text))
    await state.set_state(CarAdmin.add_car_color)
    await message.answer("Введите цвет.")


@router.message(CarAdmin.add_car_color)
async def process_car_color(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await state.set_state(CarAdmin.add_car_engine)
    await message.answer("Введите характеристики двигателя (например, '3.0L V6').")


@router.message(CarAdmin.add_car_engine)
async def process_car_engine(message: Message, state: FSMContext):
    await state.update_data(engine=message.text)
    await state.set_state(CarAdmin.add_car_transmission)
    await message.answer("Введите тип трансмиссии (например, 'АКПП').")


@router.message(CarAdmin.add_car_transmission)
async def process_car_transmission(message: Message, state: FSMContext):
    await state.update_data(transmission=message.text)
    await state.set_state(CarAdmin.add_car_fuel)
    await message.answer("Введите тип топлива (например, 'Бензин').")


@router.message(CarAdmin.add_car_fuel)
async def process_car_fuel(message: Message, state: FSMContext):
    await state.update_data(fuel=message.text)
    await state.set_state(CarAdmin.add_car_price)
    await message.answer("Введите цену за час аренды (только число).")


@router.message(CarAdmin.add_car_price)
async def process_car_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте еще раз.")
        return
    await state.update_data(price=price)
    await state.set_state(CarAdmin.add_car_image_url)
    await message.answer("Отправьте URL-адрес изображения автомобиля.")


@router.message(CarAdmin.add_car_image_url)
async def process_car_image_url(message: Message, state: FSMContext):
    await state.update_data(image_url=message.text)
    await state.set_state(CarAdmin.add_car_description)
    await message.answer("Введите краткое описание автомобиля.")


@router.message(CarAdmin.add_car_description)
async def process_car_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    car_data = await state.get_data()
    summary = "<b>Проверьте данные автомобиля:</b>\n\n"
    for key, value in car_data.items():
        summary += f"<b>{key.replace('_', ' ').capitalize()}:</b> {value}\n"

    await message.answer(
        summary,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Сохранить", callback_data="admin_car_confirm_add")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_car_cancel_add")]
        ])
    )
    await state.set_state(CarAdmin.add_car_confirm)


@router.callback_query(F.data == "admin_car_confirm_add", CarAdmin.add_car_confirm)
async def confirm_add_car(callback: CallbackQuery, state: FSMContext):
    car_data = await state.get_data()
    car_id = await add_car(car_data)

    if car_id:
        await callback.message.answer(f"✅ Автомобиль успешно добавлен с ID: {car_id}")
    else:
        await callback.message.answer("❌ Произошла ошибка при добавлении автомобиля.")

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "admin_car_cancel_add", CarAdmin.add_car_confirm)
async def cancel_add_car(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Добавление автомобиля отменено.")
    await callback.answer()