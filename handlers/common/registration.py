import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from repositories import user_repo

router = Router()
log = logging.getLogger(__name__)

class ProviderRegistration(StatesGroup):
    entering_name = State()

def get_client_main_menu() -> InlineKeyboardMarkup:
    """Возвращает главное меню для клиента."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Посмотреть автомобили", callback_data="show_cars")],
        [InlineKeyboardButton(text="🤝 Стать поставщиком", callback_data="register_provider")]
    ])

def get_provider_main_menu() -> InlineKeyboardMarkup:
    """Возвращает главное меню для поставщика."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚗 Добавить автомобиль", callback_data="add_vehicle")],
        [InlineKeyboardButton(text="📋 Мои автомобили", callback_data="list_my_vehicles")]
    ])

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Обрабатывает команду /start. Приветствует пользователя и показывает главное меню
    в зависимости от его роли.
    """
    await state.clear()
    user = await user_repo.get_or_create_user(message.from_user.id)

    if not user:
        await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
        return

    role = user.get('role')
    if role == 'provider':
        await message.answer(f"С возвращением, поставщик услуг! Ваше меню:", reply_markup=get_provider_main_menu())
    elif role == 'admin':
        # TODO: Добавить админское меню
        await message.answer(f"Здравствуйте, администратор!", reply_markup=get_provider_main_menu())
    else: # client
        await message.answer("Добро пожаловать! Вы можете просмотреть автомобили или стать поставщиком услуг.",
                             reply_markup=get_client_main_menu())

@router.callback_query(F.data == "register_provider")
async def start_provider_registration(callback: CallbackQuery, state: FSMContext):
    """Запускает FSM для регистрации поставщика."""
    await state.set_state(ProviderRegistration.entering_name)
    await callback.message.edit_text("Отлично! Чтобы зарегистрироваться как поставщик, пожалуйста, введите ваше имя или название компании.")
    await callback.answer()

@router.message(ProviderRegistration.entering_name)
async def process_provider_name(message: Message, state: FSMContext):
    """Обрабатывает имя поставщика, обновляет роль и создает профиль."""
    provider_name = message.text
    user = await user_repo.get_user_by_tg_id(message.from_user.id)

    if not user:
        await message.answer("Произошла ошибка. Не удалось найти ваш профиль. Попробуйте /start", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    # Обновляем роль на 'provider'
    await user_repo.set_user_role(user['id'], 'provider')

    # Создаем профиль поставщика
    provider_profile = await user_repo.create_provider_profile(user['id'], provider_name)

    if not provider_profile:
        await message.answer("Произошла ошибка при создании профиля поставщика. Пожалуйста, свяжитесь с поддержкой.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    await message.answer(
        f"Поздравляем! Вы успешно зарегистрированы как поставщик услуг под именем '{provider_name}'.\n\n"
        "Теперь вы можете добавлять свои автомобили.",
        reply_markup=get_provider_main_menu()
    )
    await state.clear()