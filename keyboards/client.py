from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def date_selection_keyboard(_) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора даты."""
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
    """Создает клавиатуру для выбора часа."""
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
    """Создает клавиатуру для выбора минут."""
    buttons = [
        InlineKeyboardButton(
            text=f"{minute:02}",
            callback_data=f"minute_{minute}"
        )
        for minute in (0, 15, 30, 45)
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def language_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора языка (если потребуется)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es"),
        ]
    ])