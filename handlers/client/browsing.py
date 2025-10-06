# handlers/client/browsing.py
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from repo.offers import get_published_offers_by_category
from keyboards.client import carousel_keyboard, back_to_main_menu_keyboard, taxi_menu_keyboard
from keyboards.locations import pickup_category_keyboard
from states.client_states import OrderServiceState # Используем правильные состояния
from middlewares.i18n import gettext as _

router = Router()

# --- Вспомогательные функции ---

def format_offer_caption(_, offer: dict, category: str) -> str:
    """Форматирует описание предложения для карточки в карусели."""
    if category == 'taxi':
        caption_parts = [
            f"<b>{offer.get('title', '')}</b>\n"
        ]
        if offer.get('description'):
            caption_parts.append(f"{offer.get('description')}\n")

        caption_parts.append(f"<b>Мест:</b> {offer.get('seats', '—')}")

        if offer.get('price_per_hour'):
            caption_parts.append(f"<b>Цена в час:</b> {offer.get('price_per_hour')} USD")
        if offer.get('price_details'):
            caption_parts.append(f"<i>{offer.get('price_details')}</i>")

        return "\n".join(caption_parts)

    # Форматирование для других категорий
    return f"<b>{offer.get('title', 'Нет заголовка')}</b>\n\n{offer.get('description', 'Нет описания')}"


async def show_offer_carousel(
    callback_or_message,
    state: FSMContext,
    _,
    category: str,
    index: int = 0
):
    """
    Основная функция для отображения карусели предложений.
    Загружает данные, сохраняет в state и показывает карточку по индексу.
    """
    offers = await get_published_offers_by_category(category)
    await state.update_data({f'offers_{category}': offers, 'current_category': category})

    message = callback_or_message if not isinstance(callback_or_message, CallbackQuery) else callback_or_message.message

    if not offers:
        await message.edit_text(
            _("К сожалению, в этой категории пока нет предложений."),
            reply_markup=back_to_main_menu_keyboard(_)
        )
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.answer()
        return

    offer = offers[index]
    caption = format_offer_caption(_, offer, category)
    photo_id = (offer.get('photo_file_ids') or [None])[0]
    markup = carousel_keyboard(_, index, len(offers), category, offer.get('provider_tg_id'))

    try:
        if photo_id:
            media = InputMediaPhoto(media=photo_id, caption=caption, parse_mode="HTML")
            if message.photo:
                await message.edit_media(media, reply_markup=markup)
            else:
                await message.delete()
                await message.answer_photo(photo_id, caption=caption, reply_markup=markup, parse_mode="HTML")
        else:
            await message.edit_text(caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        logging.warning(f"Failed to edit message, sending new one. Error: {e}")
        if photo_id:
            await message.answer_photo(photo_id, caption=caption, reply_markup=markup, parse_mode="HTML")
        else:
            await message.answer(caption, reply_markup=markup, parse_mode="HTML")

    await state.update_data({f'current_index_{category}': index})
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.answer()

# --- Обработчики карусели ---

@router.callback_query(F.data.in_({"taxi_browse_cars", "category_tours", "category_photographers", "category_ceremonies", "category_restaurants", "category_housing"}))
async def cb_start_browsing(callback: CallbackQuery, state: FSMContext):
    category_map = {
        "taxi_browse_cars": "taxi",
        "category_tours": "tours",
        "category_photographers": "photographers",
        "category_ceremonies": "ceremonies",
        "category_restaurants": "restaurants",
        "category_housing": "housing",
    }
    category = category_map.get(callback.data)
    await show_offer_carousel(callback, state, _, category, index=0)


@router.callback_query(F.data.startswith("prev_") | F.data.startswith("next_"))
async def cb_navigate_carousel(callback: CallbackQuery, state: FSMContext):
    try:
        new_index = int(callback.data.split("_")[1])
        data = await state.get_data()
        category = data.get('current_category')
        if not category: raise ValueError("Category not found in state")
        await show_offer_carousel(callback, state, _, category, index=new_index)
    except (ValueError, IndexError, KeyError) as e:
        await callback.answer("Ошибка навигации.", show_alert=True)
        logging.warning(f"Invalid carousel navigation: {e} | CB: {callback.data}")


@router.callback_query(F.data.startswith("select_offer_"))
async def cb_select_offer(callback: CallbackQuery, state: FSMContext):
    try:
        index = int(callback.data.split("_")[-1])
        data = await state.get_data()
        category = data.get('current_category')
        offers = data.get(f'offers_{category}')

        if not offers or not category: raise ValueError("Offers or category not found in state")

        selected_car_title = offers[index].get('title', 'Неизвестное авто')
        await state.update_data(selected_car=selected_car_title)

        # Запускаем FSM из service_selection
        await state.set_state(OrderServiceState.entering_pickup)

        await callback.message.answer(
            _("Вы выбрали: {car_title}.\n\nТеперь выберите, откуда едем?").format(car_title=selected_car_title)
        )

        # Показываем первую клавиатуру из флоу заказа
        await callback.message.answer(
            _("enter_pickup"),
            reply_markup=pickup_category_keyboard()
        )
        await callback.answer()

    except (ValueError, IndexError, KeyError) as e:
        await callback.answer("Ошибка выбора автомобиля.", show_alert=True)
        logging.warning(f"Failed to select offer: {e} | CB: {callback.data}")


@router.callback_query(F.data == "back_to_taxi_menu")
async def cb_back_to_taxi_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        _("Такси / Кабриолеты — выберите действие:"),
        reply_markup=taxi_menu_keyboard(_)
    )
    await callback.answer()