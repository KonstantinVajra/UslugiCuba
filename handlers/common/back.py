# handlers/common/back.py
from __future__ import annotations
import contextlib  # ← добавили
from typing import Callable, Dict, Any

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from callbacks.common import BackCb
from services import nav_fsm
from keyboards.common import back_kb  # ← добавили

router = Router(name="common_back")

# === 1) Укажите здесь ваши рендер-функции для шагов ===
# Каждая функция должна принимать (message: types.Message, state: FSMContext, **kwargs)
# и заново отрисовывать нужный экран/клавиатуру.
async def render_choose_service(message: types.Message, state: FSMContext, **kwargs):  # TODO: замените на вашу функцию
    await message.answer("Вы в начале. Выберите услугу заново.")  # заглушка

SCREEN_RENDERERS: Dict[str, Callable[[types.Message, FSMContext], Any]] = {
    "choose_service": render_choose_service,
    # Примеры, добавьте свои реальные экраны:
    # "choose_from": render_choose_from,
    # "choose_to": render_choose_to,
    # "choose_datetime": render_choose_datetime,
    # "confirm": render_confirm,
}

@router.callback_query(BackCb.filter())
async def on_back(call: types.CallbackQuery, callback_data: BackCb, state: FSMContext):
    snap = await nav_fsm.pop(state)
    if not snap:
        await call.answer("Предыдущего шага нет", show_alert=False)
        return

    screen = snap.get("screen")
    args = snap.get("args", {}) or {}

    renderer = SCREEN_RENDERERS.get(screen) or SCREEN_RENDERERS.get("choose_service")

    # чистим инлайн-кнопки у текущего сообщения, чтобы не было «залипаний»
    with contextlib.suppress(Exception):
        await call.message.edit_reply_markup(reply_markup=None)

    await renderer(call.message, state, **args)
    await call.answer()

# === пример рендера для шага "choose_from" (покажет кнопку Назад) ===
async def render_choose_from(message: types.Message, state: FSMContext, from_code: str = "", **kwargs):
    await message.answer(
        f"(ВОССТАНОВЛЕН) Откуда уже было выбрано: {from_code}\nВыберите точку назначения",
        reply_markup=back_kb()  # ← теперь функция найдена
    )

# зарегистрируем его в таблице рендеров
SCREEN_RENDERERS.update({
    "choose_from": render_choose_from,
})
