import logging
from db.db_config import get_db_pool

log = logging.getLogger(__name__)

async def list_services(category: str, city_id: int | None = None) -> list[dict]:
    """Возвращает список услуг по категории и, опционально, городу."""
    pool = get_db_pool()
    query = """
        SELECT id, category, title, description, city_id
        FROM uslugicuba.services
        WHERE category = $1
          AND ($2::bigint IS NULL OR city_id = $2)
        ORDER BY id;
    """
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(query, category, city_id)
            log.info(f"Found {len(rows)} services for category='{category}' city_id={city_id}")
            return [dict(row) for row in rows]
        except Exception:
            log.exception("Failed to list_services")
            return []

async def list_offers(service_id: int) -> list[dict]:
    """Возвращает все офферы (тарифы) по ID услуги."""
    pool = get_db_pool()
    query = """
        SELECT id, service_id, offer_type, zone_id, title, details, price, currency
        FROM uslugicuba.service_offers
        WHERE service_id = $1
        ORDER BY zone_id NULLS LAST, id;
    """
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(query, service_id)
            log.info(f"Found {len(rows)} offers for service_id={service_id}")
            return [dict(row) for row in rows]
        except Exception:
            log.exception("Failed to list_offers for service_id=%s", service_id)
            return []

async def list_zones(location_code: str) -> list[dict]:
    """Возвращает зоны по коду локации (например, 'VAR' для Варадеро)."""
    pool = get_db_pool()
    query = """
        SELECT z.id, z.code, z.name
        FROM uslugicuba.zones z
        JOIN uslugicuba.locations l ON l.id = z.location_id
        WHERE l.code = $1
        ORDER BY z.id;
    """
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(query, location_code)
            log.info(f"Found {len(rows)} zones for location_code='{location_code}'")
            return [dict(row) for row in rows]
        except Exception:
            log.exception("Failed to list_zones for location_code=%s", location_code)
            return []

async def list_vehicles(service_id: int, city_id: int) -> list[dict]:
    """
    Возвращает список активных автомобилей для услуги в указанном городе.
    (В этой версии не включает фото и цены по зонам, как опциональные в задаче).
    """
    pool = get_db_pool()
    query = """
        SELECT v.id, v.title, v.make, v.model, v.year, v.color, v.seats, v.is_cabrio, v.description
        FROM uslugicuba.vehicles v
        WHERE v.service_id = $1
          AND v.city_id = $2
          AND v.is_active = true
        ORDER BY v.id;
    """
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(query, service_id, city_id)
            log.info(f"Found {len(rows)} vehicles for service_id={service_id}, city_id={city_id}")
            return [dict(row) for row in rows]
        except Exception:
            log.exception("Failed to list_vehicles for service_id=%s, city_id=%s", service_id, city_id)
            return []