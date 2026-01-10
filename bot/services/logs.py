# bot/services/logs.py

from datetime import datetime
from config import Config


def _now_utc() -> str:
    return datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S UTC")


def hacker_block(title: str, body: str) -> str:
    """
    Returns a hacker-style formatted log block.
    """
    return (
        f"🛑 {title}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{body}\n"
        f"🕒 Time: {_now_utc()}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )


async def send_log(app, text: str):
    """
    Sends log text to private LOG_CHANNEL safely.
    """
    if not Config.LOG_CHANNEL:
        return
    try:
        await app.send_message(Config.LOG_CHANNEL, text)
    except Exception:
        # Silent fail: logging must never break the bot
        pass


# ─── PREBUILT LOG TEMPLATES ───────────────────────────────────────────

def log_user_connected(username: str | None, user_id: int) -> str:
    return hacker_block(
        "SYSTEM ACCESS DETECTED",
        f"👤 User: @{username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        f"⚠️ Mode: FREE USER"
    )


def log_premium_granted(admin_id: int, target_id: int, expiry: str) -> str:
    return hacker_block(
        "PRIVILEGED ACCESS GRANTED",
        f"👑 Admin ID: {admin_id}\n"
        f"👤 Target ID: {target_id}\n"
        f"⏳ Expiry: {expiry}"
    )


def log_premium_revoked(user_id: int, reason: str) -> str:
    return hacker_block(
        "ACCESS REVOKED",
        f"👤 User ID: {user_id}\n"
        f"⚠️ Reason: {reason}"
    )


def log_security_ban(admin_id: int, target_id: int, reason: str) -> str:
    return hacker_block(
        "SECURITY FLAG RAISED",
        f"👑 Admin ID: {admin_id}\n"
        f"👤 Target ID: {target_id}\n"
        f"🚫 Action: BAN\n"
        f"📝 Reason: {reason}"
    )


def log_security_unban(admin_id: int, target_id: int) -> str:
    return hacker_block(
        "ACCESS RESTORED",
        f"👑 Admin ID: {admin_id}\n"
        f"👤 Target ID: {target_id}\n"
        f"✅ Action: UNBAN"
    )


def log_link_step(
    username: str | None,
    user_id: int,
    is_premium: bool,
    link_id: str,
    file_name: str,
    step: str
) -> str:
    return hacker_block(
        "DELIVERY PIPELINE HIT",
        f"👤 User: @{username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        f"💎 Premium: {'YES' if is_premium else 'NO'}\n"
        f"🔗 Link ID: {link_id}\n"
        f"📄 File: {file_name}\n"
        f"📍 Step: {step}"
    )


def log_system_online(bot_username: str, version: str) -> str:
    return hacker_block(
        "SYSTEM ONLINE",
        f"🤖 Bot: @{bot_username}\n"
        f"🚀 Version: {version}\n"
        f"🧠 Monitoring: ACTIVE"
    )
