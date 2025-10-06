# keyboards/main_menu.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .common import build_nav_keyboard

def main_menu_keyboard():
    """Создает клавиатуру главного меню с двумя основными разделами."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🚖 Такси/ретрокары", callback_data="main_menu:taxi_retro")
    builder.button(text="🧭 Услуги Кубы", callback_data="main_menu:cuba_services")
    builder.adjust(1)
    return builder.as_markup()

def cuba_services_keyboard():
    """Создает клавиатуру со списком 'Услуг Кубы'."""
    builder = InlineKeyboardBuilder()

    services = {
        "🎩 Гиды / Переводчики": "cuba_service:guide",
        "📸 Фото и видео": "cuba_service:photo",
        "💍 Свадебные церемонии": "cuba_service:wedding",
        "💄 Стилисты / Визажисты": "cuba_service:style",
        "🍽️ Рестораны / Домашние обеды": "cuba_service:food",
        "🧑‍💼 Свой человек (Варадеро)": "cuba_service:concierge",
        "👗 Аренда платьев": "cuba_service:dress",
        "🗺️ Экскурсии": "cuba_service:tours",
        "📦 Индивидуальный запрос": "cuba_service:custom",
    }

    for text, callback_data in services.items():
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)

    # Добавляем навигационные кнопки "Назад" и "В главное меню"
    nav_keyboard = build_nav_keyboard(back_callback="nav_back_to_main")
    builder.row(*nav_keyboard.inline_keyboard[0])

    return builder.as_markup()

def taxi_services_keyboard():
    """Создает клавиатуру для выбора между такси и ретро-автомобилем."""
    builder = InlineKeyboardBuilder()

    # Эти callback'и будут перехвачены существующим обработчиком service_selection
    builder.button(text="🚖 Такси", callback_data="service_taxi")
    builder.button(text="🚗 Ретро-автомобиль", callback_data="service_retro")

    builder.adjust(1)

    # Добавляем навигационные кнопки "Назад" и "В главное меню"
    nav_keyboard = build_nav_keyboard(back_callback="nav_back_to_main")
    builder.row(*nav_keyboard.inline_keyboard[0])

    return builder.as_markup()