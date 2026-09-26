"""Test-only Telegram configuration diagnostic (no channel messages sent).

Purpose: verify the Telegram configuration path safely:
- reports whether TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are configured,
  with MASKED fingerprints (first 4 + last 4 chars only) so credentials are
  never exposed in full;
- with --get-me, performs the read-only Bot API `getMe` call, which touches
  only the bot identity (first_name/username/id) — it sends nothing to any
  chat/channel and changes nothing;
- without --get-me, performs NO network call at all.

Safety: never enables real execution, never modifies Strategy A, never
creates a bot, never guesses a chat ID. Exit code 0 when the configuration
is complete (and getMe, if requested, succeeded), 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))

if __package__ in (None, ""):
    from telegram_client import (  # type: ignore
        read_telegram_env,
        telegram_delivery_status,
    )
else:
    from scripts.telegram_client import (  # type: ignore
        read_telegram_env,
        telegram_delivery_status,
    )


def _mask(value: str | None) -> str | None:
    """Fingerprint a secret: first4 + ... + last4, or None."""
    if not value:
        return None
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}...{value[-4:]}"


def _get_me(bot_token: str) -> dict:
    """Read-only Bot API getMe. Returns a structured, credential-free result."""
    from urllib.request import Request, urlopen

    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        with urlopen(Request(url), timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except Exception as exc:
        return {"ok": False, "detail": f"EXCEPTION: {exc}"}
    if not isinstance(payload, dict) or not payload.get("ok"):
        return {"ok": False, "detail": f"API_ERROR: {json.dumps(payload)[:200]}"}
    bot = payload.get("result") or {}
    # Only identity fields are echoed; the token never appears in output.
    return {
        "ok": True,
        "detail": "getMe OK (read-only; no message sent)",
        "bot_first_name": bot.get("first_name"),
        "bot_username": bot.get("username"),
        "bot_id": bot.get("id"),
    }


def diagnose(*, do_get_me: bool = False, env: dict | None = None) -> dict:
    token, chat = read_telegram_env(env)
    status = telegram_delivery_status(env)
    result = {
        "diagnostic": "telegram_configuration (test-only; sends no messages)",
        "bot_token_configured": bool(token),
        "bot_token_fingerprint": _mask(token),
        "chat_id_configured": bool(chat),
        "chat_id_fingerprint": _mask(chat),
        "delivery_mode": status["mode"],
        "configured": bool(token and chat),
        "get_me": None,
    }
    if do_get_me and token:
        result["get_me"] = _get_me(token)
    elif do_get_me:
        result["get_me"] = {"ok": False, "detail": "NOT_CONFIGURED (no token)"}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Telegram configuration diagnostic (test-only)")
    parser.add_argument(
        "--get-me", action="store_true",
        help="also call the read-only Bot API getMe (validates the token; "
        "sends no messages, reveals only the bot identity)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    result = diagnose(do_get_me=args.get_me)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Telegram configuration diagnostic (test-only, no messages sent)")
        print(f"  bot token configured : {result['bot_token_configured']}"
              f"  [{result['bot_token_fingerprint'] or '—'}]")
        print(f"  chat id configured   : {result['chat_id_configured']}"
              f"  [{result['chat_id_fingerprint'] or '—'}]")
        print(f"  delivery mode        : {result['delivery_mode']}")
        print(f"  configuration        : {'COMPLETE' if result['configured'] else 'INCOMPLETE (NOT_CONFIGURED)'}")
        if result["get_me"]:
            gm = result["get_me"]
            print(f"  getMe                : {'OK' if gm.get('ok') else 'FAILED'}"
                  + (f"  bot=@{gm.get('bot_username')}" if gm.get("ok") else f"  ({gm.get('detail')})"))
    return 0 if result["configured"] and (result["get_me"] is None or result["get_me"].get("ok")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
