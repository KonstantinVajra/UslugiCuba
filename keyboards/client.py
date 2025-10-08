from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def date_selection_keyboard(_) -> InlineKeyboardMarkup:
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(7)]

    buttons = [
        InlineKeyboardButton(
            text=_("Today") if i == 0 else date.strftime("%d.%m"),
            callback_data=f"date_{date.strftime('%Y-%m-%d')}"
        )
        for i, date in enumerate(dates)
    ]

    keyboard = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def hour_selection_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=f"{hour:02}",
            callback_data=f"hour_{hour}"
        )
        for hour in range(8, 21)  # С 08:00 до 20:00
    ]

    keyboard = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def minute_selection_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=f"{minute:02}",
            callback_data=f"minute_{minute}"
        )
        for minute in (0, 15, 30, 45)
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def service_inline_keyboard(_) -> InlineKeyboardMarkup:
    """
    Главное меню с двумя кнопками.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🚖 {_('Taxi & Cabriolets')}", callback_data="svc:taxi")],
        [InlineKeyboardButton(text=f"🇨🇺 {_('Cuba Services')}", callback_data="show_cuba_services")]
    ])

def cuba_services_keyboard(_) -> InlineKeyboardMarkup:
    """
    Клавиатура для "Услуг Кубы".
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🧭 {_('Guides and excursions')}", callback_data="service_guide")],
        [InlineKeyboardButton(text=f"📸 {_('Photo and video')}", callback_data="service_photographer")],
        [InlineKeyboardButton(text=f"💄 {_('Stylists and make-up artists')}", callback_data="service_stylist")],
        [InlineKeyboardButton(text=f"🍽 {_('Restaurants and home cooking')}", callback_data="service_restaurant")],
        [InlineKeyboardButton(text=f"💍 {_('Wedding ceremonies')}", callback_data="service_wedding")],
        [InlineKeyboardButton(text=f"👗 {_('Dress rental')}", callback_data="service_dress_rental")],
        [InlineKeyboardButton(text=f"🕴 {_('Your man / Fixer')}", callback_data="service_fixer")],
        [InlineKeyboardButton(text=f"✉️ {_('Individual requests')}", callback_data="service_individual")],
        [InlineKeyboardButton(text=f"⬅️ {_('Back')}", callback_data="back_to_main_menu")]
    ])


def confirm_inline_keyboard(_) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌", callback_data="confirm_no"),
        ]
    ])


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es"),
        ]
    ])