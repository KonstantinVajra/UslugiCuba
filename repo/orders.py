# repo/orders.py
import asyncpg
import logging
import json
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

_pool = None
NO_DB = False

log = logging.getLogger("repo.orders")
_pool: asyncpg.Pool | None = None

async def get_pool():
    global _pool, NO_DB
    if _pool or NO_DB:
        return _pool

    try:
        _pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            ssl="require",
        )
        return _pool
    except Exception as e:
        logging.warning("DB pool init failed: %s — continuing without DB", e)
        NO_DB = True
        return None

async def ping_db():
    pool = await get_pool()
    if not pool:
        logging.warning("Skipping DB ping (NO-DB mode)")
        return
    async with pool.acquire() as conn:
        await conn.execute("SELECT 1")

async def get_or_create_user_id(con: asyncpg.Connection, tg_id: int, username: str) -> int:
    """Находит пользователя по tg_id. Если не найден — создает нового. Возвращает внутренний id."""
    user_id = await con.fetchval('SELECT id FROM svc."user" WHERE tg_id = $1', tg_id)
    if user_id:
        return user_id
    return await con.fetchval(
        'INSERT INTO svc."user" (tg_id, username, role) VALUES ($1, $2, $3) RETURNING id',
        tg_id, username, 'client'
    )

async def get_service_id(con: asyncpg.Connection, category: str) -> int | None:
    """Получает ID услуги по ее категории."""
    # Для такси и кабриолетов используем одну и ту же услугу 'taxi'
    if category in ('taxi', 'cabrio'):
        category = 'taxi'
    return await con.fetchval("SELECT id FROM uslugicuba.services WHERE category = $1 LIMIT 1", category)


async def create_order(order: dict) -> int:
    """Пишет заказ в БД в соответствии с правильной схемой."""
    pool = await get_pool()
    if not pool:
        log.warning("NO-DB mode: order will not be persisted")
        return -1

    async with pool.acquire() as con:
        try:
            # 1. Получаем/создаем ID клиента
            customer_id = await get_or_create_user_id(
                con,
                order["client_tg_id"],
                order.get("client_username", f"user_{order['client_tg_id']}")
            )

            # 2. Получаем ID сервиса (для такси)
            service_id = await get_service_id(con, "taxi")
            if not service_id:
                log.error("Service 'taxi' not found in uslugicuba.services")
                raise ValueError("Taxi service not configured in DB")

            # 3. Собираем мета-данные
            meta_data = {
                "lang": order.get("lang"),
                "price_quote": order.get("price_quote"),
                "price_payload": order.get("price_payload", {}),
                "pickup_details": order.get("pickup_text"),
                "dropoff_details": order.get("dropoff_text"),
            }
            if order.get("options", {}).get("selected_car"):
                 meta_data["selected_car"] = order.get("options", {}).get("selected_car")

            # 4. Вставляем заказ в uslugicuba.orders
            row = await con.fetchrow(
                """
                INSERT INTO uslugicuba.orders(
                  customer_id, service_id, state,
                  date_time, pax, customer_note, meta
                )
                VALUES ($1, $2, 'confirmed', $3, $4, $5, $6::jsonb)
                RETURNING id
                """,
                customer_id,
                service_id,
                order.get("when_dt"),
                order.get("pax", 1),
                order.get("customer_note", ""),
                json.dumps(meta_data)
            )
            if not row or "id" not in row:
                raise RuntimeError("INSERT into uslugicuba.orders returned no id")

            oid = int(row["id"])
            log.info("Order inserted into uslugicuba.orders with id=%s", oid)
            return oid

        except Exception as e:
            log.exception("create_order failed with correct schema: %s", e)
            raise