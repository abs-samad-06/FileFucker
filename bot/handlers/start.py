# bot/handlers/start.py

from pyrogram import filters
from pyrogram.types import Message

from bot.services.users import get_or_create_user, update_last_active
from bot.services.logs import send_log, log_user_connected


def register_start_handler(app, users_col):

    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client, message: Message):
        parts = message.text.split()
        user = message.from_user

        # ─── DEEP LINK CASE ───────────────────────────────────────────
        # Agar /start ke saath token hai, to yahan kuch nahi karega
        # link.py usko handle karega
        if len(parts) > 1:
            return

        # ─── NORMAL /start ───────────────────────────────────────────
        user_db = await get_or_create_user(users_col, user)
        await update_last_active(users_col, user.id)

        # log only on first join
        if user_db.get("joined_at"):
            await send_log(
                app,
                log_user_connected(user.username, user.id)
            )

        await message.reply_text(
            f"""
🔥 **Welcome to FileFucker Bot**

👋 Hi {user.first_name or 'bro'}  
Yahan files upload karo aur **secure download links** banao 😎

💎 **Premium users** ko:
• Direct file access  
• No wait  
• No ads  

📌 **How to use**
1️⃣ File bhejo  
2️⃣ `/genlink` likho  
3️⃣ Link share karo  

Ready ho? File daal BC 😈
""",
            disable_web_page_preview=True
        )
