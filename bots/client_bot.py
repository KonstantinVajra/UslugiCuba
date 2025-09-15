# bots/client_bot.py
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import CLIENT_BOT_TOKEN
from middlewares.i18n import I18nMiddleware
from handlers.client import service_selection, taxi_flow
from handlers.common.back import router as back_router  # ← подключаем «Назад»
from repo.orders import ping_db  # как у вас было

# Логи
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("client_bot")

async def run_client_bot():
    # Новый способ задания parse_mode — без депрекейта
    bot = Bot(
        token=CLIENT_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # i18n для сообщений и коллбеков
    i18n = I18nMiddleware()
    dp.message.middleware(i18n)
    dp.callback_query.middleware(i18n)

    # Роутеры
    dp.include_router(service_selection.router)
    dp.include_router(taxi_flow.router)
    dp.include_router(back_router)  # «Назад»

    # Проверка БД (не валим запуск, если БД недоступна)
    try:
        await ping_db()
        logger.info("DB OK. Starting polling...")
    except Exception as e:
        logging.warning("DB not reachable: %s — starting in NO-DB mode", e)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
