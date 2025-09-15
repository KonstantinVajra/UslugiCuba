# keyboards/common.py
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from callbacks.common import BackCb


def back_kb(text: str = "◀️ Назад") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=text, callback_data=BackCb().pack())
    return kb.as_markup()

def confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data="confirm_order")
    kb.button(text="❌ Отмена",     callback_data="cancel_order")
    kb.adjust(2)
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data=BackCb().pack()))
    return kb.as_markup()

def minutes_kb():
    kb = InlineKeyboardBuilder()
    for m in (0, 15, 30, 45):
        kb.button(text=f"{m:02d}", callback_data=f"min:{m:02d}")
    kb.adjust(4)
    kb.row(InlineKeyboardButton(text="◀️ Назад", callback_data=BackCb().pack()))
    return kb.as_markup()