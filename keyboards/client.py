from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Literal

# --- Главное меню ---

def main_menu_keyboard(_) -> InlineKeyboardMarkup:
    """Клавиатура для главного меню с категориями услуг."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("🚖 Такси / Кабрио"), callback_data="category_taxi")],
        [InlineKeyboardButton(text=_("🗺️ Экскурсии"), callback_data="category_tours")],
        [InlineKeyboardButton(text=_("📸 Фотографы"), callback_data="category_photographers")],
        [InlineKeyboardButton(text=_("💍 Церемонии"), callback_data="category_ceremonies")],
        [InlineKeyboardButton(text=_("🍽️ Рестораны"), callback_data="category_restaurants")],
        [InlineKeyboardButton(text=_("🏠 Проживание"), callback_data="category_housing")],
    ])

# --- Меню ветки "Такси" ---

def taxi_menu_keyboard(_) -> InlineKeyboardMarkup:
    """Клавиатура для выбора действия в категории 'Такси'."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("📝 Быстрый заказ"), callback_data="taxi_quick_order")],
        [InlineKeyboardButton(text=_("🚘 Выбрать авто (посмотреть автомобили)"), callback_data="taxi_browse_cars")],
        [InlineKeyboardButton(text=_("⬅️ Назад"), callback_data="back_to_main_menu")]
    ])

# --- Навигация и общие кнопки ---

def back_to_main_menu_keyboard(_) -> InlineKeyboardMarkup:
    """Клавиатура с одной кнопкой 'Назад' в главное меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("⬅️ Назад"), callback_data="back_to_main_menu")]
    ])

def home_and_back_keyboard(_, back_callback: str) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками '🏠 Главное меню' и '⬅️ Назад'.
    :param back_callback: Callback-data для кнопки "Назад".
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("🏠 Главное меню"), callback_data="back_to_main_menu"),
            InlineKeyboardButton(text=_("⬅️ Назад"), callback_data=back_callback)
        ]
    ])

# --- Карусель предложений ---

def carousel_keyboard(
    _,
    current_index: int,
    total_items: int,
    category: str,
    provider_tg_id: int
) -> InlineKeyboardMarkup:
    """
    Динамическая клавиатура для карусели предложений.
    Отображает навигацию, индикатор и кнопки действий в зависимости от категории.
    """
    # 1. Навигация: ⬅️ 1/N ➡️
    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"prev_{current_index-1}"))

    nav_buttons.append(InlineKeyboardButton(text=f"{current_index + 1}/{total_items}", callback_data="ignore"))

    if current_index < total_items - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"next_{current_index+1}"))

    # 2. Кнопки действий: "Выбрать" или "Связаться"
    action_button_row = []
    if category == 'taxi':
        action_button_row.append(InlineKeyboardButton(text=_("✅ Выбрать"), callback_data=f"select_offer_{current_index}"))
    else:
        action_button_row.append(InlineKeyboardButton(text=_("👤 Связаться с провайдером"), url=f"tg://user?id={provider_tg_id}"))

    # 3. Навигация: Назад и Главное меню
    back_callback = "back_to_taxi_menu" if category == 'taxi' else "back_to_main_menu"

    navigation_row = [
        InlineKeyboardButton(text=_("🏠 Главное меню"), callback_data="back_to_main_menu"),
        InlineKeyboardButton(text=_("⬅️ Назад"), callback_data=back_callback)
    ]

    keyboard = [nav_buttons, action_button_row, navigation_row]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- Клавиатуры для FSM быстрого заказа ---

def cancel_fsm_keyboard(_) -> InlineKeyboardMarkup:
    """Кнопка отмены для шагов FSM."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("✖️ Отмена"), callback_data="cancel_fsm")]
    ])

def confirmation_keyboard(_) -> InlineKeyboardMarkup:
    """Кнопки 'Подтвердить' и 'Отмена'."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("✅ Подтвердить"), callback_data="fsm_confirm")],
        [InlineKeyboardButton(text=_("✖️ Отмена"), callback_data="cancel_fsm")]
    ])