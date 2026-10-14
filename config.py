import os
from dotenv import load_dotenv

HOST = "0.0.0.0"



load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
PORT = int(os.getenv("PORT", 8080))
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8080").rstrip("/")

# Manual card transfer settings
CARD_NUMBER = os.getenv("CARD_NUMBER", "9860 6004 0697 7147")
CARD_OWNER = os.getenv("CARD_OWNER", "XUJAMURATOVA ZARGUL")
NEWS_LINK = os.getenv("NEWS_LINK", "https://t.me/YAKUDZA_UC_NEWS")
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/yakfast_support")

# Web admin panel password
ADMIN_PANEL_KEY = os.getenv("ADMIN_PANEL_KEY", "yakudza2026")

# Click Billing Config
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")

# Payme Billing Config
PAYME_MERCHANT_ID = os.getenv("PAYME_MERCHANT_ID", "")
PAYME_SECRET_KEY = os.getenv("PAYME_SECRET_KEY", "")

# Basic validation
if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("WARNING: BOT_TOKEN is not set in .env! Please set it.")
if not ADMIN_IDS:
    print("WARNING: ADMIN_IDS are not set in .env! Please add at least one admin Telegram ID.")
if not CLICK_SECRET_KEY or not PAYME_SECRET_KEY:
    print("INFO: Automated billing (Click/Payme merchant keys) is not fully set up. Manual card transfer mode will be active.")

