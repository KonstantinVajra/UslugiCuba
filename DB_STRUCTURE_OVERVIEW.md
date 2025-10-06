# Структура Базы данных «Услуги Кубы»

## Схемы
- **svc** — системная: пользователи, провайдеры, автомобили.
- **uslugicuba** — доменная: города/зоны/локации, каталог услуг, офферы/цены, клиенты, заказы.

---

## Схема: `svc`

### Таблица: `svc."user"`
*Telegram-пользователи, взаимодействующие с ботом.*
| Column | Type | Default | Notes |
|---|---|---|---|
| `id` | `INTEGER IDENTITY` | `PK` | |
| `tg_id` | `BIGINT` | `UNIQUE, NOT NULL` | |
| `username` | `VARCHAR(255)` | `NULL` | |
| `role` | `VARCHAR(20)` | `'client'` | `client/provider/admin` |
| `is_banned` | `BOOLEAN` | `FALSE` | |
| `joined_at` | `TIMESTAMPTZ` | `NOW()` | |

### Таблица: `svc.provider`
*Поставщики услуг (водители, гиды, фотографы и т.п.). 1:1 к svc.user.*
| Column | Type | Default | Notes |
|---|---|---|---|
| `id` | `INTEGER IDENTITY` | `PK` | |
| `user_id` | `INTEGER` | `NOT NULL UNIQUE` | `FK svc."user"(id) ON DELETE CASCADE` |
| `name` | `VARCHAR(255)` | `NOT NULL` | |
| `phone` | `VARCHAR(50)` | `NULL` | |
| `is_active` | `BOOLEAN` | `TRUE` | |
| `created_at` | `TIMESTAMPTZ` | `NOW()` | |

### Таблица: `svc.vehicle`
*Автомобили, предлагаемые провайдерами.*
| Column | Type | Default | Notes |
|---|---|---|---|
| `id` | `INTEGER IDENTITY` | `PK` | |
| `provider_id` | `INTEGER` | `NOT NULL` | `FK svc.provider(id) ON DELETE CASCADE` |
| `title` | `VARCHAR(255)` | `NOT NULL` | |
| `description` | `TEXT` | `NULL` | |
| `photo_file_ids` | `TEXT[]` | `'{}'` | |
| `seats` | `INTEGER` | `NULL` | |
| `price_per_hour` | `NUMERIC(10,2)` | `NULL` | |
| `price_details` | `TEXT` | `NULL` | |
| `status` | `VARCHAR(20)` | `'draft'` | `draft/published/archived` |
| `created_at` | `TIMESTAMPTZ` | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOW()` | |

---

## Схема: `uslugicuba`

### Таблица: `uslugicuba.customers`
*Отражение svc.user в доменной модели, хранит доп. данные клиента.*
| Column | Type | Default | Notes |
|---|---|---|---|
| `id` | `INTEGER IDENTITY` | `PK` | |
| `user_id` | `INTEGER` | `NOT NULL UNIQUE` | `FK svc."user"(id) ON DELETE CASCADE` |
| `full_name` | `VARCHAR(255)` | `NULL` | |
| `phone` | `VARCHAR(50)` | `NULL` | |
| `lang` | `VARCHAR(10)` | `'ru'` | |
| `meta` | `JSONB` | `'{}'` | |
| `created_at` | `TIMESTAMPTZ` | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOW()` | |

### Таблица: `uslugicuba.orders`
*Основная таблица заказов.*
| Column | Type | Default | Notes |
|---|---|---|---|
| `id` | `INTEGER IDENTITY` | `PK` | |
| `customer_id` | `INTEGER` | `NOT NULL` | `FK uslugicuba.customers(id) ON DELETE CASCADE` |
| `service_id` | `INTEGER` | `NULL` | `FK uslugicuba.services(id) ON DELETE SET NULL` |
| `provider_id` | `INTEGER` | `NULL` | `FK svc.provider(id) ON DELETE SET NULL` |
| `vehicle_id` | `INTEGER` | `NULL` | `FK svc.vehicle(id) ON DELETE SET NULL` |
| `state` | `uslugicuba.order_state` | `'new'` | `ENUM: new, pending, assigned, done, canceled` |
| `date_time` | `TIMESTAMPTZ` | `NULL` | |
| `pax` | `INTEGER` | `NULL` | |
| `customer_note` | `TEXT` | `NULL` | |
| `meta` | `JSONB` | `'{}'` | |
| `pickup_text` | `TEXT` | `NULL` | |
| `dropoff_text` | `TEXT` | `NULL` | |
| `created_at` | `TIMESTAMPTZ` | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | `NOW()` | |

### Другие таблицы (справочники)
- `uslugicuba.cities`
- `uslugicuba.zones`
- `uslugicuba.locations`
- `uslugicuba.services`
- `uslugicuba.service_offers`
- `uslugicuba.service_zone_prices`
- `uslugicuba.vehicles` (проекция)

---
## Связи (кратко)
- `svc.user` ──1:1── `svc.provider` ──1:N── `svc.vehicle`
-    │
-    └─1:1── `uslugicuba.customers` ──1:N── `uslugicuba.orders`
- `uslugicuba.services` ──1:N── `uslugicuba.orders`
- `uslugicuba.locations` ──(pickup/dropoff)── `uslugicuba.orders`

## Паттерн создания заказа
1. `get_or_create` user в `svc."user"` по `tg_id`.
2. `get_or_create` customer в `uslugicuba.customers` по `user_id`.
3. `INSERT` order в `uslugicuba.orders` с `customer_id`.