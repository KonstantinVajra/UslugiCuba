Бот для оформления услуг (такси, ретро-авто, гид, фотограф). Ведёт пользователя пошагово через inline-кнопки: выбор услуги → точки отправления/назначения → дата и время → подтверждение заказа.

Возможности

👤 Команды /start, /order.

🧭 Маршрут: откуда / куда с категориями:

🏨 Отели (список с эмодзи),

🍽 Рестораны (список с эмодзи),

✈️ Аэропорты (список).

📅 Выбор даты → ⏰ выбор часа → минут → итоговая карточка заказа с кнопками ✅ подтвердить / ❌ отменить.

🌐 Локализация (gettext): ru / en / es (автовыбор по from_user.language_code, можно хранить выбор в FSM).

🔒 Токен берётся из .env.

Технологии

Python 3.11

aiogram v3 (Router, FSM)

gettext для i18n (.po → .mo)

python-dotenv для конфигурации

Структура проекта
UslugiCuba/
├─ bots/
│  └─ client_bot.py          # инициализация бота, Dispatcher, middleware, роутеры
├─ handlers/
│  └─ client/
│     └─ service_selection.py # сценарий выбора услуги/локаций/даты-времени/подтверждения
├─ keyboards/
│  ├─ client.py               # inline-клавиатуры: услуги, дата/час/минута
│  └─ locations.py            # клавиатуры: категории и списки отелей/ресторанов/аэропортов
├─ locales/
│  ├─ en/LC_MESSAGES/bot.po
│  ├─ es/LC_MESSAGES/bot.po
│  └─ ru/LC_MESSAGES/bot.po
├─ middlewares/
│  └─ i18n.py                 # I18nMiddleware на gettext
├─ states/
│  └─ client_states.py        # FSM: OrderServiceState
├─ compile_translations.py    # компиляция .po → .mo
├─ config.py                  # загрузка .env (CLIENT_BOT_TOKEN)
├─ main.py                    # entry point (run_client_bot)
└─ requirements.txt

Быстрый старт
# 1) зависимости
pip install -r requirements.txt

# 2) конфиг
# создайте .env и положите токен:
# CLIENT_BOT_TOKEN=123456:ABC-DEF...

# 3) компиляция переводов (разово; при изменении .po — повторить)
python compile_translations.py

# 4) запуск
python main.py

Переменные окружения
CLIENT_BOT_TOKEN=тут_токен_бота


.env уже в .gitignore — не коммить.

Жизненный цикл диалога

/start → сообщение приветствия и меню услуг.

Выбор услуги (taxi | retro | guide | photographer).

Выбор откуда: категория (отель/ресторан/аэропорт) → конкретное место из списка.

Выбор куда: аналогично.

Выбор даты → часа → минут.

Итоговая карточка с данными заказа + кнопки подтверждения/отмены.

Клавиатуры (общая схема)

service_inline_keyboard(_)

pickup_category_keyboard() / dropoff_category_keyboard()

hotel_list_keyboard(prefix) / restaurant_list_keyboard(prefix) / airport_list_keyboard(prefix)

date_selection_keyboard(_) / hour_selection_keyboard() / minute_selection_keyboard()

Callback-данные имеют префиксы:

service_*, pickup_* / dropoff_*, date_YYYY-MM-DD, hour_HH, minute_MM

I18n

Мидлварь подставляет в хэндлеры переводчик _ = gettext.gettext по языку пользователя.

Язык можно принудительно хранить/читать из FSM state (если реализуете переключатель).

Тексты живут в locales/*/LC_MESSAGES/bot.po. После правок — заново python compile_translations.py.

Известные трудности и как решено

Python 3.11 и f-строки: нельзя вкладывать строковые литералы с теми же кавычками внутри f"...".
✅ Решение: выносить _("key") в переменные перед форматированием.

Синтаксис в locations.py: был неверный отступ в hotel_list_keyboard и битая строка — давало IndentationError/SyntaxError.
✅ Починено: ровные отступы, корректные строки.

Структура импортов: пути должны соответствовать фактическим папкам (bots/, handlers/, keyboards/, states/, middlewares/).
✅ Приведено к рабочему варианту.

Компилированные .mo и __pycache__ в git:
✅ Исключены через .gitignore.

Пуш на GitHub: конфликт из-за已有 коммита (README), решено git pull --rebase → git push.

Что ещё предстоит (roadmap)

🔙 Кнопки «Назад» на каждом шаге.

🧾 Расчёт стоимости (тарифы/километраж), валидация времени (например, не в прошлом).

💾 Хранилище заказов (БД) + админ-панель.

💳 Интеграция оплаты.

🌍 Переключатель языка в боте + вычитка переводов.

🧪 Тесты (юнит/интеграционные), CI (lint + pytests).

📈 Логирование, алерты.

🧹 Рефакторинг повторяющихся хэндлеров (обобщить «pickup/dropoff» для отелей/ресторана/аэропортов).

Troubleshooting

SyntaxError: f-string: unterminated / «nested string literals» → проверь, что нет f"… {_("key")} …", вынеси в переменную.

ModuleNotFoundError → проверь пути импортов и, что запускаешь из корня.

«Unauthorized» → проверь CLIENT_BOT_TOKEN.

Переводы не применяются → заново python compile_translations.py, проверь locales и I18nMiddleware.

Пуш отклонён → сделай git pull --rebase origin main, реши конфликты, затем git push.

Лицензия

MIT (настрой по необходимости).

Команды, чтобы добавить README в репо
# (из корня проекта)
git add README.md
git commit -m "docs: add README with setup, flow, troubleshooting and roadmap"
git push