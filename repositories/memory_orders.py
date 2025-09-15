from __future__ import annotations

from typing import Dict, Optional
from models.order import OrderDraft
from repositories.orders import OrdersRepository

class InMemoryOrdersRepository(OrdersRepository):
    """Простая InMemory-реализация (для разработки/тестов)."""
    def __init__(self) -> None:
        self._store: Dict[int, OrderDraft] = {}
    def save(self, draft: OrderDraft) -> None:
        self._store[draft.user_id] = draft
    def get(self, user_id: int) -> Optional[OrderDraft]:
        return self._store.get(user_id)
    def delete(self, user_id: int) -> None:
        self._store.pop(user_id, None)
