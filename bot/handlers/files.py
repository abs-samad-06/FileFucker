# bot/handlers/files.py

import uuid
from datetime import datetime
from pyrogram import filters


def register_file_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(filters.private & filters.document)
    async def document_handler(client, message):
        await _handle_file(message, files_col)

    @app.on_message(filters.private & filters.video)
    async def video_handler(client, message):
        await _handle_file(message, files_col)

    @app.on_message(filters.private & filters.audio)
    async def audio_handler(client, message):
        await _handle_file(message, files_col)

    @app.on_message(filters.private & filters.photo)
    async def photo_handler(client, message):
        await _handle_file(message, files_col)


async def _handle_file(message, files_col):
    user = message.from_user
    file = (
        message.document
        or message.video
        or message.audio
        or message.photo
    )

    file_uid = str(uuid.uuid4())

    file_data = {
        "file_uid": file_uid,
        "file_id": file.file_id,
        "file_name": getattr(file, "file_name", "unknown"),
        "file_size": file.file_size,
        "file_type": file.__class__.__name__,
        "uploaded_by": user.id,
        "uploaded_at": datetime.utcnow(),
        "downloads": 0
    }

    await files_col.insert_one(file_data)

    await message.reply_text(
        text=(
            "✅ **File received & saved**\n\n"
            f"📎 Name: `{file_data['file_name']}`\n"
            f"🆔 ID: `{file_uid}`\n\n"
            "🔗 Ab /genlink bhej ke link bana MC 😈"
        )
    )
