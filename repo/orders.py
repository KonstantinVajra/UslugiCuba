import asyncpg
import logging
import json
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

log = logging.getLogger("repo.orders")
_pool: asyncpg.Pool | None = None
NO_DB = False

async def get_pool() -> asyncpg.Pool | None:
    global _pool, NO_DB
    if _pool:
        return _pool
    if NO_DB:
        return None
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

async def _get_or_create_user_id(con: asyncpg.Connection, tg_id: int, username: str | None) -> int:
    """Finds user in svc.user by tg_id or creates a new one."""
    user_row = await con.fetchrow('SELECT id FROM svc."user" WHERE tg_id = $1', tg_id)
    if user_row:
        return user_row['id']

    return await con.fetchval(
        'INSERT INTO svc."user" (tg_id, username) VALUES ($1, $2) RETURNING id',
        tg_id, username
    )

async def _get_or_create_customer_id(con: asyncpg.Connection, user_id: int, lang: str) -> int:
    """Finds customer in uslugicuba.customers by user_id or creates a new one."""
    customer_row = await con.fetchrow('SELECT id FROM uslugicuba.customers WHERE user_id = $1', user_id)
    if customer_row:
        return customer_row['id']

    return await con.fetchval(
        'INSERT INTO uslugicuba.customers (user_id, lang) VALUES ($1, $2) RETURNING id',
        user_id, lang
    )

async def create_order(order_data: dict) -> int:
    """
    Creates a customer (if not exists) and then an order in the database.
    """
    pool = await get_pool()
    if not pool:
        log.warning("NO-DB mode: Order creation skipped.")
        return -1  # Indicate failure in NO-DB mode

    tg_id = order_data.get("client_tg_id")
    username = order_data.get("username")
    lang = order_data.get("lang", "ru")

    async with pool.acquire() as con:
        async with con.transaction():
            try:
                # 1. Get or create svc.user
                user_id = await _get_or_create_user_id(con, tg_id, username)

                # 2. Get or create uslugicuba.customers
                customer_id = await _get_or_create_customer_id(con, user_id, lang)

                # 3. Create uslugicuba.orders
                # Ensure place details are handled correctly
                pickup = order_data.get("pickup", {})
                dropoff = order_data.get("dropoff", {})

                query = """
                    INSERT INTO uslugicuba.orders (
                        customer_id, service_id, state, date_time, pax,
                        pickup_kind, pickup_id, pickup_text,
                        dropoff_kind, dropoff_id, dropoff_text,
                        meta
                    ) VALUES (
                        $1, NULL, 'new', $2, $3,
                        $4, $5, $6,
                        $7, $8, $9,
                        $10::jsonb
                    ) RETURNING id
                """

                meta = {
                    "service_name": order_data.get("service"),
                    "price_quote": order_data.get("price_quote"),
                    "price_payload": order_data.get("price_payload"),
                    "options": order_data.get("options", {})
                }

                order_id = await con.fetchval(
                    query,
                    customer_id,
                    order_data.get("datetime"),
                    order_data.get("pax", 1),
                    pickup.get("kind"),
                    pickup.get("id"),
                    pickup.get("name"),
                    dropoff.get("kind"),
                    dropoff.get("id"),
                    dropoff.get("name"),
                    json.dumps(meta, ensure_ascii=False)
                )
                log.info(f"Order created with ID: {order_id}")
                return order_id

            except Exception as e:
                log.exception("create_order transaction failed: %s", e)
                raise