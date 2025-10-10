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

# ← добавили работу со справочниками и ценами
from data_loader import load_locations
from pricing import quote_price

router = Router()

# ───────────────── Справочники из CSV ─────────────────
# читаем один раз при импорте модуля
_LOCS = load_locations()
# списки вида: [("id","name"), ...]
AIRPORTS: list[tuple[str, str]] = _LOCS.get("airport", [])
HOTELS:   list[tuple[str, str]] = _LOCS.get("hotel", [])

# Быстрые словари "имя → id" (чтобы по названию находить id)
# Быстрые словари "имя → id" (по CSV), чтобы по названию найти id
NAME2AIRPORT = {name: _id for _id, name in AIRPORTS}
NAME2HOTEL   = {name: _id for _id, name in HOTELS}

# Набор возможных ключей, где в dict может лежать «человеческое» название
NAME_KEYS = ["name", "text", "title", "label", "value", "display", "full", "place"]

def resolve_place(name: str) -> tuple[str, str | None]:
    """
    По названию вернуть (kind, id), если знаем из справочника;
    иначе угадать по ключевым словам.
    """
    if name in NAME2AIRPORT:
        return "airport", NAME2AIRPORT[name]
    if name in NAME2HOTEL:
        return "hotel", NAME2HOTEL[name]
    low = name.lower()
    if "airport" in low or "аэропорт" in low:
        return "airport", None
    if "hotel" in low or "отель" in low or "iberostar" in low:
        return "hotel", None
    return "city", None

def norm_place(val) -> tuple[str, str, str | None]:
    """
    Принимает:
      - dict (с любым из ключей NAME_KEYS + optional kind/id/type/key/code)
      - list/tuple вида (id, name) или (name,) или (name, id)
      - простую строку
    Возвращает: (name, kind, id). kind/id при отсутствии выводим из CSV/эвристики.
    """
    name = ""
    kind = None
    _id  = None

    # dict
    if isinstance(val, dict):
        for k in NAME_KEYS:
            if val.get(k):
                name = str(val[k]).strip()
                break
        if not name:
            name = str(val).strip()
        kind = val.get("kind") or val.get("type")
        _id  = val.get("id")   or val.get("key")  or val.get("code")

    # list / tuple
    elif isinstance(val, (list, tuple)):
        if len(val) >= 2:
            a, b = str(val[0]), str(val[1])
            # пытаемся понять, что id, а что имя
            if a in NAME2AIRPORT or a in NAME2HOTEL:
                _id, name = a, b
            elif b in NAME2AIRPORT or b in NAME2HOTEL:
                _id, name = b, a
            else:
                _id, name = a, b  # по умолчанию считаем (id, name)
        elif len(val) == 1:
            name = str(val[0]).strip()
        else:
            name = ""

    # простая строка
    else:
        name = str(val).strip()

    # если нет kind/id — определяем по справочникам/эвристике
    if not kind:
        kind, resolved_id = resolve_place(name)
        _id = _id or resolved_id

    return name, kind, _id



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


# ───────────────── ВХОД В СЦЕНАРИЙ ─────────────────

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


# ───────────────── PICKUP ─────────────────

@router.callback_query(TaxiOrder.pickup, F.data.startswith("choose:pickup"))
async def choose_pickup_kind(callback: CallbackQuery, state: FSMContext):
    _, _, kind = callback.data.split(":")  # airport | hotel
    if kind == "airport":
        await callback.message.edit_text("🛫 Выберите аэропорт:", reply_markup=kb_from_list("pickupA", AIRPORTS))
    else:
        await callback.message.edit_text("🏨 Выберите отель:", reply_markup=kb_from_list("pickupH", HOTELS))

