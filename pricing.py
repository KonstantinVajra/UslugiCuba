# pricing.py
from __future__ import annotations
from typing import Optional, Tuple
from datetime import time

from data_loader import load_prices

def is_night(hhmm: str | None) -> bool:
    if not hhmm or hhmm == "now":
        return False
    hh, mm = map(int, hhmm.split(":"))
    t = time(hh, mm)
    # ночь 22:00–06:00
    return t >= time(22, 0) or t < time(6, 0)

def quote_price(
    service: str,
    from_kind: str, from_id: Optional[str],
    to_kind: str, to_id: Optional[str],
    when_hhmm: Optional[str] = None,
    options: Optional[dict] = None,
) -> Tuple[float, dict]:
    """
    Возвращает (цена_usd, payload)
    Приоритет подбора тарифа:
      1) from_id+to_id
      2) from_kind+to_kind
      3) fallback: airport<->city / city<->city (если такие правила есть в CSV)
    Модификаторы: ночь +20%, деткресло +5 USD
    """
    prices = load_prices()
    options = options or {}

    # 1) точное совпадение id
    for r in prices:
        if r["service"] != service:
            continue
        if r["from_id"] and r["to_id"]:
            if r["from_kind"] == from_kind and r["to_kind"] == to_kind \
               and r["from_id"] == (from_id or "") and r["to_id"] == (to_id or ""):
                base = r["base_usd"]; payload = {"rule": "id->id", "base_usd": base}
                return apply_modifiers(base, when_hhmm, options, payload)

    # 2) совпадение по видам (kind)
    for r in prices:
        if r["service"] != service:
            continue
        if not r["from_id"] and not r["to_id"]:
            if r["from_kind"] == from_kind and r["to_kind"] == to_kind:
                base = r["base_usd"]; payload = {"rule": "kind->kind", "base_usd": base}
                return apply_modifiers(base, when_hhmm, options, payload)

    # 3) fallback — ищем любое airport->city и т.п.
    for r in prices:
        if r["service"] != service:
            continue
        if r["from_kind"] == from_kind and r["to_kind"] == to_kind:
            base = r["base_usd"]; payload = {"rule": "fallback", "base_usd": base}
            return apply_modifiers(base, when_hhmm, options, payload)

    # если ничего не нашли — вернём 0 и пустой payload (бот пусть обработает красиво)
    return 0.0, {"rule": "not_found"}

def apply_modifiers(base: float, when_hhmm: Optional[str], options: dict, payload: dict):
    total = base
    mods = []

    if is_night(when_hhmm):
        night_add = round(base * 0.2, 2)
        total += night_add
        mods.append({"type": "night_pct", "value": 0.2, "add_usd": night_add})

    if options.get("child_seat"):
        total += 5.0
        mods.append({"type": "child_seat_usd", "value": 5.0})

    payload = {**payload, "mods": mods}
    return round(total, 2), payload
