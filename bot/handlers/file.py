# bot/handlers/file.py

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime

from bot.services.users import update_last_active


def register_file_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(
        filters.private
        & (
            filters.document
            | filters.video
            | filters.audio
            | filters.photo
        )
    )
    async def file_handler(client, message: Message):
        user = message.from_user
        await update_last_active(users_col, user.id)

        # pick the file object
        file = (
            message.document
            or message.video
            or message.audio
            or message.photo
        )

        file_name = getattr(file, "file_name", "file")
        file_size = getattr(file, "file_size", 0)

        data = {
            "file_id": file.file_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file.__class__.__name__,
            "uploaded_by": user.id,
            "uploaded_at": datetime.utcnow(),
            "downloads": 0
        }

        await files_col.insert_one(data)

        await message.reply_text(
            f"""✅ **File Saved**

📎 Name: `{file_name}`
📦 Size: `{round(file_size/1024/1024, 2)} MB`

🔗 Ab `/genlink` likh ke link bana MC 😈
""",
            disable_web_page_preview=True
        )
