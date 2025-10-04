import os
import csv
import re
import logging
from functools import lru_cache
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from keyboards.client import (
    date_selection_keyboard,
    hour_selection_keyboard,
    minute_selection_keyboard,
    service_inline_keyboard,
)
from keyboards.locations import (
    airport_list_keyboard,
    dropoff_category_keyboard,
    hotel_list_keyboard,
    pickup_category_keyboard,
    restaurant_list_keyboard,
    get_locations_by_kind,
)
from pricing import quote_price
from states.client_states import OrderServiceState
from repo.orders import create_order  # Импортируем функцию для работы с БД

router = Router()

# --- Вспомогательные функции для работы с локациями ---

@lru_cache()
def get_location_by_id(location_id: str) -> dict | None:
    """Находит локацию по ID в кэшированном списке."""
    all_locations = get_locations_by_kind()
    for kind in all_locations:
        for loc in all_locations[kind]:
            if loc["id"] == location_id:
                loc_with_kind = loc.copy()
                loc_with_kind['kind'] = kind
                return loc_with_kind
    return None

def to_place_dict(kind: str, _id: str, name: str) -> dict:
    """Единый формат хранения точки в state."""
    return {"kind": kind or "", "id": _id or "", "name": name or ""}

# === Команды /start и /order ===

@router.message(F.text.in_({"/start", "/order"}))
async def start_order(message: Message, state: FSMContext, _: dict):
    await message.answer(_("start_msg"))
    await message.answer(_("choose_service"), reply_markup=service_inline_keyboard(_))
    await state.set_state(OrderServiceState.choosing_service)

@router.callback_query(F.data.startswith("service_"))
async def handle_service_choice(callback: CallbackQuery, state: FSMContext, _: dict):
    service_map = {
        "service_taxi": _("Taxi"),
        "service_retro": _("Retro car"),
        "service_guide": _("Guide"),
        "service_photographer": _("Photographer"),
    }
    selected_service = service_map.get(callback.data, "Unknown Service")
    await state.update_data(service=selected_service)
    await callback.message.edit_text(_("enter_pickup"), reply_markup=pickup_category_keyboard())
    await state.set_state(OrderServiceState.entering_pickup)
    await callback.answer()

# === Выбор категории локации ===

@router.callback_query(F.data.endswith("_category_hotel"))
async def handle_hotel_category(callback: CallbackQuery, _: dict):
    prefix = "pickup" if callback.data.startswith("pickup") else "dropoff"
    await callback.message.edit_text("🏨 Выберите отель:", reply_markup=hotel_list_keyboard(prefix))
    await callback.answer()

@router.callback_query(F.data.endswith("_category_restaurant"))
async def handle_restaurant_category(callback: CallbackQuery, _: dict):
    prefix = "pickup" if callback.data.startswith("pickup") else "dropoff"
    await callback.message.edit_text("🍽 Выберите ресторан:", reply_markup=restaurant_list_keyboard(prefix))
    await callback.answer()

@router.callback_query(F.data.endswith("_category_airport"))
async def handle_airport_category(callback: CallbackQuery, _: dict):
    prefix = "pickup" if callback.data.startswith("pickup") else "dropoff"
    text = "🛫 Выберите аэропорт отправления:" if prefix == "pickup" else "🛬 Выберите аэропорт назначения:"
    await callback.message.edit_text(text, reply_markup=airport_list_keyboard(prefix))
    await callback.answer()

# === ОБЩИЙ обработчик выбора локации ===

@router.callback_query(F.data.regexp(r"^(pickup|dropoff)_(hotel|restaurant|airport)_(.+)$"))
async def handle_location_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    match = re.match(r"^(pickup|dropoff)_(hotel|restaurant|airport)_(.+)$", callback.data)
    if not match:
        await callback.answer("Ошибка: неверные данные.", show_alert=True)
        return

    action, kind, location_id = match.groups()
    location = get_location_by_id(location_id)
    if not location:
        await callback.answer("Ошибка: локация не найдена!", show_alert=True)
        return

    place_data = to_place_dict(location['kind'], location['id'], location['name'])
    await state.update_data({action: place_data})

    await callback.message.edit_reply_markup(reply_markup=None)

    if action == "pickup":
        await callback.message.answer(f"✅ {_('pickup_chosen')}: {location['name']}")
        await callback.message.answer(_("dropoff_msg"), reply_markup=dropoff_category_keyboard())
        await state.set_state(OrderServiceState.entering_dropoff)
    else: # dropoff
        await callback.message.answer(f"✅ {_('dropoff_chosen')}: {location['name']}")
        await callback.message.answer(_("choose_date"), reply_markup=date_selection_keyboard(_))
        await state.set_state(OrderServiceState.entering_date)

    await callback.answer()

