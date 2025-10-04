# repo/orders.py
import logging
import json
from db.db_config import get_db_pool

log = logging.getLogger("repo.orders")

async def create_order(order: dict) -> int:
    """
    Пишет заказ в БД.
    """
    pool = get_db_pool() # Получаем пул, инициализированный на старте

    # Безопасно готовим JSON-поля один раз
    options_json = json.dumps(order.get("options", {}), ensure_ascii=False)
    payload_json = json.dumps(order.get("price_payload", {}), ensure_ascii=False)

    async with pool.acquire() as con:
        try:
            # Запрос из старой версии, может потребовать адаптации к новой схеме
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
            log.info("Order inserted id=%s", oid)
            return oid

        except Exception:
            log.exception("create_order failed")
            raise
