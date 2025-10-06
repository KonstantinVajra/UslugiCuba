# keyboards/common.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_nav_keyboard(back_callback: str | None = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "⬅️ Назад" и "🏠 В главное меню".

    :param back_callback: Callback-данные для кнопки "Назад". Если None, кнопка не добавляется.
    :return: Объект InlineKeyboardMarkup.
    """
    builder = InlineKeyboardBuilder()
    if back_callback:
        builder.button(text="⬅️ Назад", callback_data=back_callback)
    builder.button(text="🏠 В главное меню", callback_data="nav_main_menu")
    builder.adjust(2)
    return builder.as_markup()