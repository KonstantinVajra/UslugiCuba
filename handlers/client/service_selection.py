from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.client_states import OrderServiceState
from keyboards.client import (
    service_inline_keyboard,
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
from handlers.client.taxi_flow import TaxiOrder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pricing import quote_price            # (импорт вверху файла, если ещё нет)
from keyboards.locations import HOTEL_NAMES, RESTAURANT_NAMES, AIRPORT_NAMES

router = Router()


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
    selected_service = service_map.get(callback.data, callback.data)
    await state.update_data(service=selected_service)

    # 👉 ВАЖНО: оставляем родной поток с категориями (там есть Ресторан)
    await callback.message.answer(_("enter_pickup"), reply_markup=pickup_category_keyboard())
    await state.set_state(OrderServiceState.entering_pickup)
    await callback.answer()



# Pickup: Airport
@router.callback_query(F.data == "pickup_airports")
async def pickup_airports(callback: CallbackQuery, state: FSMContext, _: dict):
    await callback.message.edit_text("🛫 Выберите аэропорт отправления:", reply_markup=airport_list_keyboard("pickup"))
    await callback.answer()


@router.callback_query(F.data.startswith("pickup_airport_"))
async def pickup_selected_airport(callback: CallbackQuery, state: FSMContext, _: dict):
    try:
        index = int(callback.data.split("_")[-1])
        pickup_location = AIRPORT_NAMES[index]
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора аэропорта", show_alert=True)
        return

    pickup_txt = _('pickup_chosen')
    await state.update_data(pickup=pickup_location)
    await callback.message.answer(f"✅ {pickup_txt}: {pickup_location}")
    await callback.message.answer(_("dropoff_msg"), reply_markup=dropoff_category_keyboard())
    await state.set_state(OrderServiceState.entering_dropoff)
    await callback.answer()


# Dropoff: Airport
@router.callback_query(F.data == "dropoff_airports")
async def dropoff_airports(callback: CallbackQuery, state: FSMContext, _: dict):
    await callback.message.edit_text("🛬 Выберите аэропорт назначения:", reply_markup=airport_list_keyboard("dropoff"))
    await callback.answer()


@router.callback_query(F.data.startswith("dropoff_airport_"))
async def dropoff_selected_airport(callback: CallbackQuery, state: FSMContext, _: dict):
    try:
        index = int(callback.data.split("_")[-1])
        dropoff_location = AIRPORT_NAMES[index]
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора аэропорта", show_alert=True)
        return

    dropoff_txt = _('dropoff_chosen')
    await state.update_data(dropoff=dropoff_location)
    await callback.message.answer(f"✅ {dropoff_txt}: {dropoff_location}")
    await callback.message.answer(_("choose_date"), reply_markup=date_selection_keyboard(_))
    await state.set_state(OrderServiceState.entering_date)
    await callback.answer()


# Pickup: Hotel
@router.callback_query(F.data == "pickup_hotels")
async def pickup_hotels(callback: CallbackQuery, state: FSMContext, _: dict):
    await callback.message.edit_text("🏨 Выберите отель:", reply_markup=hotel_list_keyboard("pickup"))
    await callback.answer()


@router.callback_query(F.data == "pickup_restaurants")
async def pickup_restaurants(callback: CallbackQuery, state: FSMContext, _: dict):
    await callback.message.edit_text("🍽 Выберите ресторан:", reply_markup=restaurant_list_keyboard("pickup"))
    await callback.answer()


@router.callback_query(F.data.startswith("pickup_hotel_"))
async def pickup_selected_hotel(callback: CallbackQuery, state: FSMContext, _: dict):
    try:
        index = int(callback.data.split("_")[-1])
        pickup_location = HOTEL_NAMES[index]
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора отеля", show_alert=True)
        return

    pickup_txt = _('pickup_chosen')
    await state.update_data(pickup=pickup_location)
    await callback.message.answer(f"✅ {pickup_txt}: {pickup_location}")
    await callback.message.answer(_("dropoff_msg"), reply_markup=dropoff_category_keyboard())
    await state.set_state(OrderServiceState.entering_dropoff)
    await callback.answer()


@router.callback_query(F.data.startswith("pickup_rest_"))
async def pickup_selected_restaurant(callback: CallbackQuery, state: FSMContext, _: dict):
    try:
        index = int(callback.data.split("_")[-1])
        pickup_location = RESTAURANT_NAMES[index]
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора ресторана", show_alert=True)
        return

    pickup_txt = _('pickup_chosen')
    await state.update_data(pickup=pickup_location)
    await callback.message.answer(f"✅ {pickup_txt}: {pickup_location}")
    await callback.message.answer(_("dropoff_msg"), reply_markup=dropoff_category_keyboard())
    await state.set_state(OrderServiceState.entering_dropoff)
    await callback.answer()


# Dropoff: Hotel
@router.callback_query(F.data == "dropoff_hotels")
async def dropoff_hotels(callback: CallbackQuery, state: FSMContext, _: dict):
    await callback.message.edit_text("🏨 Выберите отель:", reply_markup=hotel_list_keyboard("dropoff"))
    await callback.answer()


@router.callback_query(F.data == "dropoff_restaurants")
async def dropoff_restaurants(callback: CallbackQuery, state: FSMContext, _: dict):
    await callback.message.edit_text("🍽 Выберите ресторан:", reply_markup=restaurant_list_keyboard("dropoff"))
    await callback.answer()


@router.callback_query(F.data.startswith("dropoff_hotel_"))
async def dropoff_selected_hotel(callback: CallbackQuery, state: FSMContext, _: dict):
    try:
        index = int(callback.data.split("_")[-1])
        dropoff_location = HOTEL_NAMES[index]
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора отеля", show_alert=True)
        return

    dropoff_txt = _('dropoff_chosen')
    await state.update_data(dropoff=dropoff_location)
    await callback.message.answer(f"✅ {dropoff_txt}: {dropoff_location}")
    await callback.message.answer(_("choose_date"), reply_markup=date_selection_keyboard(_))
    await state.set_state(OrderServiceState.entering_date)
    await callback.answer()


@router.callback_query(F.data.startswith("dropoff_rest_"))
async def dropoff_selected_restaurant(callback: CallbackQuery, state: FSMContext, _: dict):
    try:
        index = int(callback.data.split("_")[-1])
        dropoff_location = RESTAURANT_NAMES[index]
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора ресторана", show_alert=True)
        return

    dropoff_txt = _('dropoff_chosen')
    await state.update_data(dropoff=dropoff_location)
    await callback.message.answer(f"✅ {dropoff_txt}: {dropoff_location}")
    await callback.message.answer(_("choose_date"), reply_markup=date_selection_keyboard(_))
    await state.set_state(OrderServiceState.entering_date)
    await callback.answer()


# Quick fallback: fixed airport
@router.callback_query(F.data == "pickup_airport")
async def pickup_airport(callback: CallbackQuery, state: FSMContext, _: dict):
    pickup_location = "Аэропорт Вардеро"
    pickup_txt = _('pickup_chosen')
    await state.update_data(pickup=pickup_location)
    await callback.message.answer(f"✅ {pickup_txt}: {pickup_location}")
    await callback.message.answer(_("dropoff_msg"), reply_markup=dropoff_category_keyboard())
    await state.set_state(OrderServiceState.entering_dropoff)
    await callback.answer()


@router.callback_query(F.data == "dropoff_airport")
async def dropoff_airport(callback: CallbackQuery, state: FSMContext, _: dict):
    dropoff_location = "Аэропорт Вардеро"
    dropoff_txt = _('dropoff_chosen')
    await state.update_data(dropoff=dropoff_location)
    await callback.message.answer(f"✅ {dropoff_txt}: {dropoff_location}")
    await callback.message.answer(_("choose_date"), reply_markup=date_selection_keyboard(_))
    await state.set_state(OrderServiceState.entering_date)
    await callback.answer()


# Date / Time selection
@router.callback_query(F.data.startswith("date_"), OrderServiceState.entering_date)
async def handle_date_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    date = callback.data.split("_", 1)[1]
    chosen_date = _('chosen_date')
    await state.update_data(selected_date=date)
    await callback.message.edit_text(f"{chosen_date}: {date}")
    await callback.message.answer(_("choose_hour"), reply_markup=hour_selection_keyboard())
    await state.set_state(OrderServiceState.entering_hour)
    await callback.answer()


@router.callback_query(F.data.startswith("hour_"), OrderServiceState.entering_hour)
async def handle_hour_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    hour = callback.data.split("_", 1)[1]
    chosen_hour = _('chosen_hour')
    await state.update_data(selected_hour=hour)
    await callback.message.edit_text(f"{chosen_hour}: {hour}")
    await callback.message.answer(_("choose_minute"), reply_markup=minute_selection_keyboard())
    await state.set_state(OrderServiceState.entering_minute)
    await callback.answer()



@router.callback_query(F.data.startswith("minute_"), OrderServiceState.entering_minute)
async def handle_minute_selection(callback: CallbackQuery, state: FSMContext, _: dict):
    minute = callback.data.split("_", 1)[1]
    data = await state.get_data()

    # Собираем данные
    date = data.get("selected_date")
    hour = data.get("selected_hour")
    service = data.get("service", "—")
    pickup = data.get("pickup", "—")
    dropoff = data.get("dropoff", "—")
    datetime_str = f"{date} {hour}:{minute}"
    await state.update_data(datetime=datetime_str)

    # 👉 Определяем виды локаций для прайса
    def kind_of(name: str) -> str:
        if name in HOTEL_NAMES:
            return "hotel"
        if name in RESTAURANT_NAMES:
            return "restaurant"
        if name in AIRPORT_NAMES or "Аэропорт" in name:
            return "airport"
        return "city"

    from_kind = kind_of(pickup)
    to_kind   = kind_of(dropoff)
    when_hhmm = f"{hour}:{minute}"

    # 👉 Считаем цену (service slug жёстко 'taxi' для этого сценария)
    try:
        price, payload = quote_price(
            service="taxi",
            from_kind=from_kind, from_id=None,   # id необязательны, сработает kind->kind
            to_kind=to_kind,     to_id=None,
            when_hhmm=when_hhmm,
            options=data.get("options", {}),
        )
        # Можно сохранить для_confirm:
        await state.update_data(price_quote=price, price_payload=payload)
        price_line = f"💵 Цена: {price} USD\n"
    except Exception:
        price_line = "💵 Цена: —\n"

    # Текст карточки
    order_summary = _('order_summary')
    service_txt   = _('service')
    from_txt      = _('from')
    to_txt        = _('to')
    date_txt      = _('date')
    time_txt      = _('time')
    confirm_prompt= _('confirm_prompt')

    summary = (
        f"📋 {order_summary}:\n\n"
        f"🛎️ {service_txt}: {service}\n"
        f"📍 {from_txt}: {pickup}\n"
        f"📍 {to_txt}: {dropoff}\n"
        f"📅 {date_txt}: {date}\n"
        f"⏰ {time_txt}: {hour}:{minute}\n"
        f"{price_line}\n"                # 👉 вставили цену
        f"{confirm_prompt}"
    )

    # Кнопки подтверждения — без изменений
    confirm_btn = _("confirm_order_btn")
    cancel_btn  = _("cancel")
    confirm_kb  = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ " + confirm_btn, callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ " + cancel_btn,  callback_data="cancel_order")]
        ]
    )

    await callback.message.answer(summary, reply_markup=confirm_kb)
    await state.set_state(OrderServiceState.confirming_order)
    await callback.answer()