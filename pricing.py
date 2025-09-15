# pricing.py
from __future__ import annotations
from typing import Dict, Optional, Tuple
from pathlib import Path
import csv, re

# === пути к данным ===
DATA_DIR = Path(__file__).resolve().parent / "data"
HOTELS_CSV = DATA_DIR / "zones_hotels.csv"
RESTAURANTS_CSV = DATA_DIR / "zones_restaurants.csv"  # опционально

# === айди аэропортов (ровно id из твоих inline-кнопок) ===
AIRPORT_VRA_IDS = {
    "varadero_airport", "juan_gualberto_gomez", "vra",
    "aeroport_varadero", "aэропорт_варадеро", "аэропорт_варадеро",
}
AIRPORT_HAV_IDS = {
    "havana_airport", "jose_marti", "jose_marti_international_airport", "hav",
    "aeroport_havana", "aэропорт_гаваны", "аэропорт_гаваны",
}
AIRPORT_IDS = AIRPORT_VRA_IDS | AIRPORT_HAV_IDS

# === порядок зон ===
ZONE_ORDER = ["A", "B", "C", "D"]
ZONE_INDEX = {z: i for i, z in enumerate(ZONE_ORDER)}

# === нормализация id/имён: нижний регистр + любые не-«букво/цифро» → '_' (кириллица сохраняется) ===
_slug_re = re.compile(r"\W+", flags=re.UNICODE)
def slugify(s: str) -> str:
    return _slug_re.sub("_", (s or "").strip().lower()).strip("_")

def _load_zones_csv(path: Path) -> Dict[str, str]:
    """
    Читает CSV с колонками минимум: name, zone_code.
    Ключ строим от name через slugify, т.е. id = slugify(name).
    """
    mapping: Dict[str, str] = {}
    if not path.exists():
        return mapping
    with path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            zone = (row.get("zone_code") or "").strip().upper()
            if not name or not zone:
                continue
            mapping[slugify(name)] = zone
    return mapping

# Загружаем разом при импорте (пара сотен строк — ок)
_HOTEL_ZONES: Dict[str, str] = _load_zones_csv(HOTELS_CSV)
_RESTAURANT_ZONES: Dict[str, str] = _load_zones_csv(RESTAURANTS_CSV)  # может быть пуст

def _zone_distance(a: str, b: str) -> Optional[int]:
    if a not in ZONE_INDEX or b not in ZONE_INDEX:
        return None
    return abs(ZONE_INDEX[a] - ZONE_INDEX[b])

def _airport_price_vra(zone: str) -> Optional[float]:
    # D↔VRA=40, A/B↔VRA=30, C↔VRA=35
    if zone == "D": return 40.0
    if zone in {"A", "B"}: return 30.0
    if zone == "C": return 35.0
    return None

def _zone_for(kind: Optional[str], _id: Optional[str]) -> Optional[str]:
    """
    Возвращает 'A'/'B'/'C'/'D' или 'AIRPORT_VRA'/'AIRPORT_HAV' по (kind, id) из FSM.
    Все соответствия берём из CSV (без распознаваний текстов!).
    """
    kid = (_id or "").lower()
    knd = (kind or "").lower()

    # аэропорты — по id из кнопок
    if kid in AIRPORT_HAV_IDS: return "AIRPORT_HAV"
    if kid in AIRPORT_VRA_IDS: return "AIRPORT_VRA"
    if knd == "airport" and kid in AIRPORT_IDS: return "AIRPORT"  # запасной случай

    # отели — из zones_hotels.csv (ключ id = slugify(name))
    if knd == "hotel":
        # id из FSM уже слаг: slugify(name) в ваших генераторах.
        # если по какой-то причине id «не по месту», пытаемся нормализовать:
        return _HOTEL_ZONES.get(kid) or _HOTEL_ZONES.get(slugify(kid))

    # рестораны — сначала ищем в zones_restaurants.csv, иначе дефолт B (как вы описали)
    if knd == "restaurant":
        z = _RESTAURANT_ZONES.get(kid) or _RESTAURANT_ZONES.get(slugify(kid))
        if z: return z
        return "B"  # дефолт для ресторанов

    # прочие типы — по мере появления добавим CSV и сюда же
    return None

def quote_price(
    service: str,
    from_kind: Optional[str], from_id: Optional[str],
    to_kind:   Optional[str], to_id:   Optional[str],
    when_hhmm: Optional[str] = None,
    options:   Optional[dict] = None,
) -> tuple[float, dict]:
    """
    Публичное API для хэндлеров: вернуть (цена_USD, meta).
    Полностью опирается на id из FSM и CSV. Никаких эвристик по строкам.
    """
    options = options or {}
    if service != "taxi":
        return 0.0, {"rule": "n/a"}

    z_from = _zone_for(from_kind, from_id)
    z_to   = _zone_for(to_kind, to_id)

    # HAV ↔ зоны A–D = 120
    if z_from == "AIRPORT_HAV" and z_to in ZONE_INDEX:
        return 120.0, {"rule": f"airport_hav:{z_to}", "z_from": z_from, "z_to": z_to}
    if z_to == "AIRPORT_HAV" and z_from in ZONE_INDEX:
        return 120.0, {"rule": f"airport_hav:{z_from}", "z_from": z_from, "z_to": z_to}

    # VRA ↔ зоны A–D по правилам
    if z_from == "AIRPORT_VRA" and z_to in ZONE_INDEX:
        p = _airport_price_vra(z_to)
        if p is not None:
            return p, {"rule": f"airport_vra:{z_to}", "z_from": z_from, "z_to": z_to}
    if z_to == "AIRPORT_VRA" and z_from in ZONE_INDEX:
        p = _airport_price_vra(z_from)
        if p is not None:
            return p, {"rule": f"airport_vra:{z_from}", "z_from": z_from, "z_to": z_to}

    # Зоны A–D: спец-кейсы и базовые дистанции
    if z_from in ZONE_INDEX and z_to in ZONE_INDEX:
        pair = {z_from, z_to}
        if pair == {"D", "A"}:
            return 30.0, {"rule": "zones:D<->A", "z_from": z_from, "z_to": z_to}
        if pair == {"D", "B"}:
            return 25.0, {"rule": "zones:D<->B", "z_from": z_from, "z_to": z_to}

        dist = _zone_distance(z_from, z_to)
        if dist == 0: return 10.0, {"rule": "zones:same", "z_from": z_from, "z_to": z_to}
        if dist == 1: return 15.0, {"rule": "zones:adjacent", "z_from": z_from, "z_to": z_to}
        if dist == 2: return 20.0, {"rule": "zones:through_one", "z_from": z_from, "z_to": z_to}
        if dist == 3: return 30.0, {"rule": "zones:through_two", "z_from": z_from, "z_to": z_to}

    # если не смогли определить зоны (нет в CSV), честный фолбэк
    return 15.0, {"rule": "fallback", "z_from": z_from, "z_to": z_to}
