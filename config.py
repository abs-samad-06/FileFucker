# config.py
import os
from datetime import timedelta

class Config:
    # ─── BASIC BOT CONFIG ─────────────────────────────────────────────
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")

    # ─── OWNER & ADMINS ───────────────────────────────────────────────
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))

    # Multiple admins comma separated: 12345,67890
    ADMINS = set(
        int(x)
        for x in os.getenv("ADMINS", "").split(",")
        if x.strip().isdigit()
    )

    # Owner is always admin
    ADMINS.add(OWNER_ID)

    # ─── DATABASE ─────────────────────────────────────────────────────
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # ─── CHANNELS ─────────────────────────────────────────────────────
    DB_CHANNEL = int(os.getenv("DB_CHANNEL", "0"))
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))

    # ─── PREMIUM PRICING ──────────────────────────────────────────────
    PREMIUM_PLANS = {
        "7d": {
            "days": 7,
            "price": 25
        },
        "30d": {
            "days": 30,
            "price": 70
        },
        "365d": {
            "days": 365,
            "price": 190
        }
    }

    # ─── SHORTNER / AD FLOW (FIXED) ────────────────────────────────────
    AD_FLOW = [
        {"step": 1, "wait": 10},
        {"step": 2, "wait": 15},
        {"step": 3, "wait": 5}
    ]

    # ─── LANGUAGE ─────────────────────────────────────────────────────
    DEFAULT_LANGUAGE = "en"   # en / hi

    # ─── LOG STYLE ────────────────────────────────────────────────────
    LOG_STYLE = "hacker"  # hacker / clean

    # ─── SECURITY ─────────────────────────────────────────────────────
    MAX_FILE_SIZE_MB = 2000  # Telegram limit safety

    # ─── MISC ─────────────────────────────────────────────────────────
    BOT_NAME = "FileFucker"
    VERSION = "1.0.0"


# Quick sanity check (optional, safe)
def validate_config():
    missing = []
    if not Config.BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not Config.API_ID:
        missing.append("API_ID")
    if not Config.API_HASH:
        missing.append("API_HASH")
    if not Config.OWNER_ID:
        missing.append("OWNER_ID")
    if not Config.DATABASE_URL:
        missing.append("DATABASE_URL")
    if not Config.DB_CHANNEL:
        missing.append("DB_CHANNEL")
    if not Config.LOG_CHANNEL:
        missing.append("LOG_CHANNEL")

    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
