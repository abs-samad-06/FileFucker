# bot/services/premium.py

from datetime import datetime, timedelta
from typing import Optional


def calculate_expiry(days: int) -> datetime:
    """
    Calculate premium expiry datetime.
    """
    return datetime.utcnow() + timedelta(days=days)


def is_expired(expiry: Optional[datetime]) -> bool:
    """
    Check whether premium is expired.
    """
    if not expiry:
        return True

    # expiry can be string if stored badly, handle safely
    if isinstance(expiry, str):
        try:
            expiry = datetime.fromisoformat(expiry)
        except Exception:
            return True

    return datetime.utcnow() > expiry
