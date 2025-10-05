import logging
from typing import List, Dict, Any

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from repositories import vehicle_repo

router = Router()
log = logging.getLogger(__name__)


def format_car_caption(car: Dict[str, Any]) -> str:
    """Форматирует описание автомобиля для клиентской карточки."""
    price_str = f"${car.get('price_per_hour')}/час" if car.get('price_per_hour') else car.get('price_details', 'Цена по запросу')

    caption = (
        f"<b>{car.get('title')}</b>\n\n"
        f"👥 {car.get('seats')} места\n"
        f"💵 {price_str}\n\n"
        f"📝 {car.get('description')}"
    )
    return caption

def get_car_keyboard(
    cars: List[Dict[str, Any]],
    car_index: int,
    photo_index: int
) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для карусели."""
    total_cars = len(cars)
    current_car = cars[car_index]
    total_photos = len(current_car.get('photo_file_ids', []))

    nav_buttons = []

    # Навигация по фотографиям
    if total_photos > 1:
        prev_photo_idx = (photo_index - 1 + total_photos) % total_photos
        next_photo_idx = (photo_index + 1) % total_photos
        nav_buttons.extend([
            InlineKeyboardButton(text="◀️ Фото", callback_data=f"photo_{car_index}_{prev_photo_idx}"),
            InlineKeyboardButton(text=f"{photo_index + 1}/{total_photos}", callback_data="noop"),
            InlineKeyboardButton(text="Фото ▶️", callback_data=f"photo_{car_index}_{next_photo_idx}"),
        ])

    # Навигация по автомобилям
    if total_cars > 1:
        prev_car_idx = (car_index - 1 + total_cars) % total_cars
        next_car_idx = (car_index + 1) % total_cars
        nav_buttons.append(
            InlineKeyboardButton(text="<< Пред.", callback_data=f"car_nav_{prev_car_idx}")
        )
        nav_buttons.append(
            InlineKeyboardButton(text="След. >>", callback_data=f"car_nav_{next_car_idx}")
        )

    keyboard = [
        nav_buttons,
        [InlineKeyboardButton(text="📞 Связаться для заказа", url=f"tg://user?id={current_car.get('provider_tg_id')}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "browse_cars")
async def show_cars_handler(callback: CallbackQuery, state: FSMContext):
    """Отображает карусель опубликованных автомобилей."""
    await state.clear()
    cars = await vehicle_repo.get_published_vehicles()
    if not cars:
        await callback.message.answer("К сожалению, на данный момент нет доступных автомобилей.")
        await callback.answer()
        return

    await state.update_data(cars=cars)
    car = cars[0]
    photo_index = 0

    caption = format_car_caption(car)
    keyboard = get_car_keyboard(cars, 0, photo_index)

    await callback.message.answer_photo(
        photo=car["photo_file_ids"][photo_index],
        caption=caption,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

async def update_car_view(callback: CallbackQuery, state: FSMContext, car_index: int, photo_index: int):
    """Обновляет сообщение с карточкой автомобиля."""
    data = await state.get_data()
    cars = data.get("cars", [])
    car = cars[car_index]

    caption = format_car_caption(car)
    keyboard = get_car_keyboard(cars, car_index, photo_index)
    media = InputMediaPhoto(media=car["photo_file_ids"][photo_index], caption=caption, parse_mode="HTML")

    await callback.message.edit_media(media=media, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("car_nav_"))
async def car_navigation_handler(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает навигацию между автомобилями."""
    car_index = int(callback.data.split("_")[-1])
    await update_car_view(callback, state, car_index, photo_index=0)

@router.callback_query(F.data.startswith("photo_"))
async def photo_navigation_handler(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает навигацию между фотографиями."""
    _, car_index_str, photo_index_str = callback.data.split("_")
    await update_car_view(callback, state, int(car_index_str), int(photo_index_str))

@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    """Пустой обработчик для кнопок-счетчиков."""
    await callback.answer()