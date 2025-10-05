import asyncpg
import logging
from typing import Dict, Any, Optional, List

from db.db_config import get_pool

log = logging.getLogger(__name__)

async def add_vehicle(provider_id: int, data: Dict[str, Any], status: str) -> Optional[Dict[str, Any]]:
    """
    Добавляет новый автомобиль в БД для указанного поставщика с заданным статусом.
    """
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        try:
            new_vehicle = await conn.fetchrow(
                """
                INSERT INTO svc.vehicle (
                    provider_id, title, description, photo_file_ids, seats,
                    price_per_hour, price_details, status
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
                """,
                provider_id,
                data.get("title"),
                data.get("description"),
                data.get("photo_file_ids"),
                data.get("seats"),
                data.get("price_per_hour"),
                data.get("price_details"),
                status,
            )
            return dict(new_vehicle) if new_vehicle else None
        except asyncpg.PostgresError as e:
            log.error("Failed to add vehicle for provider_id=%d: %s", provider_id, e)
            return None

async def get_published_vehicles() -> List[Dict[str, Any]]:
    """
    Возвращает список всех автомобилей со статусом 'published'.
    """
    pool = await get_pool()
    if not pool:
        return []

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT v.*, p.name as provider_name, u.tg_id as provider_tg_id
            FROM svc.vehicle v
            JOIN svc.provider p ON v.provider_id = p.id
            JOIN svc.user u ON p.user_id = u.id
            WHERE v.status = 'published'
            ORDER BY v.id
            """
        )
        return [dict(row) for row in rows]