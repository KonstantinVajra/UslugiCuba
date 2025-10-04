import asyncpg
import logging
from config import config

log = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None

async def init_db_pool():
    """
    Initializes the database connection pool.
    Must be called at application startup.
    """
    global _pool
    if _pool:
        return

    try:
        log.info(
            "Connecting to PostgreSQL: host=%s port=%s db=%s user=%s",
            config.DB_HOST, config.DB_PORT, config.DB_NAME, config.DB_USER
        )
        _pool = await asyncpg.create_pool(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            ssl=config.DB_SSLMODE,
            min_size=1,
            max_size=5,
        )
        # Test connection
        async with _pool.acquire() as conn:
            await conn.execute("SELECT 1")
        log.info("Database connection pool initialized successfully.")
    except Exception:
        log.exception("Failed to initialize database connection pool.")
        raise

def get_db_pool() -> asyncpg.Pool:
    """
    Returns the existing database connection pool.
    Raises an exception if the pool is not initialized.
    """
    if _pool is None:
        raise RuntimeError(
            "Database pool is not initialized. Call init_db_pool() at startup."
        )
    return _pool

async def close_db_pool():
    """
    Closes the database connection pool.
    Must be called at application shutdown.
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        log.info("Database connection pool closed.")