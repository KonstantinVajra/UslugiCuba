import logging
from typing import Dict, Any
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from config import ADMIN_IDS
from repositories import vehicle_repo, user_repo

router = Router()
log = logging.getLogger(__name__)

def get_moderation_keyboard(vehicle_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для модерации."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"mod_approve_{vehicle_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"mod_decline_{vehicle_id}")
        ],
        [InlineKeyboardButton(text="➡️ Следующий", callback_data="mod_next")]
    ])

def format_moderation_caption(car: Dict[str, Any]) -> str:
    """Форматирует описание автомобиля для карточки модерации."""
    caption = (
        f"<b>Заявка на модерацию</b>\n\n"
        f"<b>Авто:</b> {car.get('make')} {car.get('model')} ({car.get('year')})\n"
        f"<b>Владелец:</b> {car.get('provider_name', 'N/A')}\n"
        f"<b>Цена:</b> ${car.get('price', 0):.2f}/час\n\n"
        f"<b>Описание:</b>\n{car.get('description', 'Нет описания.')}"
    )
    return caption

@router.message(Command("moderate"))
async def cmd_moderate(message: Message, state: FSMContext):
    """Начинает сессию модерации автомобилей."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    await state.clear()
    vehicles_to_moderate = await vehicle_repo.get_vehicles_for_moderation()

    if not vehicles_to_moderate:
        await message.answer("Нет автомобилей, ожидающих модерации.")
        return

    await state.update_data(mod_vehicles=vehicles_to_moderate, mod_index=0)

    car = vehicles_to_moderate[0]
    caption = format_moderation_caption(car)
    keyboard = get_moderation_keyboard(car['id'])

    await message.answer_photo(photo=car["photo_url"], caption=caption, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("mod_"))
async def process_moderation_action(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обрабатывает действия модератора: одобрение, отклонение, переход к следующему."""
    action, vehicle_id_str = callback.data.split("_", 1)

    if action in ["approve", "decline"]:
        vehicle_id = int(vehicle_id_str)
        is_approved = (action == "approve")

        success = await vehicle_repo.update_vehicle_status(vehicle_id, is_approved)

        if success:
            status_text = "одобрен" if is_approved else "отклонен"
            await callback.message.edit_caption(
                caption=f"{callback.message.caption}\n\n<b>Статус: {status_text.upper()}</b>",
                reply_markup=None,
                parse_mode="HTML"
            )

            # Уведомляем провайдера
            vehicle = await vehicle_repo.get_vehicle_by_id(vehicle_id)
            provider_user = await user_repo.get_user_by_id(vehicle['provider_id'])
            if provider_user:
                try:
                    await bot.send_message(
                        provider_user['tg_id'],
                        f"Ваш автомобиль '{vehicle.get('make')} {vehicle.get('model')}' был {status_text} модератором."
                    )
                except Exception as e:
                    log.error("Failed to send moderation notification to provider %s: %s", provider_user['tg_id'], e)
        else:
            await callback.answer("Не удалось обновить статус.", show_alert=True)

    # Показываем следующий автомобиль
    data = await state.get_data()
    vehicles = data.get("mod_vehicles", [])
    current_index = data.get("mod_index", 0)
    next_index = current_index + 1

    await state.update_data(mod_index=next_index)

    if next_index < len(vehicles):
        car = vehicles[next_index]
        caption = format_moderation_caption(car)
        keyboard = get_moderation_keyboard(car['id'])
        await callback.message.answer_photo(photo=car["photo_url"], caption=caption, reply_markup=keyboard, parse_mode="HTML")
    else:
        await callback.message.answer("Автомобили для модерации закончились.")
        await state.clear()

    await callback.answer()