# bots/client_bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import CLIENT_BOT_TOKEN
from middlewares.i18n import I18nMiddleware
from handlers.client import service_selection, taxi_flow, cars
from handlers.admin import car_admin
from db.db_config import init_db_pool, close_db_pool

# --- Logging setup ---
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("client_bot")


async def run_client_bot():
    """Initializes and runs the client bot."""
    bot = Bot(token=CLIENT_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # Register startup and shutdown handlers for the database pool
    dp.startup.register(init_db_pool)
    dp.shutdown.register(close_db_pool)

    # Register middlewares
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Include all the routers
    dp.include_router(car_admin.router)
    dp.include_router(service_selection.router)
    dp.include_router(taxi_flow.router)
    dp.include_router(cars.router)

    logger.info("Starting polling...")

    # Start the bot
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)