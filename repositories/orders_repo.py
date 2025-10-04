import logging
import json
from db.db_config import get_db_pool

log = logging.getLogger(__name__)

async def ensure_customer(tg_user_id: int, tg_username: str | None) -> int:
    """
    Находит или создаёт клиента в таблице customers и возвращает его ID.
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        # Сначала пытаемся найти клиента
        customer_id = await conn.fetchval(
            "SELECT id FROM uslugicuba.customers WHERE tg_user_id = $1",
            tg_user_id
        )
        if customer_id:
            log.info(f"Found existing customer id={customer_id} for tg_user_id={tg_user_id}")
            return customer_id

        # Если не нашли, создаём нового
        log.info(f"Creating new customer for tg_user_id={tg_user_id} username='{tg_username}'")
        try:
            new_customer_id = await conn.fetchval(
                """
                INSERT INTO uslugicuba.customers (tg_user_id, tg_username)
                VALUES ($1, $2)
                RETURNING id;
                """,
                tg_user_id, tg_username
            )
            return new_customer_id
        except Exception:
            log.exception("Failed to ensure_customer for tg_user_id=%s", tg_user_id)
            raise

async def create_order(
    customer_id: int,
    service_id: int,
    city_id: int | None,
    zone_id: int | None,
    pax: int | None,
    note: str | None,
    vehicle_id: int | None,
    meta: dict | None
) -> int:
    """Создаёт новый заказ в таблице orders и возвращает его ID."""
    pool = get_db_pool()
    meta_json = json.dumps(meta or {})
    log.info(
        "Creating order: customer_id=%s, service_id=%s, city_id=%s, zone_id=%s, vehicle_id=%s",
        customer_id, service_id, city_id, zone_id, vehicle_id
    )
    query = """
        INSERT INTO uslugicuba.orders
        (customer_id, service_id, city_id, zone_id, date_time, pax, customer_note, meta, vehicle_id)
        VALUES ($1, $2, $3, $4, NOW(), $5, $6, COALESCE($7, '{}'::jsonb), $8)
        RETURNING id;
    """
    async with pool.acquire() as conn:
        try:
            order_id = await conn.fetchval(
                query,
                customer_id, service_id, city_id, zone_id, pax, note, meta_json, vehicle_id
            )
            log.info(f"Successfully created order_id={order_id}")
            return order_id
        except Exception:
            log.exception("Failed to create_order")
            raise

async def add_event(
    order_id: int,
    event: str,
    actor_type: str,
    actor_id: int | None,
    payload: dict | None
):
    """Добавляет событие в лог order_events."""
    pool = get_db_pool()
    payload_json = json.dumps(payload or {})
    log.info(
        "Adding event: order_id=%s, event='%s', actor='%s:%s'",
        order_id, event, actor_type, actor_id
    )
    query = """
        INSERT INTO uslugicuba.order_events
        (order_id, event, actor_type, actor_id, payload)
        VALUES ($1, $2, $3, $4, COALESCE($5, '{}'::jsonb));
    """
    async with pool.acquire() as conn:
        try:
            await conn.execute(query, order_id, event, actor_type, actor_id, payload_json)
        except Exception:
            log.exception("Failed to add_event for order_id=%s", order_id)
            raise