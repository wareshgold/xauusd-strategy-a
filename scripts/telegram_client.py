"""Minimal Telegram Bot API client shared by the gateway and the report layer.

Reporting/infrastructure only:
- transport adapter for an already-authorized, already-formatted message;
- does not calculate SP2L geometry, alter direction, or create signals;
- credentials are read from TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID at call time.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class TelegramSendResult:
    success: bool
    detail: str  # NOT_CONFIGURED | HTTP_200 | EXCEPTION: ... | HTTP_<status>
    response: dict | None


def read_telegram_env(env: dict | None = None) -> tuple[str | None, str | None]:
    source = os.environ if env is None else env
    return source.get("TELEGRAM_BOT_TOKEN"), source.get("TELEGRAM_CHAT_ID")


def telegram_delivery_status(env: dict | None = None) -> dict:
    """Pre-delivery destination status from existing configuration only.

    mode REAL means both TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set and
    a real API call will be attempted. mode MOCK means nothing will leave
    the host (calls return NOT_CONFIGURED). No bot is created and no chat
    ID is guessed anywhere in this codebase.
    """
    bot_token, chat_id = read_telegram_env(env)
    bot_configured = bool(bot_token)
    chat_configured = bool(chat_id)
    return {
        "bot_configured": bot_configured,
        "chat_configured": chat_configured,
        "mode": "REAL" if (bot_configured and chat_configured) else "MOCK",
    }


def send_telegram_message(
    text: str,
    *,
    bot_token: str | None = None,
    chat_id: str | None = None,
    timeout: float = 15,
    parse_mode: str | None = None,
    retries: int = 4,
    env: dict | None = None,
) -> TelegramSendResult:
    """Send one text message. Falls back to environment credentials.

    parse_mode: optional Telegram formatting (e.g. "HTML"). Plain text
    when omitted.

    Never raises: every failure mode is returned as a structured result so
    callers can log it deterministically.
    """
    if bot_token is None or chat_id is None:
        env_token, env_chat = read_telegram_env(env)
        bot_token = bot_token or env_token
        chat_id = chat_id or env_chat

    if not bot_token or not chat_id:
        return TelegramSendResult(success=False, detail="NOT_CONFIGURED", response=None)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params: dict[str, str] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        params["parse_mode"] = parse_mode
    body = urlencode(params).encode()
    last_exc: Exception | None = None
    for attempt in range(max(1, retries)):
        try:
            req = Request(
                url,
                data=body,
                method="POST",
                headers={"Connection": "close", "User-Agent": "SP2L-Telegram/1.0"},
            )
            with urlopen(req, timeout=timeout) as response:
                status = response.status
                payload = response.read().decode("utf-8", errors="replace")
            break
        except Exception as exc:  # transient network failures are retried
            last_exc = exc
            if attempt + 1 >= max(1, retries):
                return TelegramSendResult(
                    success=False,
                    detail=f"EXCEPTION: {exc}",
                    response=None,
                )
            time.sleep(0.75 * (2 ** attempt))
    else:
        return TelegramSendResult(
            success=False,
            detail=f"EXCEPTION: {last_exc}",
            response=None,
        )

    try:
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            parsed = {"raw": payload[:512]}
    except Exception:
        parsed = {"raw": payload[:512]}

    if 200 <= status < 300:
        return TelegramSendResult(success=True, detail=f"HTTP_{status}", response=parsed)
    return TelegramSendResult(success=False, detail=f"HTTP_{status}", response=parsed)
