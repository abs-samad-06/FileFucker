# bot/services/users.py

from datetime import datetime


async def get_or_create_user(users_col, user):
    existing = await users_col.find_one({"user_id": user.id})

    if existing:
        return existing

    new_user = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "is_premium": False,
        "premium_expiry": None,
        "joined_at": datetime.utcnow()
    }

    await users_col.insert_one(new_user)
    return new_user
