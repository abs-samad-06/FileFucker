# bot/handlers/link.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from bot.services.shortner import create_link
from bot.services.logs import send_log, log_link_step


def register_link_handler(app, db, users_col):
    """
    Registers /link command.
    Usage:
      - Reply to a FILE with /link
    Behavior:
      - Premium user -> direct file
      - Free user    -> web short link (ad funnel)
    """

    @app.on_message(filters.command("link") & filters.private)
    async def link_handler(client, message):
        # Must reply to a file
        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply_text(
                "Reply to a file with /link to generate access."
            )

        user_id = message.from_user.id
        user = await users_col.find_one({"user_id": user_id})
        if not user:
            return await message.reply_text("User not registered. Send /start first.")

        doc = message.reply_to_message.document
        file_id = doc.file_id
        file_name = doc.file_name or "file"

        # ─── PREMIUM USER: DIRECT FILE ────────────────────────────────
        if user.get("is_premium"):
            await client.send_document(
                chat_id=user_id,
                document=file_id,
                caption="💎 **Premium Access**\nDirect file delivery enabled."
            )

            # Log direct access
            await send_log(
                client,
                log_link_step(
                    username=message.from_user.username,
                    user_id=user_id,
                    is_premium=True,
                    link_id="DIRECT",
                    file_name=file_name,
                    step="DIRECT DELIVERY"
                )
            )
            return

        # ─── FREE USER: GENERATE SHORT LINK ───────────────────────────
        link_data = await create_link(
            db=db,
            owner_id=user_id,
            file_id=file_id,
            file_name=file_name,
            is_premium=False
        )

        token = link_data["token"]
        web_url = f"https://{Config.BOT_NAME}.herokuapp.com/l/{token}"

        await message.reply_text(
            "🧨 **Free Access Mode**\n\n"
            "File protected by secure delivery.\n"
            "Complete steps to unlock:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔓 Unlock File", url=web_url)]]
            )
        )

        # Log link creation
        await send_log(
            client,
            log_link_step(
                username=message.from_user.username,
                user_id=user_id,
                is_premium=False,
                link_id=token,
                file_name=file_name,
                step="LINK GENERATED"
            )
          )
