# bot/handlers/link.py

from pyrogram import filters


def register_link_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(filters.command("start") & filters.private)
    async def start_with_link(client, message):
        parts = message.text.split()

        # Normal /start (no payload)
        if len(parts) == 1:
            return

        file_uid = parts[1]

        file = await files_col.find_one({"file_uid": file_uid})

        if not file:
            await message.reply_text(
                "❌ Invalid ya expired link.\n"
                "File nahi mili BC."
            )
            return

        # increase download count
        await files_col.update_one(
            {"file_uid": file_uid},
            {"$inc": {"downloads": 1}}
        )

        try:
            await app.send_cached_media(
                chat_id=message.chat.id,
                file_id=file["file_id"],
                caption=f"📎 {file.get('file_name', '')}"
            )
        except Exception:
            await message.reply_text(
                "⚠️ File send nahi ho pa rahi.\n"
                "Baad me try kar MC."
            )
