import os
import csv
from itertools import zip_longest
from functools import lru_cache
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Загрузка данных из CSV ---

@lru_cache()
def get_locations_by_kind() -> dict[str, list[dict]]:
    """
    Загружает локации из data/locations.csv и группирует их по типу (kind).
    Использует lru_cache для кэширования результата.
    """
    locations: dict[str, list[dict]] = {
        "airport": [],
        "hotel": [],
        "restaurant": [],
    }

    # Определяем абсолютный путь к файлу, чтобы скрипт можно было запускать из любого места
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    file_path = os.path.join(base_dir, "data", "locations.csv")

    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                kind = row.get("kind", "").strip().lower()
                if kind in locations:
                    locations[kind].append({
                        "id": row.get("id", "").strip(),
                        "name": row.get("name", "").strip(),
                        "zone": row.get("zone", "").strip().upper(),
                    })
    except FileNotFoundError:
        # В случае отсутствия файла можно предусмотреть логирование или другую обработку
        print(f"Error: locations.csv not found at {file_path}")
        return {}

    return locations

# --- Вспомогательные функции ---

def chunk_buttons(buttons: list[InlineKeyboardButton], n: int) -> list[list[InlineKeyboardButton]]:
    """Разбивает список кнопок на строки по n элементов."""
    if not buttons:
        return []
    # Фильтруем пустые значения, которые могут появиться в последней группе
    return [list(filter(None, group)) for group in zip_longest(*([iter(buttons)] * n))]

def create_location_keyboard(prefix: str, location_kind: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора локации на основе её типа (kind).
    """
    locations_data = get_locations_by_kind()
    locations_list = locations_data.get(location_kind, [])

    if not locations_list:
        return InlineKeyboardMarkup(inline_keyboard=[])

    buttons = [
        InlineKeyboardButton(
            text=loc["name"],
            callback_data=f"{prefix}_{location_kind}_{loc['id']}"
        )
        for loc in locations_list
    ]

    # Для отелей и ресторанов делаем 2 колонки, для аэропортов - 1
    num_columns = 2 if location_kind in ["hotel", "restaurant"] else 1
    keyboard_layout = chunk_buttons(buttons, num_columns)

    return InlineKeyboardMarkup(inline_keyboard=keyboard_layout)

# --- Клавиатуры категорий ---

def pickup_category_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора категории точки отправления."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏨 Отель", callback_data="pickup_category_hotel")],
            [InlineKeyboardButton(text="🍽 Ресторан", callback_data="pickup_category_restaurant")],
            [InlineKeyboardButton(text="🛫 Аэропорт", callback_data="pickup_category_airport")],
        ]
    )

def dropoff_category_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора категории точки назначения."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏨 Отель", callback_data="dropoff_category_hotel")],
            [InlineKeyboardButton(text="🍽 Ресторан", callback_data="dropoff_category_restaurant")],
            [InlineKeyboardButton(text="🛬 Аэропорт", callback_data="dropoff_category_airport")],
        ]
    )

# --- Функции для создания клавиатур по типам локаций ---

def airport_list_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру со списком аэропортов."""
    return create_location_keyboard(prefix, "airport")

def hotel_list_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру со списком отелей."""
    return create_location_keyboard(prefix, "hotel")

def restaurant_list_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру со списком ресторанов."""
    return create_location_keyboard(prefix, "restaurant")