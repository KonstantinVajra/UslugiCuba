# repositories/orders.py
import logging
import json
from db.db_config import get_pool

log = logging.getLogger("repositories.orders")

_FAKE_ID = 0
def _fake_order_id() -> int:
    """
    Возвращает -1, -2, ... (легко отличать от реальных положительных id из БД)
    """
    global _FAKE_ID
    _FAKE_ID -= 1
    return _FAKE_ID



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
                VALUES ('confirmed','taxi', $1, COALESCE($2,'ru'),
                        $3, $4, $5, COALESCE($6, 1),
                        $7::jsonb, $8, 'USD', $9::jsonb)
                RETURNING id
                """,
                order["client_tg_id"],                # обязательное поле
                order.get("lang"),                    # может быть None — COALESCE -> 'ru'
                order.get("pickup_text", ""),         # в твоём сценарии это строка
                order.get("dropoff_text", ""),
                order.get("when_dt"),                 # строка/datetime — как у тебя заведено
                order.get("pax"),                     # если None — COALESCE -> 1
                options_json,                         # jsonb
                order.get("price_quote"),             # число/Decimal — как у тебя заведено
                payload_json,                         # jsonb
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
