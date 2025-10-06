# repo/customers.py
import logging
from .db import get_pool

log = logging.getLogger(__name__)

async def get_or_create_customer_by_tg_id(tg_id: int, lang: str = 'ru') -> int:
    """
    Находит или создает пользователя в svc.user и клиента в uslugicuba.customers.
    Возвращает ID клиента (customers.id).
    """
    pool = await get_pool()
    if not pool:
        raise ConnectionError("DB pool is not available")

    async with pool.acquire() as con:
        async with con.transaction():
            # 1. Найти или создать пользователя в svc.user
            user_id = await con.fetchval(
                """
                INSERT INTO svc."user" (tg_id)
                VALUES ($1)
                ON CONFLICT (tg_id) DO UPDATE SET tg_id = $1
                RETURNING id;
                """,
                tg_id
            )

            # 2. Найти или создать клиента в uslugicuba.customers
            customer_id = await con.fetchval(
                """
                SELECT id FROM uslugicuba.customers WHERE user_id = $1
                """,
                user_id
            )

            if customer_id:
                return customer_id

            customer_id = await con.fetchval(
                """
                INSERT INTO uslugicuba.customers (user_id, lang)
                VALUES ($1, $2)
                RETURNING id;
                """,
                user_id, lang
            )
            log.info(f"Created new customer with id={customer_id} for user_id={user_id} (tg_id={tg_id})")
            return customer_id