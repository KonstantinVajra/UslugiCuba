# bots/client_bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import CLIENT_BOT_TOKEN
from middlewares.i18n import I18nMiddleware
from db.db_config import init_db_pool, close_db_pool

# Импортируем новые обработчики
from handlers.common import start as start_handler
from handlers.admin import card_management as admin_handler
from handlers.client import browsing as client_handler

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("client_bot")


async def run_client_bot():
    """Инициализирует и запускает бота."""
    bot = Bot(token=CLIENT_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем обработчики жизненного цикла для пула соединений БД
    dp.startup.register(init_db_pool)
    dp.shutdown.register(close_db_pool)

    # Регистрируем мидлвари
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Регистрируем все новые роутеры
    dp.include_router(admin_handler.router)
    dp.include_router(start_handler.router)
    dp.include_router(client_handler.router)

    logger.info("Bot is configured and starting polling...")

    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)