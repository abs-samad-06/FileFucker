# bot/handlers/request.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from bot.services.logs import send_log, hacker_block


def register_request_handler(app, users_col):
    """
    /request <message>
    - User sends a support request
    - All ADMINS receive it with quick-reply buttons
    """

    def is_admin(user_id: int) -> bool:
        return user_id in Config.ADMINS

    # ─── USER: /request ───────────────────────────────────────────────
    @app.on_message(filters.command("request") & filters.private)
    async def request_handler(client, message):
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            return await message.reply_text(
                "❓ **Support Request**\n\n"
                "Usage:\n"
                "`/request <your message>`\n\n"
                "Example:\n"
                "`/request link not opening`"
            )

        text = parts[1]
        user = await users_col.find_one({"user_id": message.from_user.id})
        if not user:
            return await message.reply_text("Send /start first.")

        # Message to admins
        admin_text = (
            "🆘 **NEW SUPPORT REQUEST**\n\n"
            f"👤 User: @{message.from_user.username or 'N/A'}\n"
            f"🆔 ID: `{message.from_user.id}`\n"
            f"💎 Premium: {'YES' if user.get('is_premium') else 'NO'}\n\n"
            f"📝 Message:\n{text}"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✉️ Reply",
                    callback_data=f"reply_req:{message.from_user.id}"
                )
            ]
        ])

        # Send to all admins
        for admin_id in Config.ADMINS:
            try:
                await client.send_message(
                    admin_id,
                    admin_text,
                    reply_markup=keyboard
                )
            except Exception:
                pass

        await message.reply_text(
            "✅ **Request sent successfully**\n\n"
            "Admin will get back to you soon."
        )

        await send_log(
            client,
            hacker_block(
                "SUPPORT REQUEST QUEUED",
                f"👤 User ID: {message.from_user.id}\n"
                f"💎 Premium: {'YES' if user.get('is_premium') else 'NO'}\n"
                f"📝 Message: {text[:200]}"
            )
        )

    # ─── ADMIN: CLICK REPLY ────────────────────────────────────────────
    @app.on_callback_query(filters.regex("^reply_req:"))
    async def reply_request(client, query):
        if not is_admin(query.from_user.id):
            return await query.answer("Not allowed", show_alert=True)

        target_id = int(query.data.split(":")[1])

        await query.message.reply_text(
            f"✍️ **Reply to User `{target_id}`**\n\n"
            "Send your reply as:\n"
            f"`/reply {target_id} <message>`"
        )

        await query.answer()

    # ─── ADMIN: /reply ────────────────────────────────────────────────
    @app.on_message(filters.command("reply") & filters.private)
    async def reply_handler(client, message):
        if not is_admin(message.from_user.id):
            return

        parts = message.text.split(maxsplit=2)
        if len(parts) != 3:
            return await message.reply_text(
                "Usage:\n`/reply user_id <message>`"
            )

        user_id = int(parts[1])
        reply_text = parts[2]

        try:
            await client.send_message(
                user_id,
                "💬 **Support Reply**\n\n"
                f"{reply_text}"
            )
            await message.reply_text("✅ Reply sent.")
        except Exception:
            await message.reply_text("❌ Failed to send reply.")

        await send_log(
            client,
            hacker_block(
                "SUPPORT RESPONSE SENT",
                f"👑 Admin ID: {message.from_user.id}\n"
                f"👤 Target User: {user_id}\n"
                f"📝 Reply: {reply_text[:200]}"
            )
      )
