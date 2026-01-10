# bot/handlers/stats.py

from pyrogram import filters
from pyrogram.types import Message

from config import Config
from bot.services.shortener import link_stats


def register_stats_handlers(app, db, users_col):

    def is_owner(user_id: int) -> bool:
        return user_id == Config.OWNER_ID

    @app.on_message(filters.command("usage") & filters.private)
    async def usage_cmd(client, message: Message):
        parts = message.text.split()

        if len(parts) < 2:
            await message.reply_text(
                "❌ Usage:\n"
                "`/usage <token>`",
                disable_web_page_preview=True
            )
            return

        token = parts[1]
        stats = await link_stats(db, token)

        if not stats:
            await message.reply_text("❌ Invalid token ya data nahi mila.")
            return

        await message.reply_text(
            f"""📊 **Link Usage Stats**

🔗 Token: `{stats['token']}`
📄 File: `{stats['file_name']}`

👆 Clicks: `{stats['clicks']}`
🧩 Step 1: `{stats['step_1']}`
🧩 Step 2: `{stats['step_2']}`
🧩 Step 3: `{stats['step_3']}`

🕒 Created: `{stats['created_at']}`
""",
            disable_web_page_preview=True
        )

    @app.on_message(filters.command("stats") & filters.private)
    async def owner_stats(client, message: Message):
        if not is_owner(message.from_user.id):
            return

        files_col = db["files"]
        links_col = db["links"]

        total_files = await files_col.count_documents({})
        total_links = await links_col.count_documents({})
        total_clicks = 0

        async for link in links_col.find({}):
            total_clicks += link.get("clicks", 0)

        await message.reply_text(
            f"""📈 **System Stats (Owner)**

📦 Total Files: `{total_files}`
🔗 Total Links: `{total_links}`
👆 Total Clicks: `{total_clicks}`
""",
            disable_web_page_preview=True
        )
