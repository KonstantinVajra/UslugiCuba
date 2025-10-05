import asyncpg
import logging
from typing import Dict, Any, Optional

from db.db_config import get_pool

log = logging.getLogger(__name__)

async def get_user_by_tg_id(tg_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает пользователя по его Telegram ID."""
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM svc.user WHERE tg_id = $1", tg_id)
        return dict(row) if row else None

async def get_or_create_user(tg_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает пользователя по Telegram ID. Если пользователь не найден, создает нового
    с ролью 'client'.
    """
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Проверяем, существует ли пользователь
            user = await conn.fetchrow("SELECT * FROM svc.user WHERE tg_id = $1", tg_id)
            if user:
                return dict(user)

            # Если нет, создаем нового
            log.info("Creating new user for tg_id=%d", tg_id)
            new_user = await conn.fetchrow(
                "INSERT INTO svc.user (tg_id, role) VALUES ($1, 'client') RETURNING *",
                tg_id
            )
            return dict(new_user) if new_user else None

async def set_user_role(user_id: int, role: str) -> bool:
    """Устанавливает роль для пользователя."""
    pool = await get_pool()
    if not pool:
        return False

    async with pool.acquire() as conn:
        result = await conn.execute("UPDATE svc.user SET role = $1 WHERE id = $2", role, user_id)
        return result == "UPDATE 1"

async def create_provider_profile(user_id: int, name: str) -> Optional[Dict[str, Any]]:
    """Создает профиль поставщика услуг, связанный с пользователем."""
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        try:
            new_provider = await conn.fetchrow(
                "INSERT INTO svc.provider (user_id, name) VALUES ($1, $2) RETURNING *",
                user_id, name
            )
            return dict(new_provider) if new_provider else None
        except asyncpg.PostgresError as e:
            log.error("Failed to create provider profile for user_id=%d: %s", user_id, e)
            return None

async def get_provider_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает профиль поставщика по user_id."""
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM svc.provider WHERE user_id = $1", user_id)
        return dict(row) if row else None

async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает пользователя по его внутреннему ID."""
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        # Нам нужна информация из обеих таблиц: user для tg_id и provider для provider_id
        # Но в данном случае нам нужен только tg_id из user
        row = await conn.fetchrow("SELECT * FROM svc.user WHERE id = $1", user_id)
        return dict(row) if row else None