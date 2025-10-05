import logging
from typing import List, Dict, Any

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from config import ADMIN_CHAT_ID
from repositories import vehicle_repo, user_repo, order_repo

router = Router()
log = logging.getLogger(__name__)

class CarBooking(StatesGroup):
    entering_comment = State()
    confirming_order = State()

# --- Helper Functions for Keyboards and Captions ---

def format_car_caption(car: Dict[str, Any], detailed: bool = False) -> str:
    """Форматирует описание автомобиля для карточки."""
    caption = f"<b>{car.get('make')} {car.get('model')} ({car.get('year')})</b>\n"
    caption += f"<i>Владелец: {car.get('provider_name', 'N/A')}</i>\n\n"

    if detailed:
        caption += (
            f"<b>Цвет:</b> {car.get('color', '-')}\n"
            f"<b>Двигатель:</b> {car.get('engine', '-')}\n"
            f"<b>Трансмиссия:</b> {car.get('transmission', '-')}\n"
            f"<b>Топливо:</b> {car.get('fuel', '-')}\n\n"
            f"<b>Описание:</b>\n{car.get('description', 'Нет описания.')}\n\n"
        )
    caption += f"<b>Цена: ${car.get('price', 0):.2f}/час</b>"
    return caption

def get_car_keyboard(cars: List[Dict[str, Any]], current_index: int) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для карусели автомобилей."""
    total_cars = len(cars)
    car_id = cars[current_index]['id']

    nav_buttons = []
    if total_cars > 1:
        prev_index = (current_index - 1 + total_cars) % total_cars
        next_index = (current_index + 1) % total_cars
        nav_buttons.extend([
            InlineKeyboardButton(text="⬅️", callback_data=f"car_nav_{prev_index}"),
            InlineKeyboardButton(text=f"{current_index + 1}/{total_cars}", callback_data="car_noop"),
            InlineKeyboardButton(text="➡️", callback_data=f"car_nav_{next_index}"),
        ])

    buttons = [
        nav_buttons,
        [InlineKeyboardButton(text="ℹ️ Подробнее", callback_data=f"car_details_{current_index}")],
        [InlineKeyboardButton(text="✅ Выбрать этот автомобиль", callback_data=f"car_select_{car_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_detailed_car_keyboard(current_index: int, car_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для детального просмотра."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к списку", callback_data=f"car_back_{current_index}")],
        [InlineKeyboardButton(text="✅ Выбрать этот автомобиль", callback_data=f"car_select_{car_id}")]
    ])

# --- Carousel and Details Handlers ---

@router.callback_query(F.data == "show_cars")
async def show_cars_handler(callback: CallbackQuery, state: FSMContext):
    """Отображает карусель одобренных автомобилей."""
    await state.clear()
    cars = await vehicle_repo.get_approved_vehicles()
    if not cars:
        await callback.message.answer("К сожалению, на данный момент нет доступных автомобилей.")
        await callback.answer()
        return

    await state.update_data(cars=cars)
    car = cars[0]
    caption = format_car_caption(car)
    keyboard = get_car_keyboard(cars, 0)

    await callback.message.answer_photo(photo=car["photo_url"], caption=caption, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("car_nav_"))
async def car_navigation_handler(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает навигацию по карусели."""
    current_index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    cars = data.get("cars", [])
    car = cars[current_index]

    caption = format_car_caption(car)
    keyboard = get_car_keyboard(cars, current_index)
    media = InputMediaPhoto(media=car["photo_url"], caption=caption, parse_mode="HTML")

    await callback.message.edit_media(media=media, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("car_details_"))
async def car_details_handler(callback: CallbackQuery, state: FSMContext):
    """Отображает подробную информацию об автомобиле."""
    current_index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    cars = data.get("cars", [])
    car = cars[current_index]

    caption = format_car_caption(car, detailed=True)
    keyboard = get_detailed_car_keyboard(current_index, car['id'])

    await callback.message.edit_caption(caption=caption, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("car_back_"))
async def car_back_handler(callback: CallbackQuery, state: FSMContext):
    """Возвращает к карусели из детального просмотра."""
    current_index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    cars = data.get("cars", [])
    car = cars[current_index]

    caption = format_car_caption(car)
    keyboard = get_car_keyboard(cars, current_index)

    await callback.message.edit_caption(caption=caption, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "car_noop")
async def car_noop_handler(callback: CallbackQuery):
    """Пустой обработчик для кнопки со счетчиком."""
    await callback.answer()

# --- Car Booking FSM ---

@router.callback_query(F.data.startswith("car_select_"))
async def select_car_handler(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс оформления заказа на автомобиль."""
    vehicle_id = int(callback.data.split("_")[-1])
    await state.update_data(vehicle_id=vehicle_id)

    await state.set_state(CarBooking.entering_comment)
    await callback.message.answer(
        "Вы выбрали автомобиль. Пожалуйста, введите комментарий к заказу (например, желаемую дату, время и место подачи).",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()

@router.message(CarBooking.entering_comment)
async def process_comment(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает комментарий и завершает заказ."""
    await state.update_data(client_comment=message.text)

    data = await state.get_data()
    vehicle_id = data.get("vehicle_id")
    vehicle = await vehicle_repo.get_vehicle_by_id(vehicle_id)
    user = await user_repo.get_or_create_user(message.from_user.id)

    order_details = {
        "client_user_id": user['id'],
        "provider_id": vehicle['provider_id'],
        "service_id": 1, # Захардкожено, т.к. услуга пока одна
        "vehicle_id": vehicle_id,
        "price": vehicle['price'],
        "client_comment": data.get("client_comment")
    }

    # Сохраняем заказ в БД
    order_id = await order_repo.create_order(order_details)
    if not order_id:
        await message.answer("Произошла ошибка при создании заказа. Пожалуйста, попробуйте снова.")
        await state.clear()
        return

    # Отправляем уведомление админу/провайдеру
    provider_user = await user_repo.get_user_by_id(vehicle['provider_id']) # Предполагая, что такая функция есть
    provider_tg_id = provider_user.get('tg_id') if provider_user else ADMIN_CHAT_ID

    notification_text = (
        f"🚘 <b>НОВАЯ ЗАЯВКА НА АВТО №{order_id}</b> 🚘\n\n"
        f"<b>Автомобиль:</b> {vehicle.get('make')} {vehicle.get('model')} ({vehicle.get('year')})\n"
        f"<b>Цена:</b> ${vehicle.get('price'):.2f}/час\n\n"
        f"<b>Комментарий клиента:</b>\n{order_details['client_comment']}\n\n"
        f"Свяжитесь с клиентом: tg://user?id={message.from_user.id}"
    )

    try:
        await bot.send_message(provider_tg_id, notification_text, parse_mode="HTML")
    except Exception as e:
        log.error("Failed to send notification to provider %s: %s", provider_tg_id, e)
        # Отправляем админу, если провайдеру не ушло
        await bot.send_message(ADMIN_CHAT_ID, f"Не удалось уведомить провайдера. {notification_text}", parse_mode="HTML")

    await message.answer(
        "✅ <b>Ваша заявка принята!</b>\n\n"
        "Владелец автомобиля скоро свяжется с вами для подтверждения деталей.\n\n"
        "Спасибо, что выбрали нас!",
        parse_mode="HTML"
    )
    await state.clear()