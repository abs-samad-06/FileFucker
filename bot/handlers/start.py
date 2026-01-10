# bot/handlers/start.py

from pyrogram import filters
from pyrogram.types import Message

from bot.services.users import get_or_create_user, update_last_active
from bot.services.logs import send_log, log_user_connected


def register_start_handler(app, users_col):

    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client, message: Message):
        user = message.from_user
        parts = message.text.split()

        # ─── DEEP LINK CASE ───────────────────────────────────────────
        # Agar /start ke saath payload hai
        # to link.py handle karega, yahan chup BC
        if len(parts) > 1:
            return

        # ─── USER DB ────────────────────────────────────────────────
        user_db = await get_or_create_user(users_col, user)
        await update_last_active(users_col, user.id)

        # ─── LOG ONLY ON FIRST JOIN ─────────────────────────────────
        if user_db.get("joined_at"):
            await send_log(
                app,
                log_user_connected(
                    user.username,
                    user.id
                )
            )

        # ─── WELCOME MESSAGE ────────────────────────────────────────
        await message.reply_text(
            f"""
🔥 **WELCOME TO FILEFUCKER BOT** 🔥

👋 Oye {user.first_name or 'BC'}  
Files sambhal ke rakhne ka kaam mera  
Aur link bana ke baantne ka kaam tera 😈

━━━━━━━━━━━━━━━━━━
💎 **KYA KARTA HAI YE BOT?**
━━━━━━━━━━━━━━━━━━
📤 File upload karo  
🔗 Secure download link banao  
📈 Downloads track karo  
⚡ Premium me direct access  

━━━━━━━━━━━━━━━━━━
🚀 **USE KARNE KA TAREEKA**
━━━━━━━━━━━━━━━━━━
1️⃣ Koi bhi file bhejo  
2️⃣ `/genlink` likho  
3️⃣ Jo link mile usko share karo  

━━━━━━━━━━━━━━━━━━
💎 **PREMIUM USERS**
━━━━━━━━━━━━━━━━━━
• No wait  
• Direct file  
• No bakchodi  

📌 Premium ke liye `/request` bhejo

━━━━━━━━━━━━━━━━━━
😎 Ready ho?
File bhejo aur system hila do BC 🔥
""",
            disable_web_page_preview=True
        )
