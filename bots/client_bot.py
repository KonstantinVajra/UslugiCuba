# bots/client_bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import CLIENT_BOT_TOKEN
from middlewares.i18n import I18nMiddleware
from handlers.client import service_selection


# +++ ЛОГИ
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("client_bot")

# +++ ПИНГ БД
from repo.orders import ping_db


async def run_client_bot():
    bot = Bot(token=CLIENT_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    dp.include_router(service_selection.router)
    # dp.include_router(taxi_flow.router) # <-- ВРЕМЕННО ОТКЛЮЧАЕМ КОНФЛИКТУЮЩИЙ ОБРАБОТЧИК

    # Проверяем БД перед запуском polling (упадём сразу, если что)
    try:
        await ping_db()
    except Exception as e:
        logging.warning("DB not reachable: %s — starting in NO-DB mode", e)
    logger.info("DB OK. Starting polling...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
