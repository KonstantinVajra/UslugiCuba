# База данных «Услуги Кубы» — полная структура (matches current DB)
**Сгенерировано:** 2025-10-06 13:20:46

## Общие объекты (schema `uslugicuba`)
- Функции/триггеры:
  - `uslugicuba.set_updated_at()` — BEFORE UPDATE: `NEW.updated_at := NOW()`.
  - `uslugicuba.sync_when_at_date_time()` — BEFORE INSERT/UPDATE на `orders`: синхронизирует `when_at` и `date_time`.
- ENUM: `uslugicuba.order_state` ∈ {`new`, `pending`, `assigned`, `done`, `canceled`}.

## Схема: `svc`
### `svc."user"`
id (IDENTITY, PK) · tg_id (BIGINT, UNIQUE, NOT NULL) · username (varchar) · role (varchar, default 'client') · is_banned (bool, default false) · joined_at (timestamptz, default now())

### `svc.provider`
id (IDENTITY, PK) · user_id (UNIQUE FK → svc."user"(id), NOT NULL) · name (varchar, NOT NULL) · phone (varchar) · is_active (bool, default true) · created_at (timestamptz, default now())

### `svc.vehicle`
id (IDENTITY, PK) · provider_id (FK → svc.provider(id), NOT NULL) · title (varchar, NOT NULL) · description (text) · photo_file_ids (text[] NOT NULL DEFAULT '{}') · seats (int) · price_per_hour (numeric) · price_details (text) · status (varchar DEFAULT 'draft') · created_at (timestamptz) · updated_at (timestamptz)
Индекс: idx_vehicle_status(status)

## Схема: `uslugicuba`
### `uslugicuba.cities`
id (IDENTITY, PK) · code (varchar UNIQUE, NOT NULL) · name (varchar NOT NULL)

### `uslugicuba.zones`
id (IDENTITY, PK) · city_id (FK → cities, NOT NULL) · code (varchar NOT NULL) · name (varchar)
UNIQUE(city_id, code)

### `uslugicuba.locations`
id (IDENTITY, PK) · kind (varchar NOT NULL) · name (varchar NOT NULL) · city_id (FK → cities) · zone_id (FK → zones)
Индексы: kind, city_id, zone_id

### `uslugicuba.services`
id (IDENTITY, PK) · category (varchar NOT NULL) · name (varchar NOT NULL) · description (text) · base_price (numeric) · city_id (FK → cities) · zone_id (FK → zones) · active (bool DEFAULT true)
Индексы: category, city_id, zone_id, active

### `uslugicuba.service_offers`
id (IDENTITY, PK) · service_id (FK → services, NOT NULL) · offer_type (varchar NOT NULL) · title (varchar NOT NULL) · price (numeric) · description (text)
Индексы: service_id, offer_type

### `uslugicuba.service_zone_prices`
id (IDENTITY, PK) · service_id (FK → services, NOT NULL) · zone_id (FK → zones, NOT NULL) · price (numeric NOT NULL)
UNIQUE(service_id, zone_id)

### `uslugicuba.customers`
id (IDENTITY, PK) · user_id (UNIQUE FK → svc."user"(id), NOT NULL) · full_name (varchar) · phone (varchar) · lang (varchar DEFAULT 'ru' NOT NULL) · meta (jsonb DEFAULT '{}' NOT NULL) · created_at (timestamptz DEFAULT now() NOT NULL) · updated_at (timestamptz DEFAULT now() NOT NULL)
Триггер: customers_updated_at_trigger → set_updated_at()

### `uslugicuba.orders`
id (IDENTITY, PK) · customer_id (FK → customers(id) NOT NULL) · service_id (FK → services) · provider_id (FK → svc.provider) · vehicle_id (FK → svc.vehicle) · state (order_state DEFAULT 'new' NOT NULL) · city_id (FK → cities) · zone_id (FK → zones) · date_time (timestamptz) · when_at (timestamptz; синхронизируется) · pax (int) · customer_note (text) · meta (jsonb DEFAULT '{}' NOT NULL) · pickup_kind (varchar) · pickup_id (FK → locations) · pickup_text (text) · dropoff_kind (varchar) · dropoff_id (FK → locations) · dropoff_text (text) · created_at (timestamptz DEFAULT now() NOT NULL) · updated_at (timestamptz DEFAULT now() NOT NULL)
Индексы: state, created_at, **idx_orders_when_at → на column `date_time`**, customer_id, pickup_kind, dropoff_kind
Триггеры: orders_updated_at_trigger (set_updated_at), orders_sync_when_at_date_time (sync_when_at_date_time)
