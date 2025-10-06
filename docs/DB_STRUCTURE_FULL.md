# База данных «Услуги Кубы» — полная структура

Ниже — актуальная структура после «чистого ресета» и патча совместимости (поля pickup/dropoff и when_at). Формат: схема → таблицы → столбцы (тип, ограничения), индексы/триггеры/связи.

## Схемы

- **svc** — системная: пользователи, провайдеры, автомобили.
- **uslugicuba** — доменная: города/зоны/локации, каталог услуг, офферы и цены, клиенты, заказы.

## Общие объекты (schema uslugicuba)

### Функции/триггеры

- **uslugicuba.set_updated_at()** — проставляет `NEW.updated_at := NOW()` (используется в `BEFORE UPDATE`-триггерах).
- **uslugicuba.sync_when_at_date_time()** — синхронизирует `orders.when_at` и `orders.date_time` в `BEFORE INSERT/UPDATE`.

### ENUM

- **uslugicuba.order_state**: `new`, `pending`, `assigned`, `done`, `canceled`.

---

## Схема: svc

### Таблица: svc."user"
Telegram-пользователи.

- **id** — `INTEGER IDENTITY`, PK
- **tg_id** — `BIGINT`, UNIQUE, NOT NULL
- **username** — `VARCHAR(255)`, NULL
- **role** — `VARCHAR(20)`, NOT NULL, DEFAULT `'client'` (client/provider/admin)
- **is_banned** — `BOOLEAN`, NOT NULL, DEFAULT `FALSE`
- **joined_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`

**Индексы/ограничения**: PK(id), UNIQUE(tg_id).

### Таблица: svc.provider
Поставщики услуг (1:1 к `svc.user`).

- **id** — `INTEGER IDENTITY`, PK
- **user_id** — `INTEGER`, NOT NULL, UNIQUE, FK → `svc."user"(id)` ON DELETE CASCADE
- **name** — `VARCHAR(255)`, NOT NULL
- **phone** — `VARCHAR(50)`, NULL
- **is_active** — `BOOLEAN`, NOT NULL, DEFAULT `TRUE`
- **created_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`

**Индексы/ограничения**: PK(id), UNIQUE(user_id), FK(user_id)→`svc."user"(id)`.

### Таблица: svc.vehicle
Автомобили провайдеров.

- **id** — `INTEGER IDENTITY`, PK
- **provider_id** — `INTEGER`, NOT NULL, FK → `svc.provider(id)` ON DELETE CASCADE
- **title** — `VARCHAR(255)`, NOT NULL
- **description** — `TEXT`, NULL
- **photo_file_ids** — `TEXT[]`, NOT NULL, DEFAULT `'{}'`
- **seats** — `INTEGER`, NULL
- **price_per_hour** — `NUMERIC(10,2)`, NULL
- **price_details** — `TEXT`, NULL
- **status** — `VARCHAR(20)`, NOT NULL, DEFAULT `'draft'` (draft/published/archived)
- **created_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`
- **updated_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`

**Индексы/ограничения**: PK(id), FK(provider_id)→`svc.provider(id)`, INDEX `idx_vehicle_status(status)`.

---

## Схема: uslugicuba

### Таблица: uslugicuba.cities
Города.

- **id** — `INTEGER IDENTITY`, PK
- **code** — `VARCHAR(16)`, NOT NULL, UNIQUE (напр., VAR/HAV)
- **name** — `VARCHAR(255)`, NOT NULL

**Индексы/ограничения**: PK(id), UNIQUE(code).

### Таблица: uslugicuba.zones
Зоны ценообразования в разрезе города (A/B/C/D).

- **id** — `INTEGER IDENTITY`, PK
- **city_id** — `INTEGER`, NOT NULL, FK → `uslugicuba.cities(id)` ON DELETE CASCADE
- **code** — `VARCHAR(5)`, NOT NULL (A/B/C/D)
- **name** — `VARCHAR(255)`, NULL
- **UNIQUE(city_id,code)**

**Индексы/ограничения**: PK(id), FK(city_id)→`cities(id)`, UNIQUE(city_id,code).

### Таблица: uslugicuba.locations
Справочник локаций (отели/рестораны/аэропорты/POI).

- **id** — `INTEGER IDENTITY`, PK
- **kind** — `VARCHAR(50)`, NOT NULL (hotel/restaurant/airport/poi/…)
- **name** — `VARCHAR(255)`, NOT NULL
- **city_id** — `INTEGER`, NULL, FK → `uslugicuba.cities(id)` ON DELETE SET NULL
- **zone_id** — `INTEGER`, NULL, FK → `uslugicuba.zones(id)` ON DELETE SET NULL

**Индексы**: `idx_locations_kind(kind)`, `idx_locations_city(city_id)`, `idx_locations_zone(zone_id)`.

### Таблица: uslugicuba.services
Каталог услуг.

- **id** — `INTEGER IDENTITY`, PK
- **category** — `VARCHAR(50)`, NOT NULL (taxi/cabrio/guide/photo_video/…)
- **name** — `VARCHAR(255)`, NOT NULL
- **description** — `TEXT`, NULL
- **base_price** — `NUMERIC(10,2)`, NULL
- **city_id** — `INTEGER`, NULL, FK → `uslugicuba.cities(id)` ON DELETE SET NULL
- **zone_id** — `INTEGER`, NULL, FK → `uslugicuba.zones(id)` ON DELETE SET NULL
- **active** — `BOOLEAN`, NOT NULL, DEFAULT `TRUE`

