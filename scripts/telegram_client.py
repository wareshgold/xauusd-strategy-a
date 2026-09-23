"""Minimal Telegram Bot API client shared by the gateway and report layer."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
TELEGRAM_CONFIG = ROOT / "config" / "telegram.json"


@dataclass(frozen=True)
class TelegramSendResult:
    success: bool
    detail: str
    response: dict | None


def read_telegram_config() -> tuple[str | None, str | None]:
    try:
        payload = json.loads(TELEGRAM_CONFIG.read_text(encoding="utf-8"))
        return payload.get("bot_token"), payload.get("chat_id")
    except Exception:
        return None, None


def read_telegram_env(env: dict | None = None) -> tuple[str | None, str | None]:
    source = os.environ if env is None else env
    token = source.get("TELEGRAM_BOT_TOKEN")
    chat = source.get("TELEGRAM_CHAT_ID")
    if token and chat:
        return token, chat
    return read_telegram_config()


def telegram_delivery_status(env: dict | None = None) -> dict:
    bot_token, chat_id = read_telegram_env(env)
    return {
        "bot_configured": bool(bot_token),
        "chat_configured": bool(chat_id),
        "mode": "REAL" if bot_token and chat_id else "MOCK",
    }


def send_telegram_message(text: str, *, bot_token=None, chat_id=None, timeout=15, parse_mode=None, retries=4, env=None):
    if bot_token is None or chat_id is None:
        token, chat = read_telegram_env(env)
        bot_token = bot_token or token
        chat_id = chat_id or chat
    if not bot_token or not chat_id:
        return TelegramSendResult(False, "NOT_CONFIGURED", None)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    if parse_mode:
        params["parse_mode"] = parse_mode
    body = urlencode(params).encode()
    for attempt in range(max(1, retries)):
        try:
            req = Request(url, data=body, method="POST")
            with urlopen(req, timeout=timeout) as response:
                payload = response.read().decode("utf-8", errors="replace")
                status = response.status
            return TelegramSendResult(200 <= status < 300, f"HTTP_{status}", json.loads(payload))
        except Exception as exc:
            if attempt + 1 >= retries:
                return TelegramSendResult(False, f"EXCEPTION: {exc}", None)
            time.sleep(0.75 * (2 ** attempt))
