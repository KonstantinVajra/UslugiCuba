# services/publisher.py
import asyncio
import logging
from aiogram import Bot
from aiogram.utils.markdown import html_decoration as hd

from config import ORDERS_CHANNEL_ID, PUBLISH_MAX_RETRIES, PUBLISH_BACKOFFS

log = logging.getLogger(__name__)

async def _send_message_with_retries(bot: Bot, text: str):
    """
    Пытается отправить сообщение несколько раз с задержками.
    """
    log.info(f"Attempting to send message to channel ID: {ORDERS_CHANNEL_ID}")

    if not ORDERS_CHANNEL_ID or int(ORDERS_CHANNEL_ID) == 0:
        log.warning("ORDERS_CHANNEL_ID is not set or is 0, skipping publication.")
        return

    if not PUBLISH_MAX_RETRIES or not PUBLISH_BACKOFFS:
        log.warning("Retry mechanism is not configured. Sending once.")
        try:
            await bot.send_message(
                chat_id=ORDERS_CHANNEL_ID,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            log.info("Order card published to channel %s", ORDERS_CHANNEL_ID)
        except Exception as e:
            log.error("Failed to publish order to channel %s: %s", ORDERS_CHANNEL_ID, e)
        return

    backoffs = [int(b) for b in PUBLISH_BACKOFFS.split(",")]
    max_retries = int(PUBLISH_MAX_RETRIES)

    for i in range(max_retries):
        try:
            log.info(f"Sending message... (Attempt {i+1}/{max_retries})")
            await bot.send_message(
                chat_id=ORDERS_CHANNEL_ID,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            log.info("Order card published successfully to channel %s", ORDERS_CHANNEL_ID)
            return
        except Exception as e:
            log.warning(
                "Failed to publish order to channel %s (attempt %d/%d): %s",
                ORDERS_CHANNEL_ID, i + 1, max_retries, e
            )
            if i < max_retries - 1:
                backoff = backoffs[i] if i < len(backoffs) else backoffs[-1]
                log.info("Retrying in %d seconds...", backoff)
                await asyncio.sleep(backoff)
    log.error(
        "Failed to publish order to channel %s after %d attempts.",
        ORDERS_CHANNEL_ID, max_retries
    )


def format_order_card(order_id: int, pickup: str, dropoff: str, when: str, price: float, pax: int, client_tg_id: int) -> str:
    """
    Форматирует карточку заказа для публикации.
    """
    return (
        f"<b>✅ Новый заказ #{order_id}</b>\n\n"
        f"<b>Маршрут:</b> {hd.quote(pickup)} → {hd.quote(dropoff)}\n"
        f"<b>Время:</b> {when}\n"
        f"<b>Пассажиры:</b> {pax}\n"
        f"<b>Цена:</b> {price} USD\n\n"
        f"<b>Клиент:</b> tg://user?id={client_tg_id}"
    )


async def publish_order(bot: Bot, order_data: dict):
    """
    Публикует карточку заказа в Telegram-канал.
    Запускает отправку в фоне, чтобы не блокировать основной поток.
    """
    log.info(f"publish_order called with data: {order_data}")
    if not ORDERS_CHANNEL_ID or int(ORDERS_CHANNEL_ID) == 0:
        log.warning("ORDERS_CHANNEL_ID is not set or is 0, skipping publication.")
        return

    try:
        text = format_order_card(
            order_id=order_data["order_id"],
            pickup=order_data["pickup_text"],
            dropoff=order_data["dropoff_text"],
            when=order_data.get("when_hhmm", "сейчас"),
            price=order_data["price_quote"],
            pax=order_data.get("pax", 1),
            client_tg_id=order_data["client_tg_id"],
        )
        log.info(f"Formatted order card text for channel publication:\n{text}")

        # Запускаем отправку в фоне
        asyncio.create_task(_send_message_with_retries(bot, text))
        log.info("Task for _send_message_with_retries has been created.")

    except KeyError as e:
        log.exception("Failed to format order card due to missing key: %s. Order data: %s", e, order_data)
    except Exception as e:
        log.exception("Failed to format or start publishing order card: %s", e)