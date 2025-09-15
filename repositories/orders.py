from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from models.order import OrderDraft

class OrdersRepository(ABC):
    """Интерфейс репозитория заказов."""
    @abstractmethod
    def save(self, draft: OrderDraft) -> None: ...
    @abstractmethod
    def get(self, user_id: int) -> Optional[OrderDraft]: ...
    @abstractmethod
    def delete(self, user_id: int) -> None: ...
