from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from itertools import zip_longest


# Добавь список аэропортов
AIRPORT_NAMES = [
    "Аэропорт Варадеро (VRA)",
    "Аэропорт Гаваны (HAV)",
]


def chunk_buttons(items, n: int) -> list[list[InlineKeyboardButton]]:
    """Разбивает список items на строки по n элементов для клавиатуры."""
    args = [iter(items)] * n
    return [list(filter(None, group)) for group in zip_longest(*args)]



def pickup_category_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏨 Отель", callback_data="pickup_hotels")],
            [InlineKeyboardButton(text="🍽 Ресторан", callback_data="pickup_restaurants")],
            [InlineKeyboardButton(text="🛫 Аэропорт", callback_data="pickup_airports")],
        ]
    )

def dropoff_category_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏨 Отель", callback_data="dropoff_hotels")],
            [InlineKeyboardButton(text="🍽 Ресторан", callback_data="dropoff_restaurants")],
            [InlineKeyboardButton(text="🛬 Аэропорт", callback_data="dropoff_airports")],
        ]
    )

def airport_list_keyboard(type_: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=name,
                    callback_data=f"{type_}_airport_{i}"
                )
            ] for i, name in enumerate(AIRPORT_NAMES)
        ]
    )

# --- УНИКАЛЬНЫЕ ЭМОДЗИ ДЛЯ КАЖДОГО ОТЕЛЯ ---
HOTEL_EMOJIS: dict[str, str] = {
    "Arenas Doradas": "✨",
    "Barcelo Solymar": "🌞",
    "Blau Varadero": "💙",
    "Brisas Santa Lucia": "🌬️",
    "Brisas del Caribe": "🌀",
    "Gran Caribe Vigia": "🔭",
    "Grand Aston Paredon": "🏰",
    "GrandMemories & Santuari": "🧿",
    "Iberostar Bella Costa": "🌊",
    "Iberostar Bella Vista": "🖼️",
    "Iberostar Laguna Azul": "💧",
    "Iberostar Playa Alameda": "🏖️",
    "Iberostar Selection": "🌟",
    "Iberostar Tainos": "🗿",
    "Las Morals": "🎯",
    "Los Cactus Varadero": "🌵",
    "Melia International": "🌐",
    "Melia Las Americas": "🌎",
    "Melia Las Antillas": "🛶",
    "Melia Marina Varadero": "🚤",
    "Melia Peninsula": "🗺️",
    "Melia Varadero": "🏩",
    "Memories Caribe Beach": "🐚",
    "Mistique Casa Perla": "🦪",
    "Muthu Playa Varadero": "🪸",
    "Occidental Arenas Blancas": "🏜️",
    "Palma Real": "🌴",
    "Paradisus Princess": "👸",
    "Paradisus Varadero": "🏄‍♂️",
    "Playa Vista Azul": "🟦",
    "Puntarena": "⚓",
    "Resonans Memoris Varadero": "🎶",
    "Roc Arenas Doradas": "🟨",
    "Roc Barlovento": "🎷",
    "Roc Varadero": "🧱",
    "Royalton Hicacos": "👑",
    "Selectim Family Resort Varadero": "👨‍👩‍👧‍👦",
    "Sirenis Tropical Varadero": "🐠",
    "Sol Caribe Beach": "☀️",
    "Sol Palmeras": "🌿",
    "Sol Varadero": "🔆",
    "Starfish Cuatro Palmas": "⭐️",
    "Starfish Varadero": "🐟",
    "Tuxpan Hotel": "🧳",
    "Valentin el Patriarca": "🌺",
    "Villa Cuba": "🇨🇺",
    "Villa Tortuga": "🐢",
}
HOTEL_NAMES = list(HOTEL_EMOJIS.keys())

# --- УНИКАЛЬНЫЕ ЭМОДЗИ ДЛЯ КАЖДОГО РЕСТОРАНА ---
RESTAURANT_EMOJIS: dict[str, str] = {
    "43.5 (43я улица)": "🔢",
    "Bar Galeón (53я улица)": "🏴‍☠️",
    "Beatles Bar": "🎸",
    "Bolshoi (62я улица)": "🎭",
    "Casa de Al. Аль Капоне (1я улица)": "🕵️",
    "Castell Nuovo Terazza": "🏯",
    "Compas Bar (34я улица)": "🧭",
    "Don Alex (31я улица)": "👨‍🍳",
    "El Aljibe": "🍗",
    "El Ancla (62я улица)": "🪝",
    "El Caney (40я улица)": "🏚️",
    "El Criollo (18я улица)": "🧉",
    "El Melaito": "🦞",
    "El Rancho (58я улица)": "🐄",
    "El Toro (25я улица)": "🐂",
    "La Barbacoa": "🍖",
    "La Cava (62 улица)": "🍷",
    "La Terazza Cuba (18я улица)": "🌇",
    "La Vaca Rosada. Розовая Корова (21я ул)": "🐮",
    "La Vicaria (38я улица)": "⛪",
    "La bodeguita del medio (Varadero 40я ул)": "🍸",
    "La gruta del vino (59я улица. В парке Хосоне)": "🍾",
    "La rampa (43я улица)": "🛗",
    "Marisquería Laurent (31я улица)": "🦐",
    "Mistique Casa Perla": "🐙",
    "Pina Colada La Vigia": "🍹",
    "Rigo's pizza": "🍕",
    "Salsa Suarez (31я улица)": "💃",
    "Varadero 60 (60я улица)": "6️⃣",
    "Vernissage (36я улица)": "🎨",
    "Wacos Club": "🎧",
    "Бар Floridita": "🍍",
    "Бар клуб Calle 62 (62я улица)": "🎵",
    "Вилла Дюпона. Коктейли": "🥂",
    "Клуб La Comparсита": "🕺",
    "Пивоварня Factoria 43": "🍺",
    "Рудольфо и его лобстеры (28я-29я)": "🦀",
}
RESTAURANT_NAMES = list(RESTAURANT_EMOJIS.keys())

def hotel_list_keyboard(prefix: str) -> InlineKeyboardMarkup:
    hotels = list(HOTEL_EMOJIS.keys())
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=f"{HOTEL_EMOJIS[name]} {name}", callback_data=f"{prefix}_hotel_{i}")
        for i, name in enumerate(HOTEL_NAMES)
    ]

    keyboard = chunk_buttons(buttons, 2)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def restaurant_list_keyboard(prefix: str) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=f"{RESTAURANT_EMOJIS[name]} {name}",
            callback_data=f"{prefix}_rest_{i}"
        )
        for i, name in enumerate(RESTAURANT_NAMES)
    ]
    keyboard = chunk_buttons(buttons, 2)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)