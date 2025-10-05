import asyncpg
import logging
from typing import Dict, Any, Optional

from db.db_config import get_pool

log = logging.getLogger(__name__)

async def create_order(order_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новый заказ в таблице svc.order.
    """
    pool = await get_pool()
    if not pool:
        log.warning("DB pool is not available. Cannot create order.")
        return None

    async with pool.acquire() as conn:
        try:
            # Обратите внимание, что scheduled_at, pickup_location, dropoff_location не используются
            # в текущей FSM, но могут быть добавлены в будущем.
            row = await conn.fetchrow(
                """
                INSERT INTO svc.order (client_user_id, provider_id, service_id, vehicle_id, price, client_comment, status)
                VALUES ($1, $2, $3, $4, $5, $6, 'new')
                RETURNING id
                """,
                order_data.get("client_user_id"),
                order_data.get("provider_id"),
                order_data.get("service_id"),
                order_data.get("vehicle_id"),
                order_data.get("price"),
                order_data.get("client_comment"),
            )
            order_id = dict(row)["id"] if row else None
            if order_id:
                log.info("Successfully created order with id %d", order_id)
            return order_id
        except asyncpg.PostgresError as e:
            log.error("Failed to create order: %s", e)
            return None