# === Выбор даты и времени ===

@router.callback_query(F.data.startswith("date_"), OrderServiceState.entering_date)
async def handle_date_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    date = callback.data.split("_", 1)[1]
    await state.update_data(selected_date=date)
    await callback.message.edit_text(f"{_('chosen_date')}: {date}")
    await callback.message.answer(_("choose_hour"), reply_markup=hour_selection_keyboard())
    await state.set_state(OrderServiceState.entering_hour)
    await callback.answer()

@router.callback_query(F.data.startswith("hour_"), OrderServiceState.entering_hour)
async def handle_hour_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    hour = callback.data.split("_", 1)[1]
    await state.update_data(selected_hour=hour)
    await callback.message.edit_text(f"{_('chosen_hour')}: {hour}")
    await callback.message.answer(_("choose_minute"), reply_markup=minute_selection_keyboard())
    await state.set_state(OrderServiceState.entering_minute)
    await callback.answer()

# === Финальное подтверждение заказа ===

@router.callback_query(F.data.startswith("minute_"), OrderServiceState.entering_minute)
async def handle_minute_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    minute = callback.data.split("_", 1)[1]
    data = await state.get_data()

    date, hour = data.get("selected_date"), data.get("selected_hour")
    service = data.get("service", "Taxi")
    pickup_data, dropoff_data = data.get("pickup", {}), data.get("dropoff", {})
    pickup_name, dropoff_name = pickup_data.get("name", "N/A"), dropoff_data.get("name", "N/A")
    from_kind, from_id = pickup_data.get("kind", ""), pickup_data.get("id", "")
    to_kind, to_id = dropoff_data.get("kind", ""), dropoff_data.get("id", "")

    datetime_str = f"{date} {hour}:{minute}"
    await state.update_data(datetime=datetime_str)

    price_line = "💵 Цена: —\n"
    try:
        price, payload = quote_price(
            service="taxi", from_kind=from_kind, from_id=from_id,
            to_kind=to_kind, to_id=to_id, when_hhmm=f"{hour}:{minute}"
        )
        await state.update_data(price_quote=price, price_payload=payload)
        price_line = f"💵 Цена: {price} USD\n"
    except Exception as e:
        logging.error(f"Price quote error: {e}")

    summary = (
        f"📋 {_('order_summary')}:\n\n"
        f"🛎️ {_('service')}: {service}\n"
        f"📍 {_('from')}: {pickup_name}\n"
        f"📍 {_('to')}: {dropoff_name}\n"
        f"📅 {_('date')}: {date}\n"
        f"⏰ {_('time')}: {hour}:{minute}\n"
        f"{price_line}\n"
        f"{_('confirm_prompt')}"
    )
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ " + _("confirm_order_btn"), callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ " + _("cancel"), callback_data="cancel_order")]
    ])

    await callback.message.edit_text(summary, reply_markup=confirm_kb)
    await state.set_state(OrderServiceState.confirming_order)
    await callback.answer()

# === Обработка подтверждения/отмены ===

@router.callback_query(F.data == "confirm_order", OrderServiceState.confirming_order)
async def handle_confirm_order(callback: CallbackQuery, state: FSMContext, _: dict):
    data = await state.get_data()

    pickup = data.get('pickup', {})
    dropoff = data.get('dropoff', {})

    order_details = {
        "client_tg_id": callback.from_user.id,
        "lang": callback.from_user.language_code,
        "pickup_text": pickup.get("name", ""),
        "dropoff_text": dropoff.get("name", ""),
        "when_dt": data.get("datetime"),
        "price_quote": data.get("price_quote"),
        "price_payload": data.get("price_payload", {}),
    }

    try:
        order_id = await create_order(order_details)
        confirmation_text = _("order_confirmed_msg").format(order_id=order_id)
        await callback.message.edit_text(confirmation_text, reply_markup=None)
    except Exception as e:
        logging.error(f"Failed to create order: {e}")
        await callback.message.edit_text(_("order_failed_msg"), reply_markup=None)

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_order", OrderServiceState.confirming_order)
async def handle_cancel_order(callback: CallbackQuery, state: FSMContext, _: dict):
    await state.clear()
    await callback.message.edit_text(_("order_cancelled_msg"))
    await callback.answer()