# handlers/client/service_selection.py
import logging
import os
import re
import csv
import json
from functools import lru_cache
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.client_states import OrderServiceState
from keyboards.client import (
    main_menu_keyboard,
    taxi_menu_keyboard,
    date_selection_keyboard,
    hour_selection_keyboard,
    minute_selection_keyboard,
)
from keyboards.locations import (
    pickup_category_keyboard, dropoff_category_keyboard,
    hotel_list_keyboard, restaurant_list_keyboard,
    HOTEL_NAMES, RESTAURANT_NAMES,
    AIRPORT_NAMES, airport_list_keyboard
)
from pricing import quote_price
from repo.orders import create_order

router = Router()
log = logging.getLogger(__name__)

# --- Вспомогательные функции для работы с локациями ---

def _norm(s: str) -> str:
    return re.sub(r"[^\w]+", "", (s or "")).casefold()

@lru_cache
def _loc_by_name() -> dict[str, tuple[str, str, str]]:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    path = os.path.join(base, "data", "locations.csv")
    idx = {}
    try:
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                nm = (row.get("name") or "").strip()
                if not nm: continue
                idx[_norm(nm)] = (row.get("kind", ""), row.get("id", ""), nm)
    except FileNotFoundError:
        log.error("locations.csv not found, location helpers will not work.")
    return idx

def name_to_kind_id(display_name: str, fallback_kind: str) -> tuple[str, str]:
    idx = _loc_by_name()
    key = _norm(display_name)
    if key in idx:
        kind, _id, _ = idx[key]
        return (kind or fallback_kind), _id
    return fallback_kind, ""

def to_place_dict(kind: str, _id: str, name: str) -> dict:
    return {"kind": kind or "", "id": _id or "", "name": name or ""}

def ensure_place(value, fallback_kind: str = "") -> dict:
    if isinstance(value, dict):
        return value
    name = str(value or "")
    k, i = name_to_kind_id(name, fallback_kind)
    return to_place_dict(k, i, name)

# --- 1. Главное меню и навигация ---

async def show_main_menu(message: Message, _: dict, edit: bool = False):
    text = _("🌴 Услуги Кубы — выберите категорию:")
    markup = main_menu_keyboard(_)
    try:
        if edit:
            await message.edit_text(text, reply_markup=markup)
        else:
            await message.answer(text, reply_markup=markup)
    except Exception as e:
        log.warning(f"Failed to edit message, sending new one: {e}")
        await message.answer(text, reply_markup=markup)

@router.message(F.text.in_({"/start", "/menu"}))
async def cmd_start(message: Message, state: FSMContext, _: dict):
    await state.clear()
    await show_main_menu(message, _, edit=False)

@router.callback_query(F.data == "back_to_main_menu")
async def cb_back_to_main_menu(callback: CallbackQuery, state: FSMContext, _: dict):
    await state.clear()
    await show_main_menu(callback.message, _, edit=True)
    await callback.answer()

@router.callback_query(F.data == "category_taxi")
async def cb_category_taxi(callback: CallbackQuery, _: dict):
    await callback.message.edit_text(
        _("Такси / Кабриолеты — выберите действие:"),
        reply_markup=taxi_menu_keyboard(_)
    )
    await callback.answer()

# --- 2. Восстановленный FSM для заказа такси ---

@router.callback_query(F.data == "taxi_quick_order")
async def cb_taxi_quick_order(callback: CallbackQuery, state: FSMContext, _: dict):
    await state.set_state(OrderServiceState.entering_pickup)
    await callback.message.edit_text(_("enter_pickup"), reply_markup=pickup_category_keyboard())
    await callback.answer()

# --- Шаги FSM ---

@router.callback_query(F.data.in_({"pickup_hotels", "pickup_restaurants", "pickup_airports"}), OrderServiceState.entering_pickup)
async def pickup_category(callback: CallbackQuery, state: FSMContext, _: dict):
    actions = {
        "pickup_hotels": ("🏨 Выберите отель:", hotel_list_keyboard("pickup")),
        "pickup_restaurants": ("🍽 Выберите ресторан:", restaurant_list_keyboard("pickup")),
        "pickup_airports": ("🛫 Выберите аэропорт отправления:", airport_list_keyboard("pickup")),
    }
    action = actions.get(callback.data)
    if action:
        await callback.message.edit_text(action[0], reply_markup=action[1])
    await callback.answer()

@router.callback_query(F.data.startswith("pickup_"), OrderServiceState.entering_pickup)
async def pickup_location_selected(callback: CallbackQuery, state: FSMContext, _: dict):
    parts = callback.data.split('_')
    loc_type, index_str = parts[1], parts[-1]

    try:
        index = int(index_str)
        if loc_type == 'hotel':
            location_name = HOTEL_NAMES[index]
            kind = "hotel"
        elif loc_type == 'rest':
            location_name = RESTAURANT_NAMES[index]
            kind = "restaurant"
        elif loc_type == 'airport':
            location_name = AIRPORT_NAMES[index]
            kind = "airport"
        else:
            return
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора", show_alert=True)
        return

    k, i = name_to_kind_id(location_name, kind)
    await state.update_data(pickup=to_place_dict(k, i, location_name))

    await callback.message.answer(f"✅ {_('pickup_chosen')}: {location_name}")
    await callback.message.edit_text(_("dropoff_msg"), reply_markup=dropoff_category_keyboard())
    await state.set_state(OrderServiceState.entering_dropoff)
    await callback.answer()

