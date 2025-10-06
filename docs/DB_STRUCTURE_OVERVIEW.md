# Database Overview — “Uslugi Cuba” (matches current DB)
**Generated:** 2025-10-06 13:20:46

## Schemas
- `svc` — system: users, providers, vehicles.
- `uslugicuba` — domain: cities/zones/locations, service catalog, offers/prices, customers, orders.

### Core Relations
```
svc.user ──1:1── svc.provider ──1:N── svc.vehicle
   │                         │
   └─1:1── uslugicuba.customers ──1:N── uslugicuba.orders
uslugicuba.services ──1:N── uslugicuba.service_offers
uslugicuba.services ──1:N── uslugicuba.service_zone_prices
uslugicuba.cities ──1:N── uslugicuba.zones
uslugicuba.zones  ──1:N── uslugicuba.locations
uslugicuba.services ──1:N── uslugicuba.orders
svc.provider / svc.vehicle ──1:N── uslugicuba.orders
uslugicuba.locations ──(pickup/dropoff)── uslugicuba.orders
```

### Orders model (DB truth)
- Enum: `uslugicuba.order_state` ∈ {`new`, `pending`, `assigned`, `done`, `canceled`}
- Main time field: `date_time` (compat field `when_at` mirrors it via trigger).
- Address fields: `pickup_*` / `dropoff_*` with FKs to `uslugicuba.locations`.
- `orders.customer_id` → `uslugicuba.customers(id)` (not `svc.user`).
- Index note: **`idx_orders_when_at` is on `date_time` in DB**.
