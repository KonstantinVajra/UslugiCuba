# repo/orders.py
import asyncpg
import logging
import json
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE

_pool = None
NO_DB = False

log = logging.getLogger("repo.orders")
_pool: asyncpg.Pool | None = None

_FAKE_ID = 0
def _fake_order_id() -> int:
    """
    Возвращает -1, -2, ... (легко отличать от реальных положительных id из БД)
    """
    global _FAKE_ID
    _FAKE_ID -= 1
    return _FAKE_ID

async def get_pool():
    """
    Возвращает пул подключений к БД или None, если БД недоступна.
    """
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
    """
    Проверка соединения с БД на старте. В NO-DB режиме просто пропускаем.
    """
    pool = await get_pool()
    if not pool:
        logging.warning("Skipping DB ping (NO-DB mode)")
        return

    async with pool.acquire() as conn:
        await conn.execute("SELECT 1")


async def create_order(order: dict) -> int:
    """
    Создает заказ в БД, следуя правильной трехэтапной логике:
    1. Get-or-create `svc.user`
    2. Get-or-create `uslugicuba.customers`
    3. Get `service_id` for 'taxi'
    4. Insert `uslugicuba.orders`
    """
    pool = await get_pool()
    if not pool:
        return _fake_order_id()

    async with pool.acquire() as con:
        try:
            # 1. Get-or-create svc.user
            user_id = await con.fetchval(
                """
                INSERT INTO svc."user" (tg_id, username)
                VALUES ($1, $2)
                ON CONFLICT (tg_id) DO UPDATE SET username = $2
                RETURNING id
                """,
                order["client_tg_id"],
                order.get("username"),
            )

            # 2. Get-or-create uslugicuba.customers
            customer_id = await con.fetchval(
                """
                INSERT INTO uslugicuba.customers (user_id, lang)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET lang = $2
                RETURNING id
                """,
                user_id,
                order.get("lang", "ru"),
            )

            # 3. Get service_id for 'taxi'
            service_id = await con.fetchval(
                "SELECT id FROM uslugicuba.services WHERE category = 'taxi' LIMIT 1"
            )
            if not service_id:
                log.error("Service 'taxi' not found in uslugicuba.services table.")
                raise ValueError("Taxi service not configured in the database")

            # 4. Insert order
            options_json = json.dumps(order.get("options", {}), ensure_ascii=False)
            payload_json = json.dumps(order.get("price_payload", {}), ensure_ascii=False)

            row = await con.fetchrow(
                """
                INSERT INTO uslugicuba.orders(
                  customer_id, service_id, state,
                  pickup_text, dropoff_text, when_at, pax,
                  options, price_quote, currency, price_payload, meta
                )
                VALUES ($1, $2, 'new',
                        $3, $4, $5, COALESCE($6, 1),
                        $7::jsonb, $8, 'USD', $9::jsonb, $10::jsonb)
                RETURNING id
                """,
                customer_id,
                service_id,
                order.get("pickup_text", ""),
                order.get("dropoff_text", ""),
                order.get("when_dt"),
                order.get("pax"),
                options_json,
                order.get("price_quote"),
                payload_json,
                json.dumps({"source_data": order}, ensure_ascii=False, default=str),
            )
            if not row or "id" not in row:
                raise RuntimeError("INSERT returned no id")

            oid = int(row["id"])
            logging.info("Order inserted id=%s (customer_id=%s, user_id=%s)", oid, customer_id, user_id)
            return oid

        except Exception as e:
            logging.exception("create_order failed: %s", e)
            raise