@router.callback_query(TaxiOrder.pickup, F.data.startswith("pickupA:"))
async def pickup_airport(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    if idx < 0 or idx >= len(AIRPORTS):
        return await callback.answer("Неверный выбор", show_alert=True)
    _id, name = AIRPORTS[idx]  # << вот тут берём (id, name)
    await state.update_data(pickup={"kind": "airport", "id": _id, "i": idx, "name": name})
    await callback.message.edit_text("📍 Куда едем? Выберите отель:", reply_markup=kb_from_list("dropH", HOTELS))
    await state.set_state(TaxiOrder.dropoff)

@router.callback_query(TaxiOrder.pickup, F.data.startswith("pickupH:"))
async def pickup_hotel(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    if idx < 0 or idx >= len(HOTELS):
        return await callback.answer("Неверный выбор", show_alert=True)
    _id, name = HOTELS[idx]
    await state.update_data(pickup={"kind": "hotel", "id": _id, "i": idx, "name": name})
    await callback.message.edit_text("📍 Куда едем? Выберите аэропорт:", reply_markup=kb_from_list("dropA", AIRPORTS))
    await state.set_state(TaxiOrder.dropoff)


# ───────────────── DROPOFF ─────────────────

@router.callback_query(TaxiOrder.dropoff, F.data.startswith("dropA:"))
async def drop_to_airport(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    if idx < 0 or idx >= len(AIRPORTS):
        return await callback.answer("Неверный выбор", show_alert=True)
    _id, name = AIRPORTS[idx]
    await state.update_data(dropoff={"kind": "airport", "id": _id, "i": idx, "name": name})
    await callback.message.edit_text("⏰ Во сколько подать автомобиль?", reply_markup=kb_time())
    await state.set_state(TaxiOrder.when)

@router.callback_query(TaxiOrder.dropoff, F.data.startswith("dropH:"))
async def drop_to_hotel(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    if idx < 0 or idx >= len(HOTELS):
        return await callback.answer("Неверный выбор", show_alert=True)
    _id, name = HOTELS[idx]
    await state.update_data(dropoff={"kind": "hotel", "id": _id, "i": idx, "name": name})
    await callback.message.edit_text("⏰ Во сколько подать автомобиль?", reply_markup=kb_time())
    await state.set_state(TaxiOrder.when)


# ───────────────── WHEN ─────────────────

@router.callback_query(TaxiOrder.when, F.data.startswith("time:"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    _, hhmm = callback.data.split(":", 1)  # "now" или "HH:MM"
    await state.update_data(when=hhmm)
    data = await state.get_data()

    # считаем цену сразу для показа в карточке
    try:
        price, payload = quote_price(
            service="taxi",
            from_kind=data['pickup']['kind'], from_id=data['pickup']['id'],
            to_kind=data['dropoff']['kind'], to_id=data['dropoff']['id'],
            when_hhmm=hhmm,
            options=data.get("options", {}),
        )
        # сохраним, если захочешь не пересчитывать на подтверждении
        await state.update_data(price_quote=price, price_payload=payload)
    except Exception:
        await callback.message.answer("❗ Ошибка при расчёте цены. Попробуйте ещё раз.")
        return

    text = (
        "📋 Проверьте заказ:\n"
        f"• Откуда: {data['pickup']['name']}\n"
        f"• Куда: {data['dropoff']['name']}\n"
        f"• Время: {'сейчас' if hhmm=='now' else hhmm}\n"
        f"• Пассажиры: 1\n"
        f"💵 Цена: {price} USD\n\n"
        f"Подтвердить?"
    )
    await callback.message.edit_text(text, reply_markup=kb_confirm())
    await state.set_state(TaxiOrder.confirm)



# ───────────────── CONFIRM ─────────────────
import logging, html, re, json
log = logging.getLogger("taxi_flow")


# Ловим и старое, и новое callback_data
@router.callback_query(F.data.in_({"confirm_order", "confirm:yes"}))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # чтобы «крутилка» остановилась
    data = await state.get_data()
    # временная диагностика: покажем форму pickup/dropoff
    try:

        dbg = {
            "pickup": data.get("pickup"),
            "dropoff": data.get("dropoff"),
            "selected_date": data.get("selected_date"),
            "selected_hour": data.get("selected_hour"),
            "datetime": str(data.get("datetime")),
        }
        # показ в чат (схлопываем до 500 символов, чтобы не заспамить)
        js = json.dumps(dbg, ensure_ascii=False, default=str)
        if len(js) > 500:
            js = js[:500] + "…"
        await callback.message.answer(f"<b>DEBUG state</b>\n<code>{html.escape(js)}</code>", parse_mode="HTML")
    except Exception:
        pass

    log.info("Confirm pressed. state=%s keys=%s", await state.get_state(), list(data.keys()))

    # --- Унифицированный разбор pickup/dropoff из state ---
    def pick_time(d: dict) -> str | None:
        # 1) если есть 'datetime' — вытащим "HH:MM"
        if d.get("datetime"):
            s = str(d["datetime"])
            m = re.search(r"(\d{1,2}:\d{2})", s)
            if m:
                hh, mm = m.group(1).split(":")
                return f"{int(hh):02d}:{int(mm):02d}"

        # 2) selected_hour: может быть "14" или "14:15"
        if d.get("selected_hour") is not None:
            sh = str(d["selected_hour"])
            if ":" in sh:
                hh, mm = sh.split(":", 1)
                mm = (mm + "00")[:2]  # подстрахуем минуту
                return f"{int(hh):02d}:{int(mm):02d}"
            else:
                return f"{int(sh):02d}:00"

        # 3) наш новый ключ 'when' ("now" или "HH:MM")
        if d.get("when"):
            w = str(d["when"])
            if w == "now":
                return w
            if ":" in w:
                hh, mm = w.split(":", 1)
                mm = (mm + "00")[:2]
                return f"{int(hh):02d}:{int(mm):02d}"
            return f"{int(w):02d}:00"

        return None

    def norm_place(val) -> tuple[str, str, str | None]:
        """
        На вход либо dict {"name":..,"kind":..,"id":..},
        либо просто строка с названием.
        Возвращаем (name, kind, id)
        """
        if isinstance(val, dict):
            name = val.get("name") or val.get("text") or ""
            kind = val.get("kind")
            _id  = val.get("id")
        else:
            name = str(val)
            kind = None
            _id  = None
        # если нет kind/id — резолвим по справочнику/эвристике
        if not kind:
            kind, resolved_id = resolve_place(name)
            _id = _id or resolved_id
        return name, kind, _id

    # достаём значения в обоих форматах стейта
    pickup_val   = data.get("pickup")   or data.get("from_text") or data.get("from_place")
    dropoff_val  = data.get("dropoff")  or data.get("to_text")   or data.get("to_place")
    when_hhmm    = pick_time(data)

    if not pickup_val or not dropoff_val:
        await callback.message.answer(
            "❗ Не удалось собрать маршрут из состояния.\n"
            f"<code>keys={html.escape(str(list(data.keys())))}</code>",
            parse_mode="HTML"
        )
        return

    pickup_name, from_kind, from_id = norm_place(pickup_val)
    drop_name,  to_kind,   to_id    = norm_place(dropoff_val)

    # --- Расчёт цены по CSV (fallback сработает по kind->kind, если id нет) ---
    try:
        price, payload = quote_price(
            service="taxi",
            from_kind=from_kind, from_id=from_id,
            to_kind=to_kind,     to_id=to_id,
            when_hhmm=when_hhmm,
            options=data.get("options", {}),
        )
    except Exception:
        log.exception("quote_price failed")
        await callback.message.answer("❗ Ошибка при расчёте цены. Попробуйте ещё раз.")
        return

    # --- Запись заказа ---
    try:
        order_id = await create_order({
            "client_tg_id": callback.from_user.id,
            "lang": getattr(callback.from_user, "language_code", "ru"),
            "service": data.get("service"),
            "pickup_text": pickup_name,
            "dropoff_text": drop_name,
            "when_dt": None,  # MVP: hh:mm храним в options
            "pax": int(data.get("pax") or 1),
            "options": {"time": when_hhmm} | (data.get("options") or {}),
            "price_quote": price,
            "price_payload": payload,
        })
    except Exception:
        log.exception("create_order failed")
        await callback.message.answer("❗ Не удалось сохранить заказ. Попробуйте ещё раз.")
        return

    await callback.message.edit_text(f"✅ Заказ #{order_id} принят. Ожидайте назначения водителя.")

    # (опционально) админ-чат
    if ADMIN_CHAT_ID:
        try:
            await callback.bot.send_message(
                ADMIN_CHAT_ID,
                "🆕 Новый заказ #{oid}\n"
                "Откуда: {fr}\nКуда: {to}\nВремя: {tm}\nЦена: {pr} USD".format(
                    oid=order_id, fr=pickup_name, to=drop_name, tm=(when_hhmm or "now"), pr=price
                )
            )
        except Exception:
            pass

    await state.clear()





# ───────────────── НАЗАД ─────────────────

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    cur = await state.get_state()
    if cur == TaxiOrder.confirm:
        await callback.message.edit_text("⏰ Во сколько подать автомобиль?", reply_markup=kb_time())
        await state.set_state(TaxiOrder.when)
    elif cur == TaxiOrder.when:
        data = await state.get_data()
        if data.get("pickup", {}).get("kind") == "airport":
            await callback.message.edit_text("📍 Куда едем? Выберите отель:", reply_markup=kb_from_list("dropH", HOTELS))
        else:
            await callback.message.edit_text("📍 Куда едем? Выберите аэропорт:", reply_markup=kb_from_list("dropA", AIRPORTS))
        await state.set_state(TaxiOrder.dropoff)
    elif cur == TaxiOrder.dropoff:
        await callback.message.edit_text(
            "🛫 Откуда едем? Выберите аэропорт или отель:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛫 Аэропорт", callback_data="choose:pickup:airport")],
                [InlineKeyboardButton(text="🏨 Отель",   callback_data="choose:pickup:hotel")],
            ])
        )
        await state.set_state(TaxiOrder.pickup)
    else:
        await callback.answer()
# DEBUG: ловим все непринятые коллбеки и печатаем их


import html

@router.callback_query()
async def _debug_unhandled(callback: CallbackQuery, state: FSMContext):
    cur = await state.get_state()
    # если мы сюда попали, значит ни один хэндлер выше не подошёл
    txt = (
        f"⚠️ <b>Unhandled callback</b>\n"
        f"data=<code>{html.escape(callback.data)}</code>\n"
        f"state=<code>{cur}</code>"
    )
    try:
        await callback.answer()  # чтобы крутилка не висела
        await callback.message.answer(txt, parse_mode="HTML")
    except Exception:
        pass
