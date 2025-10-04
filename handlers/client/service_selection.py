import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from middlewares.i18n import _
from states.client_states import OrderServiceState

# Импортируем новые репозитории для работы с БД
from repositories import services_repo, orders_repo

log = logging.getLogger(__name__)
router = Router()


# Шаг 1: Команда /start, отображение услуг из БД
@router.message(F.text.in_({"/start", "/order"}))
async def start_order(message: Message, state: FSMContext):
    await state.clear()

    # Получаем услуги (например, такси в Варадеро, city_id=1, как указано в задаче)
    services = await services_repo.list_services(category='taxi', city_id=1)

    if not services:
        await message.answer(_("no_services_available", "К сожалению, доступных услуг нет."))
        return

    buttons = [
        [InlineKeyboardButton(
            text=svc.get("title", f"Service {svc['id']}"),
            callback_data=f"service:{svc['id']}"
        )] for svc in services
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(_("choose_service", "Пожалуйста, выберите услугу:"), reply_markup=keyboard)
    await state.set_state(OrderServiceState.choosing_service)


# Шаг 2: Услуга выбрана, отображение тарифов/зон из БД
@router.callback_query(F.data.startswith("service:"), OrderServiceState.choosing_service)
async def handle_service_choice(callback: CallbackQuery, state: FSMContext):
    try:
        service_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        log.warning("Некорректные callback-данные для выбора услуги: %s", callback.data)
        await callback.answer("Некорректный выбор.", show_alert=True)
        return

    # Находим выбранную услугу, чтобы сохранить ее данные в состоянии
    services = await services_repo.list_services(category='taxi')
    selected_service = next((s for s in services if s['id'] == service_id), None)

    if not selected_service:
        await callback.message.edit_text(_("service_not_found", "Выбранная услуга не найдена."))
        return

    await state.update_data(
        service_id=service_id,
        city_id=selected_service.get("city_id"),
        service_title=selected_service.get("title")
    )

    # Получаем тарифы для выбранной услуги
    offers = await services_repo.list_offers(service_id=service_id)

    if not offers:
        await callback.message.edit_text(_("no_offers_available", "Для этой услуги нет доступных тарифов."))
        return

    buttons = [
        [InlineKeyboardButton(
            text=f'{offer.get("title")} - {offer.get("price")} {offer.get("currency", "USD")}',
            callback_data=f"zone:{offer['zone_id']}"
        )] for offer in offers if offer.get("price")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    # Используем старое состояние, но логика новая
    await callback.message.edit_text(_("choose_zone", "Выберите зону или тариф:"), reply_markup=keyboard)
    await state.set_state(OrderServiceState.entering_pickup)


# Шаг 3: Зона выбрана, показываем подтверждение
@router.callback_query(F.data.startswith("zone:"), OrderServiceState.entering_pickup)
async def handle_zone_choice(callback: CallbackQuery, state: FSMContext):
    try:
        zone_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        log.warning("Некорректные callback-данные для выбора зоны: %s", callback.data)
        await callback.answer("Некорректный выбор.", show_alert=True)
        return

    await state.update_data(zone_id=zone_id)

    data = await state.get_data()
    service_title = data.get("service_title", "Услуга")

    summary_text = (
        f"Вы выбрали:\n"
        f"Услуга: {service_title}\n"
        f"Зона ID: {zone_id}\n\n"
        f"Подтвердить заказ?"
    )

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")]
    ])

    await callback.message.edit_text(summary_text, reply_markup=confirm_kb)
    await state.set_state(OrderServiceState.confirming_order)


# Шаг 4: Подтверждение, создание заказа в БД
@router.callback_query(F.data == "confirm_order", OrderServiceState.confirming_order)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Обрабатываем ваш заказ...")

    try:
        user = callback.from_user
        data = await state.get_data()

        # 1. Убедимся, что клиент существует в БД
        customer_id = await orders_repo.ensure_customer(
            tg_user_id=user.id,
            tg_username=user.username
        )

        # 2. Создаем заказ
        order_id = await orders_repo.create_order(
            customer_id=customer_id,
            service_id=data.get("service_id"),
            city_id=data.get("city_id"),
            zone_id=data.get("zone_id"),
            pax=1, # По умолчанию 1 пассажир
            note=None,
            vehicle_id=None, # Выбор авто не реализован в этом сценарии
            meta=data # Сохраняем все данные из состояния в мета-поле
        )

        # 3. Добавляем событие 'placed' (заказ размещен)
        await orders_repo.add_event(
            order_id=order_id,
            event='placed',
            actor_type='customer',
            actor_id=user.id,
            payload={"state_data": data}
        )

        confirmation_text = f"Заказ №{order_id} создан. Статус: new"
        await callback.message.edit_text(confirmation_text)

    except Exception:
        log.exception("Не удалось создать заказ")
        await callback.message.edit_text("Произошла ошибка при обработке заказа. Пожалуйста, попробуйте снова.")
    finally:
        await state.clear()


# Простой хэндлер отмены
@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Заказ отменен.")
    await callback.answer()