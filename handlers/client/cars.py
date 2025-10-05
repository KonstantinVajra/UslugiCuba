import logging
from typing import List, Dict, Any

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from config import ADMIN_CHAT_ID
from keyboards.client import main_keyboard
from middlewares.i18n import _
from repositories.car_repo import get_all_published_cars, get_car_by_id, create_car_order
from states.car_selection import CarOrder

router = Router()
log = logging.getLogger(__name__)

# --- Helper Functions ---

def format_car_caption(car: Dict[str, Any], detailed: bool = False) -> str:
    """Форматирует описание автомобиля для карточки."""
    caption = f"<b>{car.get('name', 'Без названия')}</b>\n\n"
    if detailed:
        caption += (
            f"Марка: {car.get('brand', '-')}\n"
            f"Модель: {car.get('model', '-')}\n"
            f"Год: {car.get('year', '-')}\n"
            f"Цвет: {car.get('color', '-')}\n"
            f"Двигатель: {car.get('engine', '-')}\n"
            f"Трансмиссия: {car.get('transmission', '-')}\n"
            f"Топливо: {car.get('fuel', '-')}\n"
            f"Описание: {car.get('description', 'Нет описания.')}\n\n"
        )
    caption += f"<b>Цена: {car.get('price', 0)} ₽/час</b>"
    return caption


def get_car_keyboard(cars: List[Dict[str, Any]], current_index: int) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для карусели автомобилей."""
    total_cars = len(cars)
    car_id = cars[current_index]['id']

    buttons = []
    nav_buttons = []

    if total_cars > 1:
        prev_index = (current_index - 1 + total_cars) % total_cars
        next_index = (current_index + 1) % total_cars
        nav_buttons.extend([
            InlineKeyboardButton(text="⬅️", callback_data=f"car_nav_{prev_index}"),
            InlineKeyboardButton(text=f"{current_index + 1}/{total_cars}", callback_data="car_noop"),
            InlineKeyboardButton(text="➡️", callback_data=f"car_nav_{next_index}"),
        ])
    buttons.append(nav_buttons)

    buttons.append([
        InlineKeyboardButton(text="ℹ️ Подробнее", callback_data=f"car_details_{current_index}"),
    ])
    buttons.append([
        InlineKeyboardButton(text="✅ Выбрать", callback_data=f"car_select_{car_id}"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Command Handler ---

@router.callback_query(F.data == "show_cars")
async def show_cars_handler(callback: CallbackQuery, state: FSMContext):
    """Отображает карусель автомобилей."""
    cars = await get_all_published_cars()
    if not cars:
        await callback.message.answer("К сожалению, на данный момент нет доступных автомобилей.")
        await callback.answer()
        return

    await state.update_data(cars=cars)

    current_index = 0
    car = cars[current_index]

    caption = format_car_caption(car)
    keyboard = get_car_keyboard(cars, current_index)

    if car.get("image_url"):
        await callback.message.answer_photo(
            photo=car["image_url"],
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            text=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()

# --- Navigation and Details Handlers ---

@router.callback_query(F.data.startswith("car_nav_"))
async def car_navigation_handler(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает навигацию по карусели."""
    try:
        current_index = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("Ошибка навигации.", show_alert=True)
        return

    data = await state.get_data()
    cars = data.get("cars", [])
    if not cars:
        await callback.message.edit_text("Нет доступных автомобилей.")
        await callback.answer()
        return

    car = cars[current_index]
    caption = format_car_caption(car)
    keyboard = get_car_keyboard(cars, current_index)

    try:
        if not car.get("image_url"):
            raise ValueError("No image for this car, fallback to edit_text")
        media = InputMediaPhoto(media=car.get("image_url"), caption=caption, parse_mode="HTML")
        await callback.message.edit_media(media=media, reply_markup=keyboard)
    except Exception as e:
        log.warning("Failed to edit media, falling back to edit_text: %s", e)
        await callback.message.edit_text(text=caption, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()


@router.callback_query(F.data == "car_noop")
async def car_noop_handler(callback: CallbackQuery):
    """Пустой обработчик для кнопки со счетчиком, чтобы она не реагировала."""
    await callback.answer()


def get_detailed_car_keyboard(cars: List[Dict[str, Any]], current_index: int) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для детального просмотра."""
    car_id = cars[current_index]['id']
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к списку", callback_data=f"car_back_{current_index}")],
        [InlineKeyboardButton(text="✅ Выбрать", callback_data=f"car_select_{car_id}")]
    ])


@router.callback_query(F.data.startswith("car_details_"))
async def car_details_handler(callback: CallbackQuery, state: FSMContext):
    """Отображает подробную информацию об автомобиле."""
    try:
        current_index = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("Ошибка получения деталей.", show_alert=True)
        return

    data = await state.get_data()
    cars = data.get("cars", [])
    if not cars:
        await callback.message.edit_text("Нет доступных автомобилей.")
        await callback.answer()
        return

    car = cars[current_index]
    caption = format_car_caption(car, detailed=True)
    keyboard = get_detailed_car_keyboard(cars, current_index)

    try:
        await callback.message.edit_caption(caption=caption, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        log.warning("Failed to edit caption, falling back to edit_text: %s", e)
        await callback.message.edit_text(text=caption, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()


@router.callback_query(F.data.startswith("car_back_"))
async def car_back_handler(callback: CallbackQuery, state: FSMContext):
    """Возвращает к карусели из детального просмотра."""
    try:
        current_index = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("Ошибка навигации.", show_alert=True)
        return

    data = await state.get_data()
    cars = data.get("cars", [])
    if not cars:
        await callback.message.edit_text("Нет доступных автомобилей.")
        await callback.answer()
        return

    car = cars[current_index]
    caption = format_car_caption(car, detailed=False)
    keyboard = get_car_keyboard(cars, current_index)

    try:
        await callback.message.edit_caption(caption=caption, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        log.warning("Failed to edit caption, falling back to edit_text: %s", e)
        await callback.message.edit_text(text=caption, reply_markup=keyboard, parse_mode="HTML")

    await callback.answer()


# --- FSM for Car Ordering ---

@router.callback_query(F.data.startswith("car_select_"))
async def select_car_handler(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс оформления заказа на автомобиль."""
    try:
        car_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("Ошибка выбора автомобиля.", show_alert=True)
        return

    await state.update_data(selected_car_id=car_id)
    await callback.message.answer("Для оформления заявки, пожалуйста, введите ваше имя.")
    await state.set_state(CarOrder.name)
    await callback.answer()


@router.message(CarOrder.name)
async def process_name_handler(message: Message, state: FSMContext):
    """Обрабатывает введенное имя и запрашивает телефон."""
    await state.update_data(name=message.text)
    await message.answer("Отлично! Теперь, пожалуйста, введите ваш номер телефона.")
    await state.set_state(CarOrder.phone)


@router.message(CarOrder.phone)
async def process_phone_handler(message: Message, state: FSMContext):
    """Обрабатывает введенный телефон и запрашивает комментарий."""
    await state.update_data(phone=message.text)
    await message.answer("Спасибо. Если у вас есть дополнительные пожелания, напишите их в комментарии. Если нет — просто пропустите этот шаг, нажав 'Пропустить'.",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data="skip_comment")]]))
    await state.set_state(CarOrder.comment)


