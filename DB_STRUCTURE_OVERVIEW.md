# Схема Базы Данных

## SCHEMA: svc

### 1. svc.user
Хранит всех пользователей, взаимодействующих с ботом.

| Column    | Type        | Default  | Notes                  |
|-----------|-------------|----------|------------------------|
| id        | SERIAL      | —        | Primary key            |
| tg_id     | BIGINT      | —        | Telegram ID            |
| username  | VARCHAR(255)| —        | Telegram username      |
| role      | VARCHAR(20) | 'client' | client / provider / admin |
| is_banned | BOOLEAN     | false    | Бан-флаг               |
| joined_at | TIMESTAMPTZ | NOW()    | Дата регистрации       |

**Indexes:**
- `user_tg_id_key` (unique)
- PK (id)

### 2. svc.provider
Информация о поставщиках (гиды, фотографы, водители и т.д.).

| Column     | Type        | Default | Notes                     |
|------------|-------------|---------|---------------------------|
| id         | SERIAL      | —       | Primary key               |
| user_id    | INTEGER     | —       | FK → svc.user(id)         |
| name       | VARCHAR(255)| —       | Имя или название          |
| phone      | VARCHAR(50) | —       | Контакт                   |
| is_active  | BOOLEAN     | true    | Статус                    |
| created_at | TIMESTAMPTZ | NOW()   | Время регистрации         |

**Constraints:**
- FK → `svc.user(id)` (ON DELETE CASCADE)
- `user_id` уникален (1 юзер = 1 провайдер)

### 3. svc.vehicle
Список автомобилей провайдеров.

| Column         | Type          | Default | Notes                       |
|----------------|---------------|---------|-----------------------------|
| id             | SERIAL        | —       | Primary key                 |
| provider_id    | INTEGER       | —       | FK → svc.provider(id)       |
| title          | VARCHAR(255)  | —       | Название (Chevrolet BelAir) |
| description    | TEXT          | —       | Описание                    |
| photo_file_ids | TEXT[]        | '{}'    | Массив Telegram file_id     |
| seats          | INTEGER       | —       | Кол-во мест                 |
| price_per_hour | NUMERIC(10,2) | —       | Цена/час                    |
| price_details  | TEXT          | —       | Доп. описание цены          |
| status         | VARCHAR(20)   | 'draft' | draft / published / archived|
| created_at     | TIMESTAMPTZ   | NOW()   | Создано                     |
| updated_at     | TIMESTAMPTZ   | NOW()   | Обновлено                   |

**Indexes:**
- `idx_vehicle_status` → BTREE(status)

---

## 🌴 SCHEMA: uslugicuba

### 1. uslugicuba.locations
Справочник локаций (отели, рестораны, аэропорты и т.д.).

| Column  | Type         | Notes                       |
|---------|--------------|-----------------------------|
| id      | SERIAL       | PK                          |
| kind    | VARCHAR(50)  | hotel / restaurant / airport / etc. |
| name    | VARCHAR(255) | Название                    |
| city_id | INTEGER      | FK → uslugicuba.cities      |
| zone_id | INTEGER      | FK → uslugicuba.zones       |

### 2. uslugicuba.zones
Зональная система ценообразования (A/B/C/D).

| Column  | Type         | Notes              |
|---------|--------------|--------------------|
| id      | SERIAL       | PK                 |
| code    | VARCHAR(5)   | A, B, C, D         |
| name    | VARCHAR(255) | Описание зоны      |
| city_id | INTEGER      | FK → uslugicuba.cities |

### 3. uslugicuba.services
Категории услуг: такси, кабриолеты, экскурсии, фотографы, рестораны и т.д.

| Column      | Type          | Notes                               |
|-------------|---------------|-------------------------------------|
| id          | SERIAL        | PK                                  |
| category    | VARCHAR(50)   | taxi / cabrio / guide / photo_video / ... |
| name        | VARCHAR(255)  | Название услуги                     |
| description | TEXT          | Описание                            |
| base_price  | NUMERIC(10,2) | Базовая цена                        |
| city_id     | INTEGER       | FK → uslugicuba.cities              |
| zone_id     | INTEGER       | FK → uslugicuba.zones               |
| active      | BOOLEAN       | Активна / нет                       |

