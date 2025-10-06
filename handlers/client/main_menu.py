# handlers/client/main_menu.py
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.main_menu import main_menu_keyboard, cuba_services_keyboard, taxi_services_keyboard
from keyboards.common import build_nav_keyboard

router = Router()

# --- Текст для сообщений ---
MAIN_MENU_TEXT = "Добро пожаловать! Выберите интересующий вас раздел:"
CUBA_SERVICES_TEXT = "Выберите одну из наших услуг на Кубе:"
TAXI_SERVICES_TEXT = "Выберите тип автомобиля:"


# --- Обработчики ---

@router.message(CommandStart())
async def command_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())

@router.callback_query(F.data == "nav_main_menu")
async def process_nav_to_main_menu(callback: CallbackQuery):
    """Обработчик для кнопки 'В главное меню'"""
    await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "main_menu:cuba_services")
async def process_show_cuba_services(callback: CallbackQuery):
    """Показывает список услуг на Кубе"""
    await callback.message.edit_text(
        CUBA_SERVICES_TEXT,
        reply_markup=cuba_services_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "main_menu:taxi_retro")
async def process_show_taxi_services(callback: CallbackQuery):
    """Показывает меню выбора такси/ретро"""
    await callback.message.edit_text(
        TAXI_SERVICES_TEXT,
        reply_markup=taxi_services_keyboard()
    )
    await callback.answer()

# --- Обработчик для кнопок "Назад" ---

@router.callback_query(F.data == "nav_back_to_main")
async def process_back_to_main_menu(callback: CallbackQuery):
    """Возвращает в главное меню из любого подменю"""
    await callback.message.edit_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()