@router.callback_query(F.data == "skip_comment", CarOrder.comment)
async def skip_comment_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Пропускает ввод комментария и завершает заказ."""
    await state.update_data(comment="-")
    await finalize_car_order(callback.message, state, bot)
    await callback.answer()


@router.message(CarOrder.comment)
async def process_comment_handler(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает комментарий и завершает заказ."""
    await state.update_data(comment=message.text)
    await finalize_car_order(message, state, bot)


async def finalize_car_order(message: Message, state: FSMContext, bot: Bot):
    """Формирует, сохраняет и отправляет заявку на автомобиль."""
    data = await state.get_data()
    car_id = data.get("selected_car_id")

    car = await get_car_by_id(car_id)
    if not car:
        await message.answer("Произошла ошибка. Выбранный автомобиль не найден. Пожалуйста, попробуйте снова.")
        await state.clear()
        return

    order_data = {
        "car_id": car_id,
        "name": data.get("name"),
        "phone": data.get("phone"),
        "comment": data.get("comment"),
        "tg_id": message.from_user.id,
    }

    # Save to DB
    order_id = await create_car_order(order_data)
    if not order_id:
        await message.answer("Не удалось сохранить вашу заявку. Пожалуйста, свяжитесь с администратором.")
        await state.clear()
        return

    # Send notification to admin
    notification_text = (
        "🚘 <b>НОВАЯ ЗАЯВКА НА АВТО</b> 🚘\n\n"
        f"<b>Автомобиль:</b> {car.get('name')}\n"
        f"<b>Цена:</b> {car.get('price')} ₽/час\n\n"
        f"<b>Имя клиента:</b> {order_data['name']}\n"
        f"<b>Телефон:</b> {order_data['phone']}\n"
        f"<b>Комментарий:</b> {order_data['comment']}\n"
        f"<b>ID заявки:</b> {order_id}"
    )

    try:
        await bot.send_message(ADMIN_CHAT_ID, notification_text, parse_mode="HTML")
    except Exception as e:
        log.error("Failed to send car order notification to admin chat %s: %s", ADMIN_CHAT_ID, e)

    # Final message to user
    await message.answer(
        "✅ <b>Ваша заявка принята!</b>\n\n"
        "Наш менеджер скоро свяжется с вами для подтверждения деталей.\n\n"
        "Спасибо, что выбрали нас!",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

    await state.clear()