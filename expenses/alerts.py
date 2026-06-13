from __future__ import annotations

import logging
import os
import threading

import requests

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")


def _post(message: str) -> None:
    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not set; skipping budget alert.")
        return
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to deliver budget alert to Discord.")


def send_budget_alert(
    category_name: str, spent, limit, currency: str, period: str
) -> None:
    message = (
        f'**Budget alert:** "{category_name}" is over its monthly limit.\n'
        f"Spent {spent} / {limit} {currency} for {period}."
    )
    threading.Thread(target=_post, args=(message,), daemon=True).start()
