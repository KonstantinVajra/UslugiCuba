# pricing.py — работает с CSV-схемой: rule_type + from_type/from_code/to_type/to_code/price_usd

from __future__ import annotations
import os, csv
from functools import lru_cache
from datetime import time
from typing import Optional, Tuple

# ───────────── Модификаторы ─────────────

def is_night(hhmm: Optional[str]) -> bool:
    if not hhmm or hhmm == "now":
        return False
    hh, mm = map(int, hhmm.split(":"))
    t = time(hh, mm)
    # ночь 22:00–06:00
    return t >= time(22, 0) or t < time(6, 0)

def _apply_mods(base: float, when_hhmm: Optional[str], options: dict):
    total = float(base)
    mods = []
    if is_night(when_hhmm):
        add = round(base * 0.20, 2)
        total += add
        mods.append({"type": "night_pct", "value": 0.2, "add_usd": add})
    if options.get("child_seat"):
        total += 5.0
        mods.append({"type": "child_seat_usd", "value": 5.0})
    return round(total, 2), mods

# ───────────── Загрузка справочников ─────────────

@lru_cache
def _load_prices_rows():
    path = os.path.join(os.path.dirname(__file__), "data", "prices.csv")
    rows = []
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows

@lru_cache
def _load_locations_map():
    path = os.path.join(os.path.dirname(__file__), "data", "locations.csv")
    id2 = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            _id   = (r.get("id")   or "").strip()
            kind  = (r.get("kind") or "").strip().lower()
            zone  = (r.get("zone") or "").strip().upper()
            if not _id:
                continue
            # код для аэропорта — его id в верхнем регистре (VRA/HAV),
            # для остальных — используем зону
            code = _id.upper() if kind == "airport" else zone
            id2[_id] = {"kind": kind, "zone": zone, "code": code, "name": r.get("name", "")}
    return id2

# ───────────── Основная функция ─────────────

def quote_price(
    service: str,
    from_kind: str, from_id: Optional[str],
    to_kind:   str, to_id:   Optional[str],
    when_hhmm: Optional[str] = None,
    options:   Optional[dict] = None,
) -> Tuple[float, dict]:
    """
    Возвращает (цена_usd, payload) по CSV-правилам:
      - airport↔airport (rule_type=airport_airport, code=VRA/HAV)
      - airport↔zone    (rule_type=airport_zone,    to_code=A/B/C/D)
      - zone↔zone       (rule_type=zone_zone,       A↔B и т.п.)
      - intra_zone      (rule_type=intra_zone,      A↔A и т.п.)
    """
    options = options or {}
    prices  = _load_prices_rows()
    locmap  = _load_locations_map()

    fk = (from_kind or "").lower()
    tk = (to_kind   or "").lower()
    fid = (from_id or "").strip()
    tid = (to_id   or "").strip()

    fzone = locmap.get(fid, {}).get("zone", "")
    tzone = locmap.get(tid, {}).get("zone", "")
    facode = locmap.get(fid, {}).get("code", "")  # VRA/HAV для airport
    tacode = locmap.get(tid, {}).get("code", "")

    # 1) airport↔airport
    if fk == "airport" and tk == "airport" and facode and tacode:
        for r in prices:
            if r["rule_type"] == "airport_airport" and r["from_type"] == "airport" and r["to_type"] == "airport":
                if r["from_code"].upper() == facode.upper() and r["to_code"].upper() == tacode.upper():
                    base = float(r["price_usd"])
                    total, mods = _apply_mods(base, when_hhmm, options)
                    return total, {"rule": "airport_airport", "base_usd": base, "mods": mods}

    # 2) airport↔zone (hotel/restaurant считаем по зоне)
    if fk == "airport" and tzone:
        for r in prices:
            if r["rule_type"] == "airport_zone" and r["from_type"] == "airport" and r["to_type"] == "zone":
                if r["from_code"].upper() == facode.upper() and r["to_code"].upper() == tzone.upper():
                    base = float(r["price_usd"])
                    total, mods = _apply_mods(base, when_hhmm, options)
                    return total, {"rule": "airport_zone", "base_usd": base, "mods": mods}
    if tk == "airport" and fzone:
        for r in prices:
            if r["rule_type"] == "airport_zone" and r["from_type"] == "zone" and r["to_type"] == "airport":
                if r["from_code"].upper() == fzone.upper() and r["to_code"].upper() == tacode.upper():
                    base = float(r["price_usd"])
                    total, mods = _apply_mods(base, when_hhmm, options)
                    return total, {"rule": "airport_zone", "base_usd": base, "mods": mods}

    # 3) зона↔зона
    if fzone and tzone:
        if fzone.upper() == tzone.upper():
            # intra_zone
            for r in prices:
                if r["rule_type"] == "intra_zone" and r["from_type"] == "zone" and r["to_type"] == "zone":
                    if r["from_code"].upper() == fzone.upper() and r["to_code"].upper() == tzone.upper():
                        base = float(r["price_usd"])
                        total, mods = _apply_mods(base, when_hhmm, options)
                        return total, {"rule": "intra_zone", "base_usd": base, "mods": mods}
        else:
            for r in prices:
                if r["rule_type"] == "zone_zone" and r["from_type"] == "zone" and r["to_type"] == "zone":
                    if r["from_code"].upper() == fzone.upper() and r["to_code"].upper() == tzone.upper():
                        base = float(r["price_usd"])
                        total, mods = _apply_mods(base, when_hhmm, options)
                        return total, {"rule": "zone_zone", "base_usd": base, "mods": mods}

    # Ничего не нашли
    return 0.0, {"rule": "not_found"}
