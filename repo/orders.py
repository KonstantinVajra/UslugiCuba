# repo/orders.py
import asyncpg
import logging
import json
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE

log = logging.getLogger("repo.orders")
_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        log.info("Creating DB pool to %s:%s/%s user=%s ssl=%s",
                 DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_SSLMODE)
        _pool = await asyncpg.create_pool(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME, ssl=DB_SSLMODE
        )
    return _pool

async def ping_db():
    pool = await get_pool()
    async with pool.acquire() as con:
        v = await con.fetchval("select 1")
        log.info("DB ping result: %s", v)


async def create_order(order: dict) -> int:
    pool = await get_pool()
    async with pool.acquire() as con:
        try:
            row = await con.fetchrow(
                """
                INSERT INTO svc."order"(
                  status, service, client_tg_id, lang,
                  pickup_text, dropoff_text, when_dt, pax,
                  options, price_quote, currency, price_payload
                )
                VALUES ('confirmed','taxi', $1, COALESCE($2,'ru'),
                        $3, $4, $5, $6,
                        $7::jsonb, $8, 'USD', $9::jsonb)
                RETURNING id
                """,
                order["client_tg_id"],
                order.get("lang"),
                order["pickup_text"],
                order["dropoff_text"],
                order.get("when_dt"),
                order.get("pax"),
                json.dumps(order.get("options", {}), ensure_ascii=False),   # ← fix
                order.get("price_quote"),
                json.dumps(order.get("price_payload", {}), ensure_ascii=False),  # ← fix
            )
            oid = row["id"]
            log.info("Order inserted id=%s", oid)
            return oid
        except Exception as e:
            log.exception("create_order failed: %s", e)
            raise