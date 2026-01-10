# bot/services/premium.py

from datetime import datetime, timedelta
from config import Config


def calculate_expiry(days: int) -> str:
    expiry_date = datetime.utcnow() + timedelta(days=days)
    return expiry_date.strftime("%Y-%m-%d")


def is_expired(expiry_date: str | None) -> bool:
    if not expiry_date:
        return True
    return datetime.utcnow().date() > datetime.strptime(expiry_date, "%Y-%m-%d").date()
