# main.py
import asyncio
from bots.client_bot import run_client_bot
from config import config

if __name__ == "__main__":
    print("BOT TOKEN tail:", (config.CLIENT_BOT_TOKEN or "")[-8:])  # диагностика
    try:
        asyncio.run(run_client_bot())
    except KeyboardInterrupt:
        print("Bot stopped")
