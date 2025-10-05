from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def get_main_menu() -> InlineKeyboardMarkup:
    """Возвращает главное меню для клиента."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Посмотреть автомобили", callback_data="browse_cars")]
    ])

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обрабатывает команду /start, приветствует пользователя и показывает главное меню.
    """
    await message.answer(
        "Добро пожаловать! Здесь вы можете посмотреть доступные ретро-автомобили для аренды.",
        reply_markup=get_main_menu()
    )