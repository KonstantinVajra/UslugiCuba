from __future__ import annotations
from typing import List, Optional, Any

class BackStack:
    """Стек шагов для кнопки «Назад»."""
    def __init__(self) -> None:
        self._stack: List[Any] = []
    def push(self, snapshot: Any) -> None:
        self._stack.append(snapshot)
    def pop(self) -> Optional[Any]:
        if self._stack:
            return self._stack.pop()
        return None
    def clear(self) -> None:
        self._stack.clear()
