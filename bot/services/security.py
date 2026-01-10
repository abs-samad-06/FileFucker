# bot/services/security.py

from datetime import datetime


def ban_payload(reason: str | None = None):
    return {
        "banned": True,
        "ban_reason": reason or "Violation detected",
        "banned_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }


def unban_payload():
    return {
        "banned": False,
        "ban_reason": None,
        "banned_at": None
    }
