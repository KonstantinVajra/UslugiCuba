# config.py
import os
from dotenv import load_dotenv

# грузим .env из корня проекта
load_dotenv()

# === BOT TOKENS ===
CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN", "")

# === ADMIN CHAT ===
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# === ADMIN USERS ===
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in admin_ids_str.split(',') if admin_id.strip()]


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
    ADMIN_IDS=ADMIN_IDS,
    HOURS_FROM=HOURS_FROM,
    HOURS_TO=HOURS_TO,
    DB_HOST=DB_HOST,
    DB_PORT=DB_PORT,
    DB_NAME=DB_NAME,
    DB_USER=DB_USER,
    DB_PASSWORD=DB_PASSWORD,
    DB_SSLMODE=DB_SSLMODE,
)
