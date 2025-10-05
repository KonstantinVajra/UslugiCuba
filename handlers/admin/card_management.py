import logging
from typing import Dict, Any
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import ADMIN_IDS
from states.admin_states import AddVehicleAdmin
from repositories import user_repo, vehicle_repo

router = Router()
log = logging.getLogger(__name__)

# --- Фильтр для проверки прав администратора ---
class AdminFilter(F):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS

# --- Обработчик отмены ---
@router.message(Command("cancel"), AdminFilter())
@router.message(F.text.casefold() == "отмена", AdminFilter())
async def cancel_handler(message: Message, state: FSMContext):
    """Позволяет админу отменить любое действие."""
    current_state = await state.get_state()
    if current_state is None:
        return

    log.info("Admin %d cancelled state %r", message.from_user.id, current_state)
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())

# --- FSM для добавления карточки ---
@router.message(Command("addcard"), AdminFilter())
async def cmd_add_card(message: Message, state: FSMContext):
    """Начинает процесс добавления новой карточки автомобиля."""
    await state.clear()
    await state.set_state(AddVehicleAdmin.entering_provider_tg_id)
    await message.answer(
        "Шаг 1/5: Введите Telegram ID провайдера, для которого создаётся карточка.\n\n"
        "Вы можете отменить процесс в любой момент командой /cancel."
    )

@router.message(AddVehicleAdmin.entering_provider_tg_id)
async def process_provider_id(message: Message, state: FSMContext):
    """Обрабатывает ID провайдера и запрашивает фото."""
    if not message.text.isdigit():
        await message.answer("Telegram ID должен быть числом. Попробуйте еще раз.")
        return

    await state.update_data(provider_tg_id=int(message.text))
    await state.set_state(AddVehicleAdmin.uploading_photos)
    await state.update_data(photo_file_ids=[]) # Инициализируем пустой список для фото

    await message.answer(
        "Шаг 2/5: Теперь отправьте от 1 до 5 фотографий автомобиля. Когда закончите, отправьте команду /done."
    )

@router.message(AddVehicleAdmin.uploading_photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    """Обрабатывает загрузку фотографий."""
    data = await state.get_data()
    photo_file_ids = data.get("photo_file_ids", [])

    if len(photo_file_ids) >= 5:
        await message.answer("Вы уже загрузили максимальное количество фотографий (5). Отправьте /done, чтобы продолжить.")
        return

    photo_file_ids.append(message.photo[-1].file_id)
    await state.update_data(photo_file_ids=photo_file_ids)
    await message.answer(f"Фото {len(photo_file_ids)}/5 добавлено. Отправьте еще одно или /done для завершения.")

@router.message(AddVehicleAdmin.uploading_photos, Command("done"))
async def done_uploading_photos(message: Message, state: FSMContext):
    """Завершает загрузку фото и запрашивает название."""
    data = await state.get_data()
    if not data.get("photo_file_ids"):
        await message.answer("Пожалуйста, загрузите хотя бы одну фотографию.")
        return

    await state.set_state(AddVehicleAdmin.entering_title)
    await message.answer("Шаг 3/5: Отлично! Теперь введите название карточки (например, 'Chevrolet Bel Air, 1957, белый').")

@router.message(AddVehicleAdmin.entering_title)
async def process_title(message: Message, state: FSMContext):
    """Обрабатывает название и запрашивает параметры."""
    await state.update_data(title=message.text)
    await state.set_state(AddVehicleAdmin.choosing_parameters)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="2", callback_data="param_seats_2"),
            InlineKeyboardButton(text="4", callback_data="param_seats_4"),
            InlineKeyboardButton(text="5+", callback_data="param_seats_5")
        ]
    ])
    await message.answer("Шаг 4/5: Выберите количество мест.", reply_markup=keyboard)

@router.callback_query(F.data.startswith("param_seats_"))
async def process_seats(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор количества мест и запрашивает цену."""
    seats = int(callback.data.split("_")[-1])
    await state.update_data(seats=seats)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="35$", callback_data="param_price_35"),
            InlineKeyboardButton(text="50$", callback_data="param_price_50"),
            InlineKeyboardButton(text="75$", callback_data="param_price_75"),
        ],
        [InlineKeyboardButton(text="По запросу", callback_data="param_price_request")]
    ])
    await callback.message.edit_text("Теперь выберите цену за час.", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("param_price_"))
async def process_price(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор цены и запрашивает описание."""
    price_data = callback.data.split("_")[-1]
    if price_data.isdigit():
        await state.update_data(price_per_hour=int(price_data), price_details=None)
    else:
        await state.update_data(price_per_hour=None, price_details="По запросу")

    await state.set_state(AddVehicleAdmin.entering_description)
    await callback.message.edit_text("Шаг 5/5: Введите краткое описание (до 200 символов).")
    await callback.answer()

@router.message(AddVehicleAdmin.entering_description, F.text)
async def process_description_and_show_preview(message: Message, state: FSMContext):
    """Обрабатывает описание и показывает превью карточки."""
    if len(message.text) > 200:
        await message.answer("Описание слишком длинное (максимум 200 символов). Попробуйте еще раз.")
        return
    await state.update_data(description=message.text)

    data = await state.get_data()

    price_str = f"${data.get('price_per_hour')}/час" if data.get('price_per_hour') else data.get('price_details', 'Цена по запросу')

    caption = (
        f"<b>{data.get('title')}</b>\n\n"
        f"👥 {data.get('seats')} места\n"
        f"💵 {price_str}\n"
        f"📝 {data.get('description')}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить на модерацию", callback_data="finish_add_vehicle_pending_moderation")],
        [InlineKeyboardButton(text="💾 Сохранить как черновик", callback_data="finish_add_vehicle_draft")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_add_vehicle")]
    ])

    await message.answer_photo(
        photo=data['photo_file_ids'][0],
        caption=caption,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(AddVehicleAdmin.confirming_vehicle)

@router.callback_query(AddVehicleAdmin.confirming_vehicle, F.data.startswith("finish_add_vehicle_"))
async def finish_vehicle_creation(callback: CallbackQuery, state: FSMContext):
    """Завершает создание карточки, сохраняя ее с выбранным статусом."""
    action = callback.data.split("_")[-1]

    status = action  # 'draft' или 'pending_moderation'
    vehicle_data = await state.get_data()

    provider_tg_id = vehicle_data.get("provider_tg_id")
    provider = await user_repo.get_or_create_provider(provider_tg_id)

    if not provider:
        await callback.message.edit_text("❌ Ошибка: не удалось найти или создать провайдера. Проверьте Telegram ID.")
        await state.clear()
        await callback.answer()
        return

    new_vehicle = await vehicle_repo.add_vehicle(provider['id'], vehicle_data, status)

    if new_vehicle:
        await callback.message.edit_text(
            f"✅ Карточка для провайдера <b>{provider['name']}</b> (ID: {provider['id']}) успешно сохранена со статусом <b>{status}</b>."
        )
    else:
        await callback.message.edit_text("❌ Произошла ошибка при сохранении карточки в базу данных.")
    await state.clear()
    await callback.answer()

@router.callback_query(AddVehicleAdmin.confirming_vehicle, F.data == "cancel_add_vehicle")
async def cancel_from_preview(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Добавление карточки отменено.")
    await callback.answer()