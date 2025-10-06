# repo/orders.py
import asyncpg
import logging
import json
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

_pool = None
NO_DB = False

log = logging.getLogger("repo.orders")
_pool: asyncpg.Pool | None = None

_FAKE_ID = 0
def _fake_order_id() -> int:
    global _FAKE_ID
    _FAKE_ID -= 1
    return _FAKE_ID

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

async def get_or_create_user_id(con: asyncpg.Connection, tg_id: int, username: str) -> int:
    """
    Находит пользователя по tg_id. Если не найден — создает нового.
    Возвращает внутренний id пользователя.
    """
    # Сначала ищем пользователя
    user_id = await con.fetchval('SELECT id FROM svc."user" WHERE tg_id = $1', tg_id)
    if user_id:
        return user_id

    # Если не нашли, создаем нового
    return await con.fetchval(
        'INSERT INTO svc."user" (tg_id, username, role) VALUES ($1, $2, $3) RETURNING id',
        tg_id, username, 'client'
    )

async def create_order(order: dict) -> int:
    """
    Пишет заказ в БД, либо (если БД недоступна) — работает в NO-DB режиме и возвращает отрицательный id.
    """
    pool = await get_pool()
    if not pool:
        fake_id = _fake_order_id()
        logging.info("NO-DB mode: pretend INSERT order id=%s", fake_id)
        return fake_id

    async with pool.acquire() as con:
        try:
            # Получаем или создаем пользователя и получаем его внутренний ID
            user_id = await get_or_create_user_id(
                con,
                order["client_tg_id"],
                order.get("client_username", f"user_{order['client_tg_id']}")
            )

            # Теперь вставляем заказ с правильным user_id
            # ВНИМАНИЕ: Заменяем client_tg_id на user_id
            row = await con.fetchrow(
                """
                INSERT INTO svc."order"(
                  status, service, user_id, lang,
                  pickup_text, dropoff_text, when_dt, pax,
                  options, price_quote, currency, price_payload
                )
                VALUES ('confirmed','taxi', $1, COALESCE($2,'ru'),
                        $3, $4, $5, COALESCE($6, 1),
                        $7::jsonb, $8, 'USD', $9::jsonb)
                RETURNING id
                """,
                user_id,                              # <--- ИСПРАВЛЕНО
                order.get("lang"),
                order.get("pickup_text", ""),
                order.get("dropoff_text", ""),
                order.get("when_dt"),
                order.get("pax", 1),
                json.dumps(order.get("options", {})),
                order.get("price_quote"),
                json.dumps(order.get("price_payload", {})),
            )
            if not row or "id" not in row:
                raise RuntimeError("INSERT returned no id")

            oid = int(row["id"])
            logging.info("Order inserted id=%s", oid)
            return oid

        except Exception as e:
            logging.exception("create_order failed: %s", e)
            raise