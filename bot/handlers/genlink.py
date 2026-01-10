# bot/handlers/genlink.py

from pyrogram import filters
from pyrogram.types import Message

from bot.services.shortener import create_link
from bot.services.premium import is_premium
from bot.services.users import update_last_active


def register_genlink_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(filters.command("genlink") & filters.private)
    async def genlink_handler(client, message: Message):
        user = message.from_user
        await update_last_active(users_col, user.id)

        # last uploaded file by user
        file = await files_col.find_one(
            {"uploaded_by": user.id},
            sort=[("uploaded_at", -1)]
        )

        if not file:
            await message.reply_text(
                "❌ Koi file nahi mili.\n"
                "Pehle file bhej MC 😑"
            )
            return

        user_db = await users_col.find_one({"user_id": user.id})
        premium = is_premium(user_db)

        # create shortener link entry
        link = await create_link(
            db,
            owner_id=user.id,
            file_id=file["file_id"],
            file_name=file.get("file_name", ""),
            is_premium=premium
        )

        bot = await app.get_me()
        share_link = f"https://t.me/{bot.username}?start={link['token']}"

        await message.reply_text(
            f"""🔗 **Link Generated**

📎 File: `{file.get('file_name')}`
💎 Premium: `{'YES' if premium else 'NO'}`

👉 Share this link:
{share_link}
""",
            disable_web_page_preview=True
        )
