# middlewares/i18n.py

import gettext
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

# Загрузка переводов
LOCALES = {
    "en": gettext.translation("bot", localedir="locales", languages=["en"]),
    "ru": gettext.translation("bot", localedir="locales", languages=["ru"]),
    "es": gettext.translation("bot", localedir="locales", languages=["es"]),
}

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        # Получаем язык от пользователя
        lang_code = getattr(event.from_user, "language_code", "en")

        # Пробуем взять язык из FSM (если уже выбран пользователем)
        if "state" in data:
            try:
                state_data = await data["state"].get_data()
                lang_code = state_data.get("lang", lang_code)
            except Exception:
                pass

        # Фолбэк на английский
        lang = lang_code if lang_code in LOCALES else "en"

        # Подставляем функцию перевода
        data["_"] = LOCALES[lang].gettext

        return await handler(event, data)
