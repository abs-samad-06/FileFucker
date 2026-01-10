# bot/services/shortener.py

import secrets
from datetime import datetime
from typing import Optional, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase


# ─── COLLECTION NAME ──────────────────────────────────────────────────
COLLECTION_NAME = "links"


# ─── HELPERS ──────────────────────────────────────────────────────────
def generate_token(length: int = 8) -> str:
    """
    Generates a secure random short token.
    Example: yKHE9aQ2
    """
    return secrets.token_urlsafe(length)[:length]


# ─── CORE SHORTENER LOGIC ─────────────────────────────────────────────
async def create_link(
    db: AsyncIOMotorDatabase,
    *,
    owner_id: int,
    file_id: str,
    file_name: str,
    is_premium: bool
) -> Dict:
    """
    Creates a new short link entry.
    """
    token = generate_token()

    # ensure uniqueness (very rare collision, but still)
    while await db[COLLECTION_NAME].find_one({"token": token}):
        token = generate_token()

    data = {
        "token": token,

        # ownership
        "owner_id": owner_id,
        "file_id": file_id,
        "file_name": file_name,
        "is_premium": is_premium,

        # tracking
        "created_at": datetime.utcnow(),
        "clicks": 0,

        # wait-step tracking
        "step_1": 0,
        "step_2": 0,
        "step_3": 0,

        # flags
        "active": True
    }

    await db[COLLECTION_NAME].insert_one(data)
    return data


async def get_link(
    db: AsyncIOMotorDatabase,
    token: str
) -> Optional[Dict]:
    """
    Fetch link data by token.
    """
    return await db[COLLECTION_NAME].find_one(
        {"token": token, "active": True}
    )


async def increment_click(
    db: AsyncIOMotorDatabase,
    token: str
):
    """
    Increments total click count.
    """
    await db[COLLECTION_NAME].update_one(
        {"token": token},
        {"$inc": {"clicks": 1}}
    )


async def increment_step(
    db: AsyncIOMotorDatabase,
    token: str,
    step: int
):
    """
    Tracks step hit (1 / 2 / 3).
    """
    if step not in (1, 2, 3):
        return

    await db[COLLECTION_NAME].update_one(
        {"token": token},
        {"$inc": {f"step_{step}": 1}}
    )


async def deactivate_link(
    db: AsyncIOMotorDatabase,
    token: str
):
    """
    Disables a link permanently.
    """
    await db[COLLECTION_NAME].update_one(
        {"token": token},
        {"$set": {"active": False}}
    )


# ─── STATS ────────────────────────────────────────────────────────────
async def link_stats(
    db: AsyncIOMotorDatabase,
    token: str
) -> Optional[Dict]:
    """
    Returns usage stats for a link.
    """
    link = await db[COLLECTION_NAME].find_one({"token": token})
    if not link:
        return None

    return {
        "token": token,
        "file_name": link.get("file_name"),
        "clicks": link.get("clicks", 0),
        "step_1": link.get("step_1", 0),
        "step_2": link.get("step_2", 0),
        "step_3": link.get("step_3", 0),
        "created_at": link.get("created_at")
  }
