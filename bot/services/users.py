# bot/services/users.py

from datetime import datetime
from typing import Optional, Dict


async def get_or_create_user(users_col, user) -> Dict:
    """
    Fetches user from DB or creates a new one.
    """
    existing = await users_col.find_one({"user_id": user.id})
    if existing:
        return existing

    data = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "language": "en",          # future /language
        "is_premium": False,
        "premium_expiry": None,

        # stats
        "total_downloads": 0,

        # timestamps
        "joined_at": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }

    await users_col.insert_one(data)
    return data


async def update_last_active(users_col, user_id: int):
    """
    Updates last active timestamp.
    """
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"last_active": datetime.utcnow()}}
    )


async def increment_download(users_col, user_id: int):
    """
    Increments total downloads count.
    """
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"total_downloads": 1}}
    )


async def get_user(users_col, user_id: int) -> Optional[Dict]:
    """
    Fetch user without creating.
    """
    return await users_col.find_one({"user_id": user_id})
