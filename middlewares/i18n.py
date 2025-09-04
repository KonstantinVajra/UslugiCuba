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


def _get_tr(lang: str):
    return gettext.translation("bot", localedir="locales", languages=[lang], fallback=True)

def _(key: str, lang: str | None = None):
    tr = _get_tr(lang or "ru")
    return tr.gettext(key)

# Aiogram middleware (легкий)
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any

class I18nMiddleware(BaseMiddleware):
    def __init__(self, default_lang: str = "ru"):
        self.default_lang = default_lang
        super().__init__()

    async def __call__(self, handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]], event: Any, data: Dict[str, Any]) -> Any:
        data["lang"] = getattr(getattr(event, "from_user", None), "language_code", None) or self.default_lang
        data["_"] = lambda key: _(key, data["lang"])
        return await handler(event, data)
