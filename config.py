# config.py
import os
from dotenv import load_dotenv

# важно: .env перекрывает системные переменные
load_dotenv(override=True)

class Config:
    CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN")
    DEFAULT_LANGUAGE = "en"

config = Config()
