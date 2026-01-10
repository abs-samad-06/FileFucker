# bot/handlers/genlink.py

from pyrogram import filters


def register_genlink_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(filters.private & filters.command("genlink"))
    async def genlink_handler(client, message):
        user_id = message.from_user.id

        # last file uploaded by this user
        file = await files_col.find_one(
            {"uploaded_by": user_id},
            sort=[("uploaded_at", -1)]
        )

        if not file:
            await message.reply_text(
                "❌ Koi file nahi mili BC.\n"
                "Pehle file bhej fir /genlink chala 😑"
            )
            return

        file_uid = file["file_uid"]

        # simple link (abhi direct)
        link = f"https://t.me/{(await app.get_me()).username}?start={file_uid}"

        await message.reply_text(
            text=(
                "🔗 **File link generated**\n\n"
                f"📎 `{file.get('file_name', 'unknown')}`\n"
                f"🆔 `{file_uid}`\n\n"
                f"👉 **Link:**\n{link}\n\n"
                "😈 Premium hai to direct milega,\n"
                "Free hai to thoda nachayenge."
            ),
            disable_web_page_preview=True
      )