### 4. uslugicuba.service_offers
Предложения внутри услуг (например, тариф или пакет).

| Column      | Type          | Notes                             |
|-------------|---------------|-----------------------------------|
| id          | SERIAL        | PK                                |
| service_id  | INTEGER       | FK → uslugicuba.services          |
| offer_type  | VARCHAR(50)   | zone_price / package / menu_item / hourly / rental_item |
| title       | VARCHAR(255)  | Название пакета                   |
| price       | NUMERIC(10,2) | Стоимость                         |
| description | TEXT          | Детали предложения                |

### 5. uslugicuba.service_zone_prices
Привязка цен по зонам.

| Column     | Type          | Notes                     |
|------------|---------------|---------------------------|
| id         | SERIAL        | PK                        |
| service_id | INTEGER       | FK → uslugicuba.services  |
| zone_id    | INTEGER       | FK → uslugicuba.zones     |
| price      | NUMERIC(10,2) | Цена для зоны             |

### 6. uslugicuba.vehicles
(если включена связь с транспортом на уровне услуг)

| Column         | Type          | Notes                     |
|----------------|---------------|---------------------------|
| id             | SERIAL        | PK                        |
| provider_id    | INTEGER       | FK → svc.provider(id)     |
| service_id     | INTEGER       | FK → uslugicuba.services  |
| title          | VARCHAR(255)  | Название                  |
| seats          | INTEGER       | Кол-во мест               |
| price_per_hour | NUMERIC(10,2) | Цена за час               |
| photo_file_ids | TEXT[]        | Telegram file_ids         |

### 7. uslugicuba.orders
Основная таблица заказов.

| Column        | Type        | Default | Notes                            |
|---------------|-------------|---------|----------------------------------|
| id            | SERIAL      | —       | Primary key                      |
| customer_id   | INTEGER     | —       | FK → svc.user(id)                |
| service_id    | INTEGER     | —       | FK → uslugicuba.services         |
| provider_id   | INTEGER     | —       | FK → svc.provider(id)            |
| vehicle_id    | INTEGER     | —       | FK → svc.vehicle(id)             |
| state         | VARCHAR(50) | —       | Статус выполнения                |
| city_id       | INTEGER     | —       | FK → uslugicuba.cities           |
| zone_id       | INTEGER     | —       | FK → uslugicuba.zones            |
| date_time     | TIMESTAMPTZ | —       | Когда подача / начало            |
| pax           | INTEGER     | —       | Кол-во человек                   |
| customer_note | TEXT        | —       | Комментарий клиента              |
| meta          | JSONB       | '{}'    | Доп. данные (lang, session_id)   |
| created_at    | TIMESTAMPTZ | NOW()   | Дата создания                    |
| updated_at    | TIMESTAMPTZ | NOW()   | Обновление                       |

**Triggers:**
- `orders_updated_at_trigger` — автообновление `updated_at`.

**Indexes:**
- `idx_orders_state`
- `idx_orders_created`
- `idx_orders_when_at`

---

## 🔗 Главные связи
- `svc.user` ───┬─< `svc.provider` ──< `svc.vehicle`
-            │
-            └─< `uslugicuba.orders.customer_id`
- `svc.provider` ──< `uslugicuba.orders.provider_id`
- `svc.vehicle`  ──< `uslugicuba.orders.vehicle_id`
- `uslugicuba.services` ──< `uslugicuba.orders.service_id`
- `uslugicuba.zones` ──< `uslugicuba.orders.zone_id`

## ✅ Ключевые принципы архитектуры
- `svc` — отвечает за технических пользователей и инфраструктуру бота.
- `uslugicuba` — отвечает за каталог услуг, заказы и контент.
- Все новые бизнес-данные (пакеты, цены, маршруты, заказы) создаются только в `uslugicuba`.
- В будущем допускается расширение `svc` под другие боты.