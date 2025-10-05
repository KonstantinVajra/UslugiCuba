import asyncpg
import logging
from typing import Dict, Any, Optional, List

from db.db_config import get_pool

log = logging.getLogger(__name__)

async def add_vehicle(provider_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Добавляет новый автомобиль в БД для указанного поставщика."""
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        try:
            new_vehicle = await conn.fetchrow(
                """
                INSERT INTO svc.vehicle (provider_id, make, model, year, color, engine, transmission, fuel, price, photo_url, description)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """,
                provider_id,
                data.get("make"),
                data.get("model"),
                data.get("year"),
                data.get("color"),
                data.get("engine"),
                data.get("transmission"),
                data.get("fuel"),
                data.get("price"),
                data.get("photo_url"),
                data.get("description"),
            )
            return dict(new_vehicle) if new_vehicle else None
        except asyncpg.PostgresError as e:
            log.error("Failed to add vehicle for provider_id=%d: %s", provider_id, e)
            return None

async def get_vehicles_by_provider(provider_id: int) -> List[Dict[str, Any]]:
    """Возвращает список автомобилей для указанного поставщика."""
    pool = await get_pool()
    if not pool:
        return []

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM svc.vehicle WHERE provider_id = $1 ORDER BY created_at DESC", provider_id)
        return [dict(row) for row in rows]

async def get_approved_vehicles() -> List[Dict[str, Any]]:
    """Возвращает список всех одобренных автомобилей для карусели."""
    pool = await get_pool()
    if not pool:
        return []

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT v.*, p.name as provider_name FROM svc.vehicle v JOIN svc.provider p ON v.provider_id = p.id WHERE v.is_approved = TRUE ORDER BY v.id")
        return [dict(row) for row in rows]

async def get_vehicles_for_moderation() -> List[Dict[str, Any]]:
    """Возвращает список автомобилей, ожидающих модерации."""
    pool = await get_pool()
    if not pool:
        return []

    async with pool.acquire() as conn:
        # Выбираем автомобили, которые еще не были одобрены
        rows = await conn.fetch(
            "SELECT v.*, p.name as provider_name FROM svc.vehicle v "
            "JOIN svc.provider p ON v.provider_id = p.id "
            "WHERE v.is_approved IS FALSE "
            "ORDER BY v.created_at ASC"
        )
        return [dict(row) for row in rows]

async def get_vehicle_by_id(vehicle_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает детальную информацию об автомобиле по его ID."""
    pool = await get_pool()
    if not pool:
        return None

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT v.*, p.name as provider_name FROM svc.vehicle v JOIN svc.provider p ON v.provider_id = p.id WHERE v.id = $1", vehicle_id)
        return dict(row) if row else None

async def update_vehicle_status(vehicle_id: int, is_approved: bool) -> bool:
    """Обновляет статус одобрения автомобиля."""
    pool = await get_pool()
    if not pool:
        return False

    async with pool.acquire() as conn:
        result = await conn.execute("UPDATE svc.vehicle SET is_approved = $1, updated_at = now() WHERE id = $2", is_approved, vehicle_id)
        return result == "UPDATE 1"