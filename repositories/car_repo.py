import asyncpg
import logging
from typing import List, Dict, Any

from db.db_config import get_pool

log = logging.getLogger(__name__)


async def get_all_published_cars() -> List[Dict[str, Any]]:
    """Возвращает список всех опубликованных автомобилей."""
    pool = await get_pool()
    if not pool:
        log.warning("DB pool is not available.")
        return []

    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("SELECT * FROM cars WHERE status = 'published' ORDER BY id")
            return [dict(row) for row in rows]
        except asyncpg.PostgresError as e:
            log.error("Failed to fetch published cars: %s", e)
            return []


async def get_car_by_id(car_id: int) -> Dict[str, Any] | None:
    """Возвращает данные автомобиля по его ID."""
    pool = await get_pool()
    if not pool:
        log.warning("DB pool is not available.")
        return None

    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("SELECT * FROM cars WHERE id = $1", car_id)
            return dict(row) if row else None
        except asyncpg.PostgresError as e:
            log.error("Failed to fetch car by id %d: %s", car_id, e)
            return None

# --- Admin functions ---

async def add_car(car_data: Dict[str, Any]) -> int | None:
    """Добавляет новый автомобиль в БД."""
    pool = await get_pool()
    if not pool:
        log.warning("DB pool is not available. Cannot add car.")
        return None

    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO cars (name, brand, model, year, color, engine, transmission, fuel, price, image_url, description, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'published')
                RETURNING id
                """,
                car_data.get("name"),
                car_data.get("brand"),
                car_data.get("model"),
                car_data.get("year"),
                car_data.get("color"),
                car_data.get("engine"),
                car_data.get("transmission"),
                car_data.get("fuel"),
                car_data.get("price"),
                car_data.get("image_url"),
                car_data.get("description"),
            )
            car_id = dict(row)["id"] if row else None
            if car_id:
                log.info("Successfully added car with id %d", car_id)
            return car_id
        except asyncpg.PostgresError as e:
            log.error("Failed to add car: %s", e)
            return None


async def update_car_status(car_id: int, status: str) -> bool:
    """Обновляет статус автомобиля (например, 'published', 'archived')."""
    pool = await get_pool()
    if not pool:
        log.warning("DB pool is not available. Cannot update car status.")
        return False

    async with pool.acquire() as conn:
        try:
            result = await conn.execute(
                "UPDATE cars SET status = $1, updated_at = now() WHERE id = $2",
                status, car_id
            )
            if result == "UPDATE 1":
                log.info("Successfully updated status for car %d to '%s'", car_id, status)
                return True
            log.warning("Car with id %d not found for status update.", car_id)
            return False
        except asyncpg.PostgresError as e:
            log.error("Failed to update car status for car %d: %s", car_id, e)
            return False


async def create_car_order(order_data: Dict[str, Any]) -> int | None:
    """Сохраняет заявку на аренду автомобиля в БД."""
    pool = await get_pool()
    if not pool:
        log.warning("DB pool is not available. Car order cannot be saved.")
        return None

    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO car_orders (car_id, client_name, client_phone, client_comment, client_tg_id)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                order_data.get("car_id"),
                order_data.get("name"),
                order_data.get("phone"),
                order_data.get("comment"),
                order_data.get("tg_id"),
            )
            order_id = dict(row)["id"] if row else None
            if order_id:
                log.info("Successfully created car order with id %d", order_id)
            return order_id
        except asyncpg.PostgresError as e:
            log.error("Failed to create car order: %s", e)
            return None