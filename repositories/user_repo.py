import asyncpg
import logging
from typing import Dict, Any, Optional

from db.db_config import get_pool

log = logging.getLogger(__name__)

async def get_or_create_provider(tg_id: int, name: str = "Provider") -> Optional[Dict[str, Any]]:
    """
    Находит или создает пользователя и связанный с ним профиль провайдера.
    Если у пользователя нет профиля провайдера, он будет создан.
    """
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        async with conn.transaction():
            # 1. Найти или создать пользователя
            user = await conn.fetchrow("SELECT * FROM svc.user WHERE tg_id = $1", tg_id)
            if not user:
                user = await conn.fetchrow(
                    "INSERT INTO svc.user (tg_id, role) VALUES ($1, 'provider') RETURNING *",
                    tg_id
                )
            elif user['role'] != 'provider':
                await conn.execute("UPDATE svc.user SET role = 'provider' WHERE id = $1", user['id'])

            if not user:
                log.error("Failed to get or create user for tg_id=%d", tg_id)
                return None

            user_id = user['id']

            # 2. Найти или создать профиль провайдера
            provider = await conn.fetchrow("SELECT * FROM svc.provider WHERE user_id = $1", user_id)
            if not provider:
                provider = await conn.fetchrow(
                    "INSERT INTO svc.provider (user_id, name) VALUES ($1, $2) RETURNING *",
                    user_id, name
                )

            return dict(provider) if provider else None