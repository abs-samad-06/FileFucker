# bot/services/premium.py

from datetime import datetime, timedelta
from typing import Optional


def is_premium(user: dict | None) -> bool:
    """
    Checks if user is premium and not expired.
    """
    if not user:
        return False

    if not user.get("is_premium"):
        return False

    expiry = user.get("premium_expiry")
    if not expiry:
        return False

    return not is_expired(expiry)


def is_expired(expiry: Optional[datetime]) -> bool:
    """
    Returns True if premium expiry date is passed.
    """
    if not expiry:
        return True

    return datetime.utcnow() > expiry


def calculate_expiry(days: int) -> datetime:
    """
    Returns expiry datetime after X days.
    """
    return datetime.utcnow() + timedelta(days=days)
