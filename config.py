# config.py
import os
from dotenv import load_dotenv

# грузим .env из корня проекта
load_dotenv()

# === BOT TOKENS ===
CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN", "")

# === ADMIN CHAT ===
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or "0")

# === PUBLISHING ===
ORDERS_CHANNEL_ID = int(os.getenv("ORDERS_CHANNEL_ID") or "0")
PUBLISH_MAX_RETRIES = int(os.getenv("PUBLISH_MAX_RETRIES") or "3")
PUBLISH_BACKOFFS = os.getenv("PUBLISH_BACKOFFS") or "30,120,600"

# === TIME SLOTS ===
HOURS_FROM = int(os.getenv("HOURS_FROM", "8"))
HOURS_TO   = int(os.getenv("HOURS_TO", "20"))

# === DATABASE (Timeweb Cloud) ===
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "services")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

assert CLIENT_BOT_TOKEN, "CLIENT_BOT_TOKEN is missing in .env"

# в конце config.py
from types import SimpleNamespace

config = SimpleNamespace(
    CLIENT_BOT_TOKEN=CLIENT_BOT_TOKEN,
    ADMIN_CHAT_ID=ADMIN_CHAT_ID,
    HOURS_FROM=HOURS_FROM,
    HOURS_TO=HOURS_TO,
    DB_HOST=DB_HOST,
    DB_PORT=DB_PORT,
    DB_NAME=DB_NAME,
    DB_USER=DB_USER,
    DB_PASSWORD=DB_PASSWORD,
    DB_SSLMODE=DB_SSLMODE,
    # publisher
    ORDERS_CHANNEL_ID=ORDERS_CHANNEL_ID,
    PUBLISH_MAX_RETRIES=PUBLISH_MAX_RETRIES,
    PUBLISH_BACKOFFS=PUBLISH_BACKOFFS,
)
