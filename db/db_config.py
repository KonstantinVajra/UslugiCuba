import asyncpg
import logging
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

_pool: asyncpg.Pool | None = None
NO_DB = False

log = logging.getLogger(__name__)

async def init_db_pool():
    """Инициализирует пул соединений с БД."""
    global _pool, NO_DB
    if _pool:
        return

    try:
        _pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            ssl="require",
        )
        log.info("Database pool created successfully.")
    except Exception as e:
        log.warning("DB pool init failed: %s — continuing without DB", e)
        NO_DB = True
        _pool = None

async def close_db_pool():
    """Закрывает пул соединений с БД."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        log.info("Database pool closed.")

async def get_pool() -> asyncpg.Pool | None:
    """Возвращает текущий пул соединений."""
    return _pool