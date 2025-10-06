# repo/db.py
import asyncpg
import logging
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE

_pool: asyncpg.Pool | None = None
NO_DB = False

async def get_pool():
    """
    Возвращает пул подключений к БД или None, если БД недоступна.
    """
    global _pool, NO_DB
    if _pool or NO_DB:
        return _pool
    try:
        _pool = await asyncpg.create_pool(
            host=DB_HOST, port=int(DB_PORT), database=DB_NAME,
            user=DB_USER, password=DB_PASSWORD, ssl="require",
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