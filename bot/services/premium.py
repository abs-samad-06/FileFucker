# bot/services/premium.py

from datetime import datetime, timedelta


def calculate_expiry(days: int):
    return datetime.utcnow() + timedelta(days=days)


def is_premium(user: dict) -> bool:
    if not user:
        return False

    expiry = user.get("premium_expiry")
    if not expiry:
        return False

    if isinstance(expiry, str):
        try:
            expiry = datetime.fromisoformat(expiry)
        except Exception:
            return False

    return datetime.utcnow() < expiry
