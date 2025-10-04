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
        # ↓↓↓ оставь свои параметры/переменные (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, ssl и т.д.)
        _pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            ssl="require",  # или как у тебя было
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
    Пишет заказ в БД, либо (если БД недоступна) — работает в NO-DB режиме и возвращает отрицательный id.
    """
    # Безопасно готовим JSON-поля один раз
    options_json = json.dumps(order.get("options", {}), ensure_ascii=False)
    payload_json = json.dumps(order.get("price_payload", {}), ensure_ascii=False)

    # Пытаемся получить пул. Если get_pool упадёт — переключаемся в NO-DB.
    try:
        pool = await get_pool()
    except Exception as e:
        logging.warning("get_pool() failed: %s — NO-DB mode, order will not be persisted", e)
        pool = None

    if not pool:
        # NO-DB режим: не валимся, а отрабатываем "вхолостую"
        fake_id = _fake_order_id()
        logging.info(
            "NO-DB mode: pretend INSERT order id=%s | pickup=%r -> dropoff=%r | price=%r",
            fake_id, order.get("pickup_text"), order.get("dropoff_text"), order.get("price_quote")
        )
        return fake_id

    # Обычный путь: пишем в БД
    async with pool.acquire() as con:
        try:
            row = await con.fetchrow(
                """
                INSERT INTO svc."order"(
                  status, service, client_tg_id, lang,
                  pickup_text, dropoff_text, when_dt, pax,
                  options, price_quote, currency, price_payload
                )
                VALUES ('confirmed', $1, $2, COALESCE($3,'ru'),
                        $4, $5, $6, COALESCE($7, 1),
                        $8::jsonb, $9, 'USD', $10::jsonb)
                RETURNING id
                """,
                order.get("service", "taxi"),
                order["client_tg_id"],
                order.get("lang"),
                order.get("pickup_text", ""),
                order.get("dropoff_text", ""),
                order.get("when_dt"),
                order.get("pax"),
                options_json,
                order.get("price_quote"),
                payload_json,
            )
            if not row or "id" not in row:
                raise RuntimeError("INSERT returned no id")

            oid = int(row["id"])
            logging.info("Order inserted id=%s", oid)
            return oid

        except Exception as e:
            logging.exception("create_order failed: %s", e)
            # На проде — лучше пробрасывать; в деве можно fallback'нуться
            raise
