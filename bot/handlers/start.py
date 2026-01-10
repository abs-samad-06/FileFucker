# bot/handlers/start.py

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime


def register_start_handler(app, users_col):

    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client, message: Message):
        user = message.from_user

        # Save user if not exists
        await users_col.update_one(
            {"user_id": user.id},
            {
                "$setOnInsert": {
                    "user_id": user.id,
                    "name": user.first_name,
                    "username": user.username,
                    "joined_at": datetime.utcnow(),
                    "is_premium": False,
                    "premium_expiry": None
                }
            },
            upsert=True
        )

        await message.reply_text(
            f"""🔥 **Welcome {user.first_name}**

Main hoon **FileFucker Bot** 😎  
Files upload karo → main **download link** bana dunga.

📌 Commands:
• `/start` – Bot start
• File bhejo – Link milega

Premium loge to:
⚡ Fast links  
🚫 No limits  

Ab file daal BC 😈
"""
        )
