# keyboards/common.py
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.common import BackCb

def back_kb(text: str = "◀️ Назад") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=text, callback_data=BackCb().pack())
    return kb.as_markup()