@router.callback_query(F.data.in_({"dropoff_hotels", "dropoff_restaurants", "dropoff_airports"}), OrderServiceState.entering_dropoff)
async def dropoff_category(callback: CallbackQuery, state: FSMContext, _: dict):
    actions = {
        "dropoff_hotels": ("🏨 Выберите отель:", hotel_list_keyboard("dropoff")),
        "dropoff_restaurants": ("🍽 Выберите ресторан:", restaurant_list_keyboard("dropoff")),
        "dropoff_airports": ("🛬 Выберите аэропорт назначения:", airport_list_keyboard("dropoff")),
    }
    action = actions.get(callback.data)
    if action:
        await callback.message.edit_text(action[0], reply_markup=action[1])
    await callback.answer()

@router.callback_query(F.data.startswith("dropoff_"), OrderServiceState.entering_dropoff)
async def dropoff_location_selected(callback: CallbackQuery, state: FSMContext, _: dict):
    parts = callback.data.split('_')
    loc_type, index_str = parts[1], parts[-1]

    try:
        index = int(index_str)
        if loc_type == 'hotel':
            location_name = HOTEL_NAMES[index]
            kind = "hotel"
        elif loc_type == 'rest':
            location_name = RESTAURANT_NAMES[index]
            kind = "restaurant"
        elif loc_type == 'airport':
            location_name = AIRPORT_NAMES[index]
            kind = "airport"
        else:
            return
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора", show_alert=True)
        return

    k, i = name_to_kind_id(location_name, kind)
    await state.update_data(dropoff=to_place_dict(k, i, location_name))

    await callback.message.answer(f"✅ {_('dropoff_chosen')}: {location_name}")
    await callback.message.edit_text(_("choose_date"), reply_markup=date_selection_keyboard(_))
    await state.set_state(OrderServiceState.entering_date)
    await callback.answer()

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

@router.callback_query(F.data.startswith("minute_"), OrderServiceState.entering_minute)
async def handle_minute_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    minute = callback.data.split("_", 1)[1]
    await state.update_data(minute=minute)
    data = await state.get_data()

    date, hour = data.get("selected_date"), data.get("selected_hour")
    pd, dd = ensure_place(data.get("pickup")), ensure_place(data.get("dropoff"))
    pickup_name, dropoff_name = pd.get("name", ""), dd.get("name", "")
    from_kind, from_id = pd.get("kind", ""), pd.get("id", "")
    to_kind, to_id = dd.get("kind", ""), dd.get("id", "")

    when_hhmm = f"{hour}:{minute}"
    try:
        price, payload = quote_price("taxi", from_kind, from_id, to_kind, to_id, when_hhmm, data.get("options", {}))
        await state.update_data(price_quote=price, price_payload=payload)
        price_line = f"💵 {_('price')}: {price} USD\n"
    except Exception:
        price_line = f"💵 {_('price')}: —\n"

    summary_parts = [f"📋 {_('order_summary')}:\n"]
    if data.get("selected_car"):
        summary_parts.append(f"🚘 {_('selected_car')}: {data.get('selected_car')}")
    summary_parts.extend([
        f"🛎️ {_('service')}: {_('Taxi')}",
        f"📍 {_('from')}: {pickup_name}",
        f"📍 {_('to')}: {dropoff_name}",
        f"📅 {_('date')}: {date}",
        f"⏰ {_('time')}: {when_hhmm}",
        price_line,
        _('confirm_prompt')
    ])

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ " + _("confirm_order_btn"), callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ " + _("cancel"), callback_data="cancel_order")]
    ])

    await callback.message.edit_text("\n".join(summary_parts), reply_markup=confirm_kb)
    await state.set_state(OrderServiceState.confirming_order)
    await callback.answer()

@router.callback_query(F.data == "confirm_order", OrderServiceState.confirming_order)
async def fsm_confirm_order(callback: CallbackQuery, state: FSMContext, _: dict):
    data = await state.get_data()
    pd, dd = ensure_place(data.get("pickup")), ensure_place(data.get("dropoff"))
    when_dt = f"{data.get('selected_date')} {data.get('selected_hour')}:{data.get('minute', '00')}"

    try:
        order_id = await create_order({
            "client_tg_id": callback.from_user.id,
            "client_username": callback.from_user.username,
            "lang": getattr(callback.from_user, "language_code", "ru"),
            "pickup_text": pd.get("name"),
            "dropoff_text": dd.get("name"),
            "when_dt": when_dt,
            "options": {"selected_car": data.get("selected_car")} if data.get("selected_car") else {},
            "price_quote": data.get("price_quote"),
            "price_payload": data.get("price_payload", {}),
        })
        await callback.message.edit_text(f"✅ Заказ #{order_id} принят. Ожидайте.")

        admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        if admin_chat_id:
            admin_msg = f"🔔 Новый заказ #{order_id}\n"
            if data.get("selected_car"): admin_msg += f"🚘 Авто: {data.get('selected_car')}\n"
            admin_msg += f"От: {pd.get('name')}\nДо: {dd.get('name')}\nКогда: {when_dt}"
            await callback.bot.send_message(admin_chat_id, admin_msg)

    except Exception as e:
        log.exception("Failed to create order or notify admin")
        await callback.message.edit_text("❌ Не удалось создать заказ. Попробуйте снова.")
    finally:
        await state.clear()
        await callback.answer()

@router.callback_query(F.data == "cancel_order")
async def fsm_cancel_order(callback: CallbackQuery, state: FSMContext, _: dict):
    await state.clear()
    await callback.message.edit_text("❌ Заказ отменен.")
    await show_main_menu(callback.message, _, edit=False)
    await callback.answer()