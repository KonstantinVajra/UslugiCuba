# repo/offers.py
import logging
from typing import List, Dict, Any
from .orders import get_pool  # Используем тот же пул соединений

log = logging.getLogger("repo.offers")


async def get_published_offers_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Возвращает список опубликованных предложений (offers) для заданной категории.
    Для 'taxi' — запрашивает автомобили (vehicles).
    """
    pool = await get_pool()
    if not pool:
        log.warning("DB pool is not available, cannot fetch offers.")
        return []

    # ВНИМАНИЕ: Временное решение для демонстрации UX.
    # В будущем здесь должна быть логика для запроса предложений
    # из соответствующей таблицы или сущности 'Offer' для каждой категории.
    # Сейчас для всех категорий возвращаются данные из 'svc.vehicle'.
    log.info(f"Fetching offers for category '{category}' using 'svc.vehicle' as a data source.")

    async with pool.acquire() as con:
        try:
            # Нам нужен provider_tg_id, который хранится в svc.user.tg_id
            # Связь: vehicle -> provider -> user
            rows = await con.fetch(
                """
                SELECT
                    v.id,
                    v.title,
                    v.description,
                    v.photo_file_ids,
                    v.seats,
                    v.price_per_hour,
                    v.price_details,
                    u.tg_id as provider_tg_id
                FROM
                    svc.vehicle v
                JOIN
                    svc.provider p ON v.provider_id = p.id
                JOIN
                    svc."user" u ON p.user_id = u.id
                WHERE
                    v.status = 'published'
                ORDER BY
                    v.updated_at DESC;
                """
            )
            log.info(f"Fetched {len(rows)} published vehicles for category 'taxi'.")
            return [dict(row) for row in rows]
        except Exception as e:
            log.exception("Failed to fetch published offers for category '%s': %s", category, e)
            return []