# bot/handlers/link.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.premium import is_premium
from bot.services.logs import send_log, log_link_step


def register_link_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(filters.command("start") & filters.private)
    async def start_with_link(client, message):
        parts = message.text.split()

        # ─── NORMAL /start (no payload) ────────────────────────────────
        if len(parts) == 1:
            return  # start.py will handle normal /start

        # ─── START WITH FILE UID ───────────────────────────────────────
        file_uid = parts[1]
        user = message.from_user

        file = await files_col.find_one({"file_uid": file_uid})
        user_db = await users_col.find_one({"user_id": user.id})

        if not file:
            await message.reply_text(
                "❌ Invalid ya expired link.\n"
                "File nahi mili BC."
            )
            return

        # ─── FREE USER → WAIT FLOW ────────────────────────────────────
        if not is_premium(user_db):
            await send_log(
                app,
                log_link_step(
                    user.username,
                    user.id,
                    False,
                    file_uid,
                    file.get("file_name", ""),
                    "FREE_USER_BLOCKED"
                )
            )

            await message.reply_text(
                "🕒 **Free User Detected**\n\n"
                "File ke liye thoda wait karna padega 😏\n"
                "💎 Premium loge to direct milegi.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "Continue",
                        callback_data=f"wait|1|{file_uid}"
                    )
                ]])
            )
            return

        # ─── PREMIUM USER → DIRECT FILE ───────────────────────────────
        await files_col.update_one(
            {"file_uid": file_uid},
            {"$inc": {"downloads": 1}}
        )

        await send_log(
            app,
            log_link_step(
                user.username,
                user.id,
                True,
                file_uid,
                file.get("file_name", ""),
                "PREMIUM_DIRECT_DELIVERY"
            )
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
