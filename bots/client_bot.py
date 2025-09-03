from aiogram import Bot, Dispatcher
from config import config
from middlewares.i18n import I18nMiddleware
from handlers.client import service_selection

bot = Bot(token=config.CLIENT_BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(service_selection.router)

# Подключаем мидлвару для сообщений и callback'ов
dp.message.middleware(I18nMiddleware())
dp.callback_query.middleware(I18nMiddleware())

async def run_client_bot():
    # ВАЖНО: снимаем вебхук и выбрасываем «висящие» апдейты перед polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Стартуем polling
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types()
    )
