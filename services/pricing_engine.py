# services/pricing_engine.py
from __future__ import annotations
from typing import Any, Dict, Optional
from models.order import OrderDraft, PriceBreakdown
from services.zone_pricing import zone_with_defaults

ZONE_ORDER = ["A", "B", "C", "D"]
ZONE_INDEX = {z: i for i, z in enumerate(ZONE_ORDER)}

def _zone_distance(a: str, b: str) -> Optional[int]:
    if a not in ZONE_INDEX or b not in ZONE_INDEX:
        return None
    return abs(ZONE_INDEX[a] - ZONE_INDEX[b])

def _airport_price(zone: str) -> Optional[float]:
    if zone == "D":
        return 40.0
    if zone in {"A", "B"}:
        return 30.0
    if zone == "C":
        return 35.0
    return None

class PricingEngine:
    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        self.options = options or {}

    def compute(self, draft: OrderDraft) -> PriceBreakdown:
        if draft.service != "taxi":
            return PriceBreakdown(0.0, 0.0, [], "n/a")

        z_from = zone_with_defaults(draft.pickup_code or "", draft.pickup_kind)
        z_to   = zone_with_defaults(draft.dropoff_code or "", draft.dropoff_kind)

        # аэропорт
        if z_from == "AIRPORT" and z_to in ZONE_INDEX:
            p = _airport_price(z_to)
            if p is not None:
                return PriceBreakdown(p, p, [], f"airport:{z_to}")
        if z_to == "AIRPORT" and z_from in ZONE_INDEX:
            p = _airport_price(z_from)
            if p is not None:
                return PriceBreakdown(p, p, [], f"airport:{z_from}")

        # зоны A–D
        if z_from in ZONE_INDEX and z_to in ZONE_INDEX:
            pair = {z_from, z_to}
            if pair == {"D", "A"}:
                return PriceBreakdown(30.0, 30.0, [], "zones:D<->A")
            if pair == {"D", "B"}:
                return PriceBreakdown(25.0, 25.0, [], "zones:D<->B")

            dist = _zone_distance(z_from, z_to)
            if dist == 0:
                return PriceBreakdown(10.0, 10.0, [], "zones:same")
            if dist == 1:
                return PriceBreakdown(15.0, 15.0, [], "zones:adjacent")
            if dist == 2:
                return PriceBreakdown(20.0, 20.0, [], "zones:through_one")
            if dist == 3:
                return PriceBreakdown(30.0, 30.0, [], "zones:through_two")

        return PriceBreakdown(0.0, 0.0, [], "no_zone")
