# handlers/client/taxi_flow.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from config import HOURS_FROM, HOURS_TO, ADMIN_CHAT_ID
from middlewares.i18n import _
from repo.orders import create_order
from data_loader import load_locations
from pricing import quote_price
import logging
import html
import re
import json
from datetime import datetime

router = Router()
log = logging.getLogger("taxi_flow")

# --- Helpers from service_selection.py to keep this module independent ---
def _norm(s: str) -> str:
    return re.sub(r"[^\w]+", "", (s or "")).casefold()

_LOCS = load_locations()
AIRPORTS: list[tuple[str, str]] = _LOCS.get("airport", [])
HOTELS:   list[tuple[str, str]] = _LOCS.get("hotel", [])
NAME2AIRPORT = {name: _id for _id, name in AIRPORTS}
NAME2HOTEL   = {name: _id for _id, name in HOTELS}

def name_to_kind_id(display_name: str, fallback_kind: str) -> tuple[str, str]:
    from handlers.client.service_selection import _loc_by_name
    idx = _loc_by_name()
    key = _norm(display_name)
    if key in idx:
        kind, _id, _ = idx[key]
        return (kind or fallback_kind), _id
    return fallback_kind, ""

def to_place_dict(kind: str, _id: str, name: str) -> dict:
    return {"kind": kind or "", "id": _id or "", "name": name or ""}

def ensure_place(value, fallback_kind: str = "") -> dict:
    if isinstance(value, dict) and "kind" in value and "name" in value:
        return value
    name = ""
    if isinstance(value, dict):
        name = value.get("name", "")
    elif isinstance(value, str):
        name = value

    k, i = name_to_kind_id(name, fallback_kind)
    return to_place_dict(k, i, name)

# --- End of Helpers ---

def kb_from_list(prefix: str, items: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=name, callback_data=f"{prefix}:{i}")]
        for i, (_id, name) in enumerate(items)
    ]
    rows.append([InlineKeyboardButton(text="← Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_time() -> InlineKeyboardMarkup:
    rows = []
    for h in range(HOURS_FROM, HOURS_TO + 1):
        row = []
        for m in (0, 15, 30, 45):
            row.append(InlineKeyboardButton(text=f"{h:02d}:{m:02d}", callback_data=f"time:{h:02d}:{m:02d}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⏱ Сейчас", callback_data="time:now")])
    rows.append([InlineKeyboardButton(text="← Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm:yes")],
        [InlineKeyboardButton(text="← Назад", callback_data="back")]
    ])


class TaxiOrder(StatesGroup):
    pickup = State()
    dropoff = State()
    when = State()
    confirm = State()


@router.message(Command("taxi"))
async def cmd_taxi(message: Message, state: FSMContext, _):
    await state.clear()
    await message.answer(
        "🛫 Откуда едем? Выберите аэропорт или отель:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛫 Аэропорт", callback_data="choose:pickup:airport")],
            [InlineKeyboardButton(text="🏨 Отель",   callback_data="choose:pickup:hotel")],
        ])
    )
    await state.set_state(TaxiOrder.pickup)

@router.callback_query(F.data == "svc:taxi")
async def from_services(callback: CallbackQuery, state: FSMContext, _):
    await state.clear()
    await callback.message.edit_text(
        "🛫 Откуда едем? Выберите аэропорт или отель:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛫 Аэропорт", callback_data="choose:pickup:airport")],
            [InlineKeyboardButton(text="🏨 Отель",   callback_data="choose:pickup:hotel")],
        ])
    )
    await state.set_state(TaxiOrder.pickup)

@router.callback_query(TaxiOrder.pickup, F.data.startswith("choose:pickup"))
async def choose_pickup_kind(callback: CallbackQuery, state: FSMContext):
    _, _, kind = callback.data.split(":")
    if kind == "airport":
        await callback.message.edit_text("🛫 Выберите аэропорт:", reply_markup=kb_from_list("pickupA", AIRPORTS))
    else:
        await callback.message.edit_text("🏨 Выберите отель:", reply_markup=kb_from_list("pickupH", HOTELS))