**Индексы**: `idx_services_category(category)`, `idx_services_city(city_id)`, `idx_services_zone(zone_id)`, `idx_services_active(active)`.

### Таблица: uslugicuba.service_offers
Пакеты/тарифы/меню/почасовые офферы для `services`.

- **id** — `INTEGER IDENTITY`, PK
- **service_id** — `INTEGER`, NOT NULL, FK → `uslugicuba.services(id)` ON DELETE CASCADE
- **offer_type** — `VARCHAR(50)`, NOT NULL (zone_price/package/menu_item/hourly/rental_item)
- **title** — `VARCHAR(255)`, NOT NULL
- **price** — `NUMERIC(10,2)`, NULL
- **description** — `TEXT`, NULL

**Индексы**: `idx_offers_service(service_id)`, `idx_offers_type(offer_type)`.

### Таблица: uslugicuba.service_zone_prices
Нормализованные цены услуги по зонам.

- **id** — `INTEGER IDENTITY`, PK
- **service_id** — `INTEGER`, NOT NULL, FK → `uslugicuba.services(id)` ON DELETE CASCADE
- **zone_id** — `INTEGER`, NOT NULL, FK → `uslugicuba.zones(id)` ON DELETE CASCADE
- **price** — `NUMERIC(10,2)`, NOT NULL
- **UNIQUE(service_id,zone_id)**

**Индексы/ограничения**: PK(id), FK’s, UNIQUE(service_id,zone_id).

### Таблица: uslugicuba.vehicles (опциональная проекция услуга↔авто)

- **id** — `INTEGER IDENTITY`, PK
- **provider_id** — `INTEGER`, NOT NULL, FK → `svc.provider(id)` ON DELETE CASCADE
- **service_id** — `INTEGER`, NOT NULL, FK → `uslugicuba.services(id)` ON DELETE CASCADE
- **title** — `VARCHAR(255)`, NOT NULL
- **seats** — `INTEGER`, NULL
- **price_per_hour** — `NUMERIC(10,2)`, NULL
- **photo_file_ids** — `TEXT[]`, NOT NULL, DEFAULT `'{}'`

**Индексы/ограничения**: PK(id), FK’s.

### Таблица: uslugicuba.customers
Клиенты (проекция `svc.user` в домен).

- **id** — `INTEGER IDENTITY`, PK
- **user_id** — `INTEGER`, NOT NULL, UNIQUE, FK → `svc."user"(id)` ON DELETE CASCADE
- **full_name** — `VARCHAR(255)`, NULL
- **phone** — `VARCHAR(50)`, NULL
- **lang** — `VARCHAR(10)`, NOT NULL, DEFAULT `'ru'`
- **meta** — `JSONB`, NOT NULL, DEFAULT `'{}'`
- **created_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`
- **updated_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`

**Триггеры**: `customers_updated_at_trigger` (`BEFORE UPDATE` → `set_updated_at()`).

### Таблица: uslugicuba.orders
Основная таблица заказов.

- **id** — `INTEGER IDENTITY`, PK
- **customer_id** — `INTEGER`, NOT NULL, FK → `uslugicuba.customers(id)` ON DELETE CASCADE
- **service_id** — `INTEGER`, NULL, FK → `uslugicuba.services(id)` ON DELETE SET NULL
- **provider_id** — `INTEGER`, NULL, FK → `svc.provider(id)` ON DELETE SET NULL
- **vehicle_id** — `INTEGER`, NULL, FK → `svc.vehicle(id)` ON DELETE SET NULL
- **state** — `uslugicuba.order_state`, NOT NULL, DEFAULT `'new'`
- **city_id** — `INTEGER`, NULL, FK → `uslugicuba.cities(id)` ON DELETE SET NULL
- **zone_id** — `INTEGER`, NULL, FK → `uslugicuba.zones(id)` ON DELETE SET NULL
- **date_time** — `TIMESTAMPTZ`, NULL (основное поле времени)
- **when_at** — `TIMESTAMPTZ`, NULL (совместимость со старым кодом; синхронизируется триггером)
- **pax** — `INTEGER`, NULL
- **customer_note** — `TEXT`, NULL
- **meta** — `JSONB`, NOT NULL, DEFAULT `'{}'`
- **pickup_kind** — `VARCHAR(32)`, NULL (hotel/restaurant/airport/free_text)
- **pickup_id** — `INTEGER`, NULL, FK → `uslugicuba.locations(id)` ON DELETE SET NULL
- **pickup_text** — `TEXT`, NULL
- **dropoff_kind** — `VARCHAR(32)`, NULL
- **dropoff_id** — `INTEGER`, NULL, FK → `uslugicuba.locations(id)` ON DELETE SET NULL
- **dropoff_text** — `TEXT`, NULL
- **created_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`
- **updated_at** — `TIMESTAMPTZ`, NOT NULL, DEFAULT `NOW()`

**Индексы**:
`idx_orders_state(state)`, `idx_orders_created_at(created_at)`, `idx_orders_when_at(date_time)`,
`idx_orders_customer(customer_id)`, `idx_orders_pickup_kind(pickup_kind)`, `idx_orders_dropoff_kind(dropoff_kind)`.

**Триггеры**:
`orders_updated_at_trigger` (`BEFORE UPDATE` → `set_updated_at()`),
`orders_sync_when_at_date_time` (`BEFORE INSERT/UPDATE` → `sync_when_at_date_time()`).