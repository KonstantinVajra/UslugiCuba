from __future__ import annotations

from typing import Any, Dict, Optional
from models.order import OrderDraft, PriceBreakdown

class PricingEngine:
    """
    Обёртка над расчётом цены.
    Сейчас — безопасный каркас: при подключении к существующему pricing.py
    можно прокинуть вызовы внутрь. Пока — не меняет поведение бота.
    """
    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        self.options = options or {}
    def compute(self, draft: OrderDraft) -> PriceBreakdown:
        # TODO: подключить фактический расчёт из pricing.py
        return PriceBreakdown()
