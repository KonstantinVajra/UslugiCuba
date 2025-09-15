from __future__ import annotations

from datetime import date, time, datetime
from typing import Literal, List, Optional
from pydantic import BaseModel, Field

ServiceName = Literal["taxi", "retro", "guide", "photo"]

class OrderDraft(BaseModel):
    """Черновик заказа (состояние диалога)."""
    user_id: int
    service: ServiceName
    pickup_code: Optional[str] = None
    dropoff_code: Optional[str] = None
    when_date: Optional[date] = None
    when_time: Optional[time] = None
    tz: Optional[str] = None
    language: Optional[str] = None
    notes: Optional[str] = None

    def when_datetime(self) -> Optional[datetime]:
        if self.when_date and self.when_time:
            return datetime.combine(self.when_date, self.when_time)
        return None

class PriceBreakdown(BaseModel):
    total_usd: float = 0.0
    base_usd: float = 0.0
    mods: List[str] = Field(default_factory=list)
    rule: Optional[str] = None
