# bot/handlers/link.py

from pyrogram import filters
from bot.services.premium import is_premium


def register_link_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(filters.command("start") & filters.private)
    async def start_with_link(client, message):
        parts = message.text.split()

        # ─── NORMAL /start (no payload) ────────────────────────────────
        if len(parts) == 1:
            return  # let start.py handle normal /start

        # ─── START WITH FILE UID ───────────────────────────────────────
        file_uid = parts[1]
        user_id = message.from_user.id

        file = await files_col.find_one({"file_uid": file_uid})
        user = await users_col.find_one({"user_id": user_id})

        if not file:
            await message.reply_text(
                "❌ Invalid ya expired link.\n"
                "File nahi mili BC."
            )
            return

        # ─── FREE USER LOGIC ───────────────────────────────────────────
        if not is_premium(user):
            await message.reply_text(
                "🕒 **Free User Detected**\n\n"
                "Is file ke liye thoda wait karna padega 😏\n"
                "💎 Premium loge to direct milegi.\n\n"
                "👉 /request bhejo premium ke liye."
            )
            return

        # ─── PREMIUM USER → DIRECT FILE ───────────────────────────────
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
