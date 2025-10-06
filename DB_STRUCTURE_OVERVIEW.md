# 🧱 Database Overview — “Uslugi Cuba” Project

**Generated:** 2025-10-06 09:46:47  
**Schemas:** `svc`, `uslugicuba`  
**Purpose:** store user, provider, vehicle, service, and order data for the Cuba Services ecosystem.

---

## ⚙️ SCHEMA: `svc`

### 1. `svc.user`
Stores all Telegram users interacting with the bot.

| Column | Type | Default | Notes |
|--------|------|----------|-------|
| id | SERIAL | — | Primary key |
| tg_id | BIGINT | — | Telegram ID |
| username | VARCHAR(255) | — | Telegram username |
| role | VARCHAR(20) | `'client'` | client / provider / admin |
| is_banned | BOOLEAN | false | Ban flag |
| joined_at | TIMESTAMPTZ | NOW() | Registration date |

### 2. `svc.provider`
Information about service providers (guides, photographers, drivers, etc.).

| Column | Type | Default | Notes |
|--------|------|----------|-------|
| id | SERIAL | — | Primary key |
| user_id | INTEGER | — | FK → `svc.user(id)` |
| name | VARCHAR(255) | — | Provider or company name |
| phone | VARCHAR(50) | — | Contact phone |
| is_active | BOOLEAN | true | Active flag |
| created_at | TIMESTAMPTZ | NOW() | Registration time |

### 3. `svc.vehicle`
List of provider vehicles.

| Column | Type | Default | Notes |
|--------|------|----------|-------|
| id | SERIAL | — | Primary key |
| provider_id | INTEGER | — | FK → `svc.provider(id)` |
| title | VARCHAR(255) | — | Vehicle title |
| description | TEXT | — | Description |
| photo_file_ids | TEXT[] | `'{}'` | Telegram file_id array |
| seats | INTEGER | — | Number of seats |
| price_per_hour | NUMERIC(10,2) | — | Hourly rate |
| price_details | TEXT | — | Price breakdown |
| status | VARCHAR(20) | `'draft'` | draft / published / archived |
| created_at | TIMESTAMPTZ | NOW() | Creation time |
| updated_at | TIMESTAMPTZ | NOW() | Update time |

---

## 🌴 SCHEMA: `uslugicuba`

### 1. `uslugicuba.locations`
Reference of known locations (hotels, restaurants, airports, etc.).

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | PK |
| kind | VARCHAR(50) | hotel / restaurant / airport / etc. |
| name | VARCHAR(255) | Name |
| city_id | INTEGER | FK → `uslugicuba.cities` |
| zone_id | INTEGER | FK → `uslugicuba.zones` |

### 2. `uslugicuba.zones`
Pricing zone mapping (A/B/C/D).

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | PK |
| code | VARCHAR(5) | A, B, C, D |
| name | VARCHAR(255) | Zone description |
| city_id | INTEGER | FK → `uslugicuba.cities` |

### 3. `uslugicuba.services`
Categories of services (taxi, cabrio, excursions, photographers, restaurants, weddings, etc.).

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | PK |
| category | VARCHAR(50) | taxi / cabrio / guide / photo_video / restaurant / wedding_ceremony / dress_rental / etc. |
| name | VARCHAR(255) | Service name |
| description | TEXT | Service description |
| base_price | NUMERIC(10,2) | Base price |
| city_id | INTEGER | FK → `uslugicuba.cities` |
| zone_id | INTEGER | FK → `uslugicuba.zones` |
| active | BOOLEAN | Service active flag |

### 4. `uslugicuba.service_offers`
Different offers or packages within a service.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | PK |
| service_id | INTEGER | FK → `uslugicuba.services` |
| offer_type | VARCHAR(50) | zone_price / package / menu_item / hourly / rental_item |
| title | VARCHAR(255) | Offer title |
| price | NUMERIC(10,2) | Price |
| description | TEXT | Offer description |

### 5. `uslugicuba.service_zone_prices`
Per-zone pricing for services.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | PK |
| service_id | INTEGER | FK → `uslugicuba.services` |
| zone_id | INTEGER | FK → `uslugicuba.zones` |
| price | NUMERIC(10,2) | Price for the zone |

### 6. `uslugicuba.vehicles`
Optional service-linked vehicles.

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | PK |
| provider_id | INTEGER | FK → `svc.provider(id)` |
| service_id | INTEGER | FK → `uslugicuba.services` |
| title | VARCHAR(255) | Vehicle title |
| seats | INTEGER | Seats count |
| price_per_hour | NUMERIC(10,2) | Hourly rate |
| photo_file_ids | TEXT[] | Telegram file_ids |

### 7. `uslugicuba.orders`
Main table for all customer orders.

| Column | Type | Default | Notes |
|--------|------|----------|-------|
| id | SERIAL | — | Primary key |
| customer_id | INTEGER | — | FK → `svc.user(id)` |
| service_id | INTEGER | — | FK → `uslugicuba.services` |
| provider_id | INTEGER | — | FK → `svc.provider(id)` |
| vehicle_id | INTEGER | — | FK → `svc.vehicle(id)` |
| state | VARCHAR(50) | — | Order status |
| city_id | INTEGER | — | FK → `uslugicuba.cities` |
| zone_id | INTEGER | — | FK → `uslugicuba.zones` |
| date_time | TIMESTAMPTZ | — | Start time |
| pax | INTEGER | — | Number of people |
| customer_note | TEXT | — | Customer note |
| meta | JSONB | `'{}'` | Free metadata (e.g. lang, context) |
| created_at | TIMESTAMPTZ | NOW() | Created |
| updated_at | TIMESTAMPTZ | NOW() | Updated |

**Triggers:**  
- `orders_updated_at_trigger` — auto-updates `updated_at`

**Indexes:**  
- `idx_orders_state`  
- `idx_orders_created`  
- `idx_orders_when_at`

---

## 🔗 Relationships

```
svc.user ───┬─< svc.provider ──< svc.vehicle
             │
             └─< uslugicuba.orders.customer_id
svc.provider ──< uslugicuba.orders.provider_id
svc.vehicle  ──< uslugicuba.orders.vehicle_id
uslugicuba.services ──< uslugicuba.orders.service_id
uslugicuba.zones ──< uslugicuba.orders.zone_id
```

---

## ✅ Design Principles

1. `svc` holds **system and identity-level data** (users, providers, vehicles).  
2. `uslugicuba` holds **domain and business logic** (catalogs, prices, orders).  
3. All production data is created and managed inside `uslugicuba`.  
4. `svc` schema can be reused for other bots (e.g., provider or admin bots).

---

**Conclusion:**  
This schema represents the stable production structure for the Cuba Services ecosystem as of 2025-10-06 — ready for full CRUD operations across users, providers, services, vehicles, and orders.
