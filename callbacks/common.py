# callbacks/common.py
from aiogram.filters.callback_data import CallbackData

class BackCb(CallbackData, prefix="back"):
    to: str = "prev"  # зарезервировано на будущее
