import os


API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MTPROXY_URL = os.getenv("MTPROXY_URL")
MTPROXY_PORT = int(os.getenv("MTPROXY_PORT"))
MTPROXY_SECRET = os.getenv("MTPROXY_SECRECT")

ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")