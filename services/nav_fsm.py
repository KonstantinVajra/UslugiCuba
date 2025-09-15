# services/nav_fsm.py
from __future__ import annotations
from typing import Any, Dict, Optional, List
from aiogram.fsm.context import FSMContext

_STACK_KEY = "back_stack"

async def push(ctx: FSMContext, snapshot: Dict[str, Any]) -> None:
    """
    snapshot: {"screen": "choose_to", "args": {...}} — любые ваши данные для восстановления экрана.
    """
    data = await ctx.get_data()
    stack: List[Dict[str, Any]] = data.get(_STACK_KEY, [])
    stack.append(snapshot)
    await ctx.update_data(**{_STACK_KEY: stack})

async def pop(ctx: FSMContext) -> Optional[Dict[str, Any]]:
    data = await ctx.get_data()
    stack: List[Dict[str, Any]] = data.get(_STACK_KEY, [])
    snap = stack.pop() if stack else None
    await ctx.update_data(**{_STACK_KEY: stack})
    return snap

async def clear(ctx: FSMContext) -> None:
    await ctx.update_data(**{_STACK_KEY: []})
