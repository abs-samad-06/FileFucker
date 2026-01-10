# bot/services/broadcast.py

import asyncio
from typing import List, Dict
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid

BATCH_SIZE = 30
SLEEP_BETWEEN_BATCHES = 2


async def send_in_batches(
    app,
    user_ids: List[int],
    text: str
) -> Dict[str, int]:
    sent = 0
    failed = 0

    for i in range(0, len(user_ids), BATCH_SIZE):
        batch = user_ids[i:i + BATCH_SIZE]
        for uid in batch:
            try:
                await app.send_message(uid, text)
                sent += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                try:
                    await app.send_message(uid, text)
                    sent += 1
                except Exception:
                    failed += 1
            except (UserIsBlocked, PeerIdInvalid):
                failed += 1
            except Exception:
                failed += 1

        await asyncio.sleep(SLEEP_BETWEEN_BATCHES)

    return {"sent": sent, "failed": failed}
