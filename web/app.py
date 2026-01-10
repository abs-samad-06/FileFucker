# web/app.py

import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient

from config import Config
from bot.services.shortner import (
    get_link,
    increment_click,
    increment_step
)
from bot.services.logs import (
    send_log,
    log_link_step
)

# ─── APP ──────────────────────────────────────────────────────────────
app = FastAPI(title="FileFucker Web")

# ─── DB ───────────────────────────────────────────────────────────────
mongo = AsyncIOMotorClient(Config.DATABASE_URL)
db = mongo["filefucker"]

# ─── HTML TEMPLATES (INLINE) ──────────────────────────────────────────
def page_html(title, wait, btn_text, next_url):
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <style>
    body {{ background:#0b0b0b; color:#e6e6e6; font-family: monospace; text-align:center; padding-top:80px; }}
    .box {{ width:360px; margin:auto; border:1px solid #222; padding:20px; }}
    .btn {{ margin-top:20px; padding:12px 18px; background:#00ff9c; color:#000; border:none; cursor:not-allowed; opacity:.5; }}
    .btn.enabled {{ cursor:pointer; opacity:1; }}
    .hint {{ color:#888; margin-top:10px; }}
  </style>
</head>
<body>
  <div class="box">
    <h3>{title}</h3>
    <p>Security verification in progress…</p>
    <!-- PLACE YOUR ADS CODE HERE -->
    <button id="btn" class="btn">{btn_text} ({wait})</button>
    <div class="hint">Do not close this page</div>
  </div>

<script>
let t = {wait};
let btn = document.getElementById("btn");
let timer = setInterval(() => {{
  t--;
  btn.innerText = "{btn_text} (" + t + ")";
  if (t <= 0) {{
    clearInterval(timer);
    btn.classList.add("enabled");
    btn.style.cursor = "pointer";
    btn.onclick = () => window.location.href = "{next_url}";
  }}
}}, 1000);
</script>
</body>
</html>
"""


# ─── ROUTES ───────────────────────────────────────────────────────────
@app.get("/l/{token}", response_class=HTMLResponse)
async def step1(token: str, request: Request):
    link = await get_link(db, token)
    if not link:
        raise HTTPException(404, "Invalid link")

    await increment_click(db, token)
    await increment_step(db, token, 1)

    # log (fire-and-forget)
    asyncio.create_task(
        send_log(
            request.app.state.bot,
            log_link_step(
                username=None,
                user_id=link["owner_id"],
                is_premium=link["is_premium"],
                link_id=token,
                file_name=link["file_name"],
                step="PAGE 1 (10s)"
            )
        )
    )

    return page_html(
        "STEP 1 / 3",
        10,
        "Continue",
        f"/l/{token}/2"
    )


@app.get("/l/{token}/2", response_class=HTMLResponse)
async def step2(token: str, request: Request):
    link = await get_link(db, token)
    if not link:
        raise HTTPException(404, "Invalid link")

    await increment_step(db, token, 2)

    asyncio.create_task(
        send_log(
            request.app.state.bot,
            log_link_step(
                username=None,
                user_id=link["owner_id"],
                is_premium=link["is_premium"],
                link_id=token,
                file_name=link["file_name"],
                step="PAGE 2 (15s)"
            )
        )
    )

    return page_html(
        "STEP 2 / 3",
        15,
        "Continue",
        f"/l/{token}/3"
    )


@app.get("/l/{token}/3", response_class=HTMLResponse)
async def step3(token: str, request: Request):
    link = await get_link(db, token)
    if not link:
        raise HTTPException(404, "Invalid link")

    await increment_step(db, token, 3)

    asyncio.create_task(
        send_log(
            request.app.state.bot,
            log_link_step(
                username=None,
                user_id=link["owner_id"],
                is_premium=link["is_premium"],
                link_id=token,
                file_name=link["file_name"],
                step="PAGE 3 (5s)"
            )
        )
    )

    return page_html(
        "FINAL STEP",
        5,
        "Get File",
        f"/go/{token}"
    )


@app.get("/go/{token}")
async def go(token: str):
    # Final redirect to Telegram
    return RedirectResponse(
        url=f"https://t.me/{Config.BOT_NAME}?start={token}",
        status_code=302
    )


# ─── STARTUP HOOK ─────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    # Placeholder to attach bot instance later
    app.state.bot = None
