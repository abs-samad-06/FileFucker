# bot/handlers/request.py

from pyrogram import filters
from pyrogram.types import Message

from config import Config
from bot.services.logs import send_log, hacker_block


def register_request_handler(app, users_col):

    @app.on_message(filters.command("request") & filters.private)
    async def request_cmd(client, message: Message):
        user = message.from_user

        # fetch user
        user_db = await users_col.find_one({"user_id": user.id})

        if user_db and user_db.get("is_premium"):
            await message.reply_text(
                "😎 Tu already premium hai bhai.\n"
                "Aur kitna premium lega?"
            )
            return

        # build admin message
        admin_text = hacker_block(
            "PREMIUM ACCESS REQUEST",
            f"👤 User: @{user.username or 'N/A'}\n"
            f"🆔 ID: {user.id}\n"
            f"💬 Message: User requested premium access"
        )

        # send to admin
        try:
            await app.send_message(
                chat_id=Config.OWNER_ID,
                text=admin_text
            )

            # if user replied with media (screenshot)
            if message.reply_to_message:
                try:
                    await message.reply_to_message.forward(Config.OWNER_ID)
                except Exception:
                    pass

            await send_log(app, admin_text)

            await message.reply_text(
                "📩 **Request Sent Successfully**\n\n"
                "Admin ko notify kar diya hai.\n"
                "Verification ke baad premium activate hoga 💎"
            )

        except Exception:
            await message.reply_text(
                "⚠️ Request send nahi ho pa rahi.\n"
                "Baad me try kar MC."
        )