@router.callback_query(TaxiOrder.pickup, F.data.startswith("pickupA:"))
async def pickup_airport(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    _id, name = AIRPORTS[idx]
    await state.update_data(pickup={"kind": "airport", "id": _id, "name": name})
    await callback.message.edit_text("📍 Куда едем? Выберите отель:", reply_markup=kb_from_list("dropH", HOTELS))
    await state.set_state(TaxiOrder.dropoff)

@router.callback_query(TaxiOrder.pickup, F.data.startswith("pickupH:"))
async def pickup_hotel(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    _id, name = HOTELS[idx]
    await state.update_data(pickup={"kind": "hotel", "id": _id, "name": name})
    await callback.message.edit_text("📍 Куда едем? Выберите аэропорт:", reply_markup=kb_from_list("dropA", AIRPORTS))
    await state.set_state(TaxiOrder.dropoff)

@router.callback_query(TaxiOrder.dropoff, F.data.startswith("dropA:"))
async def drop_to_airport(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    _id, name = AIRPORTS[idx]
    await state.update_data(dropoff={"kind": "airport", "id": _id, "name": name})
    await callback.message.edit_text("⏰ Во сколько подать автомобиль?", reply_markup=kb_time())
    await state.set_state(TaxiOrder.when)

@router.callback_query(TaxiOrder.dropoff, F.data.startswith("dropH:"))
async def drop_to_hotel(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    _id, name = HOTELS[idx]
    await state.update_data(dropoff={"kind": "hotel", "id": _id, "name": name})
    await callback.message.edit_text("⏰ Во сколько подать автомобиль?", reply_markup=kb_time())
    await state.set_state(TaxiOrder.when)

@router.callback_query(TaxiOrder.when, F.data.startswith("time:"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    _, hhmm = callback.data.split(":", 1)
    await state.update_data(when=hhmm)
    data = await state.get_data()

    pickup_dict = ensure_place(data.get("pickup"), "")
    dropoff_dict = ensure_place(data.get("dropoff"), "")

    try:
        price, payload = quote_price(
            service="taxi",
            from_kind=pickup_dict.get("kind"), from_id=pickup_dict.get("id"),
            to_kind=dropoff_dict.get("kind"), to_id=dropoff_dict.get("id"),
            when_hhmm=hhmm,
            options=data.get("options", {}),
        )
        await state.update_data(price_quote=price, price_payload=payload)
    except Exception:
        price, payload = None, None

    text = (
        f"📋 Проверьте заказ:\n"
        f"• Откуда: {pickup_dict.get('name')}\n"
        f"• Куда: {dropoff_dict.get('name')}\n"
        f"• Время: {'сейчас' if hhmm=='now' else hhmm}\n"
        f"• Пассажиры: 1\n"
        f"💵 Цена: {price} USD\n\n" if price is not None else ""
        f"Подтвердить?"
    )
    await callback.message.edit_text(text, reply_markup=kb_confirm())
    await state.set_state(TaxiOrder.confirm)

@router.callback_query(F.data.in_({"confirm_order", "confirm:yes"}))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    log.info("Confirm pressed. state=%s keys=%s", await state.get_state(), list(data.keys()))

    pickup_dict = ensure_place(data.get("pickup"), "")
    dropoff_dict = ensure_place(data.get("dropoff"), "")

    if not pickup_dict.get("name") or not dropoff_dict.get("name"):
        await callback.message.answer("❗ Не удалось собрать маршрут. Пожалуйста, начните заново.")
        return

    datetime_str = data.get("datetime")
    datetime_obj = None
    if isinstance(datetime_str, str):
        try:
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            log.warning(f"Could not parse datetime string: {datetime_str}")

    order_payload = {
        "client_tg_id": callback.from_user.id,
        "username": callback.from_user.username,
        "lang": getattr(callback.from_user, "language_code", "ru"),
        "service": data.get("service"),
        "pickup": pickup_dict,
        "dropoff": dropoff_dict,
        "datetime": datetime_obj,
        "pax": data.get("pax", 1),
        "price_quote": data.get("price_quote"),
        "price_payload": data.get("price_payload"),
        "options": data.get("options", {}),
    }

    try:
        order_id = await create_order(order_payload)
    except Exception as e:
        log.exception("create_order failed")
        await callback.message.answer("❗ Не удалось сохранить заказ. Попробуйте ещё раз.")
        return

    await callback.message.edit_text(f"✅ Заказ #{order_id} принят. Ожидайте назначения водителя.")

    if ADMIN_CHAT_ID:
        try:
            pickup_name = pickup_dict.get("name")
            drop_name = dropoff_dict.get("name")
            when_hhmm = order_payload.get("options", {}).get("time", "не указано")
            price = order_payload.get('price_quote', 'N/A')

            await callback.bot.send_message(
                ADMIN_CHAT_ID,
                "🆕 Новый заказ #{oid}\n"
                "Откуда: {fr}\nКуда: {to}\nВремя: {tm}\nЦена: {pr} USD".format(
                    oid=order_id, fr=pickup_name, to=drop_name, tm=when_hhmm, pr=price
                )
            )
        except Exception:
            log.exception("Failed to send admin notification")

    await state.clear()

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    # This logic might need review, but is out of scope for the current task
    cur = await state.get_state()
    if cur == TaxiOrder.confirm:
        await callback.message.edit_text("⏰ Во сколько подать автомобиль?", reply_markup=kb_time())
        await state.set_state(TaxiOrder.when)
    # ... other back steps
    else:
        await callback.answer()

@router.callback_query()
async def _debug_unhandled(callback: CallbackQuery, state: FSMContext):
    cur = await state.get_state()
    txt = (
        f"⚠️ <b>Unhandled callback in taxi_flow</b>\n"
        f"data=<code>{html.escape(str(callback.data))}</code>\n"
        f"state=<code>{cur}</code>"
    )
    try:
        await callback.answer()
        await callback.message.answer(txt, parse_mode="HTML")
    except Exception:
        pass