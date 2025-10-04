# bots/client_bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import CLIENT_BOT_TOKEN
from middlewares.i18n import I18nMiddleware
from handlers.client import service_selection, taxi_flow
from db.db_config import init_db_pool, close_db_pool


# +++ ЛОГИ
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("client_bot")


async def run_client_bot():
    bot = Bot(token=CLIENT_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    dp.include_router(service_selection.router)
    dp.include_router(taxi_flow.router)

    # Инициализируем пул соединений с БД
    await init_db_pool()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await close_db_pool()
