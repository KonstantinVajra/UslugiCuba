# bots/client_bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import CLIENT_BOT_TOKEN
from middlewares.i18n import I18nMiddleware
from db.db_config import init_db_pool, close_db_pool

# Импортируем все наши новые обработчики
from handlers.common import registration
from handlers.provider import vehicle_management
from handlers.client import car_booking
from handlers.admin import moderation
# Старые обработчики, если они все еще нужны
from handlers.client import service_selection, taxi_flow

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("client_bot")


async def run_client_bot():
    """Инициализирует и запускает клиентского бота."""
    bot = Bot(token=CLIENT_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем обработчики жизненного цикла для пула соединений БД
    dp.startup.register(init_db_pool)
    dp.shutdown.register(close_db_pool)

    # Регистрируем мидлвари
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Регистрируем все роутеры в правильном порядке
    # Общие обработчики (регистрация) должны идти первыми
    dp.include_router(registration.router)

    # Роутеры для конкретных ролей
    dp.include_router(moderation.router) # Админ
    dp.include_router(vehicle_management.router) # Провайдер
    dp.include_router(car_booking.router) # Клиент

    # Старые роутеры (если они все еще используются)
    dp.include_router(service_selection.router)
    dp.include_router(taxi_flow.router)

    logger.info("Starting polling...")

    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)