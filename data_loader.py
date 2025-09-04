# data_loader.py
from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, List, Tuple

# Папка со справочниками
from pathlib import Path
DATA_DIR = Path(__file__).resolve().parent / "data"

assert (DATA_DIR / "locations.csv").exists(), f"locations.csv not found at {DATA_DIR}"
assert (DATA_DIR / "prices.csv").exists(), f"prices.csv not found at {DATA_DIR}"


# Кэши, чтобы не читать файл при каждом вызове
_locations_cache: Dict[str, List[Tuple[str, str]]] | None = None
_prices_cache: List[dict] | None = None


def load_locations() -> Dict[str, List[Tuple[str, str]]]:
    """
    Загружает locations.csv
    Возвращает словарь вида:
      {
        "airport": [("vra", "Varadero Airport"), ("hav","Jose Marti Airport"), ...],
        "hotel":   [("ibv","Iberostar Varadero"), ...],
        "city":    [("havana","Havana"), ...],
      }
    """
    global _locations_cache
    if _locations_cache is not None:
        return _locations_cache

    res: Dict[str, List[Tuple[str, str]]] = {}
    fp = DATA_DIR / "locations.csv"
    with fp.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kind = row["kind"].strip()
            _id = row["id"].strip()
            name = row["name"].strip()
            res.setdefault(kind, []).append((_id, name))
    _locations_cache = res
    return res


def load_prices() -> List[dict]:
    """
    Загружает prices.csv
    Возвращает список словарей:
      {
        "service": "taxi",
        "from_kind": "airport",
        "from_id": "vra",
        "to_kind": "hotel",
        "to_id": "ibv",
        "base_usd": 35.0,
        "notes": "день; ночь +20%"
      }
    """
    global _prices_cache
    if _prices_cache is not None:
        return _prices_cache

    prices: List[dict] = []
    fp = DATA_DIR / "prices.csv"
    with fp.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prices.append({
                "service": row["service"].strip(),
                "from_kind": row["from_kind"].strip(),
                "from_id": (row["from_id"] or "").strip(),
                "to_kind": row["to_kind"].strip(),
                "to_id": (row["to_id"] or "").strip(),
                "base_usd": float(row["base_usd"]),
                "notes": (row.get("notes") or "").strip(),
            })
    _prices_cache = prices
    return prices
