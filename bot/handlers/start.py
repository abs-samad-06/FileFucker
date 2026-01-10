# bot/handlers/start.py

from pyrogram import filters
from pyrogram.types import Message


def register_start_handler(app, users_col):

    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client, message: Message):
        user = message.from_user

        await users_col.update_one(
            {"user_id": user.id},
            {
                "$setOnInsert": {
                    "user_id": user.id,
                    "username": user.username,
                    "is_premium": False,
                    "premium_expiry": None
                }
            },
            upsert=True
        )

        await message.reply_text(
            f"👋 **Welcome {user.first_name}!**\n\n"
            "📦 Ye advanced FileStore bot hai.\n\n"
            "💎 Premium users ko **direct files** milti hain\n"
            "🆓 Free users ko **shortener flow** se\n\n"
            "Agar premium chahiye to /request bhejo 😎"
      )
