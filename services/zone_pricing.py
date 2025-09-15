# services/zone_pricing.py
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import csv, re
from typing import Dict, Optional

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_slug_re = re.compile(r"[^a-z0-9]+")

def slugify(s: str) -> str:
    s = (s or "").strip().lower().replace("ё", "e")
    return _slug_re.sub("_", s).strip("_")

# Исключения среди ресторанов
RESTAURANT_A = {
    "al_capone", "al_capone_varadero", "restaurant_al_capone",
}
RESTAURANT_C = {
    "dupont", "casa_dupont", "mansion_dupont", "restaurante_dupont", "xanadu",
}

# Если нужно быстро поправить конкретный id → зона
TEMP_ZONE_OVERRIDES: Dict[str, str] = {
    # "la_gruta_del_vino_59я_улица_в_парке_хосоне": "B",
}

AIRPORT_IDS = {
    "varadero_airport", "juan_gualberto_gomez", "vra",
    "aeroport_varadero", "aэропорт_варадеро", "аэропорт_варадеро",
}

def _load_csv_zones(path: Path, zones: Dict[str, str]) -> None:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            z = (row.get("zone_code") or "").strip().upper()
            if name and z:
                zones[slugify(name)] = z

@lru_cache(maxsize=1)
def load_zones() -> Dict[str, str]:
    zones: Dict[str, str] = {}
    _load_csv_zones(DATA_DIR / "zones_hotels.csv", zones)
    _load_csv_zones(DATA_DIR / "zones_restaurants.csv", zones)
    _load_csv_zones(DATA_DIR / "zones_airports.csv", zones)
    zones.update(TEMP_ZONE_OVERRIDES)
    for aid in AIRPORT_IDS:
        zones.setdefault(aid, "AIRPORT")
    return zones

def id_to_zone(place_id: str) -> Optional[str]:
    return load_zones().get((place_id or "").lower())

def zone_with_defaults(place_id: str, kind: Optional[str]) -> Optional[str]:
    """Вернёт зону из CSV/оверрайдов, а для ресторанов — дефолт B с исключениями."""
    if not place_id:
        return None
    pid = (place_id or "").lower()

    # 1) явные карты
    z = id_to_zone(pid)
    if z:
        return z

    # 2) дефолт для ресторанов
    if (kind or "").lower() == "restaurant":
        if pid in RESTAURANT_A:
            return "A"
        if pid in RESTAURANT_C:
            return "C"
        return "B"  # ваш общий случай

    return None
