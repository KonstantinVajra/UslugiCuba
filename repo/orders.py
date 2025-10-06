# repo/orders.py
import logging
import json
from datetime import datetime
from .db import get_pool, NO_DB
from .customers import get_or_create_customer_by_tg_id

log = logging.getLogger("repo.orders")

_FAKE_ID = 0
def _fake_order_id() -> int:
    global _FAKE_ID
    _FAKE_ID -= 1
    return _FAKE_ID

async def create_order(order: dict) -> int:
    if NO_DB:
        fake_id = _fake_order_id()
        logging.info("NO-DB mode: pretend INSERT order id=%s", fake_id)
        return fake_id

    pool = await get_pool()
    if not pool:
        raise ConnectionError("DB pool is not available for order creation")

    async with pool.acquire() as con:
        try:
            # 1. Получаем customer_id
            customer_id = await get_or_create_customer_by_tg_id(
                order["client_tg_id"],
                order.get("lang", "ru")
            )

            # 2. Получаем service_id по коду услуги
            service_code = order.get("service")
            service_id = None
            if service_code:
                service_id = await con.fetchval(
                    "SELECT id FROM uslugicuba.services WHERE category = $1 AND active = TRUE",
                    service_code
                )
                if not service_id:
                    log.warning(f"Service with category='{service_code}' not found or not active.")

            # 3. Готовим данные для вставки
            dt_str = order.get("when_dt")
            date_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M") if dt_str else None

            meta_payload = {
                "price_quote": order.get("price_quote"),
                "price_payload": order.get("price_payload", {}),
                "options": order.get("options", {}),
                "client_lang": order.get("lang"),
            }

            # 4. Создаем заказ в uslugicuba.orders
            row = await con.fetchrow(
                """
                INSERT INTO uslugicuba.orders(
                  customer_id, service_id, state, date_time, pax, customer_note, meta,
                  pickup_kind, pickup_text, dropoff_kind, dropoff_text
                )
                VALUES ($1, $2, 'new', $3, $4, $5, $6::jsonb, $7, $8, $9, $10)
                RETURNING id
                """,
                customer_id,
                service_id,
                date_time,
                order.get("pax"),
                order.get("customer_note"),
                json.dumps(meta_payload, ensure_ascii=False),
                order.get("pickup_kind"),
                order.get("pickup_text"),
                order.get("dropoff_kind"),
                order.get("dropoff_text"),
            )
            if not row or "id" not in row:
                raise RuntimeError("INSERT returned no id")

            oid = int(row["id"])
            log.info("Order inserted id=%s in uslugicuba.orders", oid)
            return oid

        except Exception as e:
            log.exception("create_order failed: %s", e)
            raise