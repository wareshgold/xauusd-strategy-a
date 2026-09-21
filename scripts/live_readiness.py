"""Pre-flight live-readiness checker for the MT5 gateway (ops infrastructure).

This module performs NO strategy computation and NO trading. It only inspects:

- the environment configuration (LIVE_TRADING_ENABLE, ALLOW_REAL_EXECUTION,
  Telegram variables via the shared client);
- the MT5 terminal/account state (connection, algo-trading button,
  account trade permissions);
- the symbol specification (visibility, trade mode, stops level, volume
  min/step/max, tick value/size).

Safety contract (unchanged):
- LIVE_TRADING_ENABLE defaults to false everywhere; this module never flips it.
- Real order execution additionally requires the operator-level double gate
  LIVE_TRADING_ENABLE=true AND ALLOW_REAL_EXECUTION=true (added to the
  gateway's execute path) — this checker only reports their state.
- Any FAILED item must be resolved by the operator; the checker never
  "fixes" anything and never invents missing configuration.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

if __package__ in (None, ""):
    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))

try:  # direct-script compatibility (repo pattern)
    from live_mt5_gateway import SYMBOL  # type: ignore
    from telegram_client import telegram_delivery_status  # type: ignore
except ModuleNotFoundError:  # pytest / package mode
    from scripts.live_mt5_gateway import SYMBOL  # type: ignore
    from scripts.telegram_client import telegram_delivery_status  # type: ignore

# account_info().margin_mode values (MetaTrader5 package constants)
MARGIN_MODE_RETAIL_HEDGING = 2

# symbol_info().trade_mode values
SYMBOL_TRADE_MODE_DISABLED = 0
SYMBOL_TRADE_MODE_FULL = 3
# Modes that allow OPENING new positions. Everything else — DISABLED (0),
# CLOSEONLY (4), or unknown — is a HARD real-execution blocker, not merely a
# degraded state.
OPENABLE_SYMBOL_TRADE_MODES = {1, 2, 3}
_SYMBOL_TRADE_MODE_NAMES = {
    0: "DISABLED",
    1: "LONGONLY",
    2: "SHORTONLY",
    3: "FULL",
    4: "CLOSEONLY",
}


def double_gate_state() -> dict:
    """Report the two-key real-execution gate without ever flipping it."""
    live = os.getenv("LIVE_TRADING_ENABLE", "false").strip().lower() == "true"
    allow = os.getenv("ALLOW_REAL_EXECUTION", "false").strip().lower() == "true"
    return {
        "live_trading_enable": live,
        "allow_real_execution": allow,
        "real_execution_possible": live and allow,
        "detail": (
            "LIVE_TRADING_ENABLE=true AND ALLOW_REAL_EXECUTION=true -> REAL orders possible"
            if (live and allow)
            else (
                "LIVE_TRADING_ENABLE=true but ALLOW_REAL_EXECUTION!=true -> dry-run only"
                if live
                else "LIVE_TRADING_ENABLE=false -> dry-run only"
            )
        ),
    }


def _probe_mt5(symbol: str) -> dict:
    """Probe the local MT5 terminal. Inspection only; always shuts down."""
    out: dict = {"initialize": False}
    mt5 = None
    try:
        import MetaTrader5 as mt5  # noqa: PLC0415
    except ImportError:
        out["error"] = "MetaTrader5 python package not importable"
        return out

    try:
        if not mt5.initialize():
            out["error"] = f"MT5 initialize failed: {mt5.last_error()}"
            return out
        out["initialize"] = True

        terminal = mt5.terminal_info()
        account = mt5.account_info()
        out["terminal_connected"] = bool(terminal.connected) if terminal else None
        # terminal_info().trade_allowed = the terminal "Algo Trading" button.
        out["terminal_algo_trading"] = bool(terminal.trade_allowed) if terminal else None

        out["account_login"] = int(account.login) if account else None
        out["account_server"] = str(account.server) if account else None
        out["account_currency"] = str(account.currency) if account else None
        out["account_leverage"] = int(account.leverage) if account else None
        out["margin_mode"] = int(account.margin_mode) if account else None
        # account_info().trade_allowed = account-level trading permission.
        out["account_trade_allowed"] = bool(account.trade_allowed) if account else None
        # account_info().trade_expert = account allows trading via API/experts.
        out["account_trade_expert"] = bool(account.trade_expert) if account else None

        if mt5.symbol_select(symbol, True):
            info = mt5.symbol_info(symbol)
            if info is not None:
                out["symbol_visible"] = bool(info.visible)
                out["symbol_trade_mode"] = int(info.trade_mode)
                out["symbol_trade_mode_name"] = _SYMBOL_TRADE_MODE_NAMES.get(
                    int(info.trade_mode), str(info.trade_mode)
                )
                out["stops_level_points"] = int(info.trade_stops_level)
                out["volume_min"] = float(info.volume_min)
                out["volume_step"] = float(info.volume_step)
                out["volume_max"] = float(info.volume_max)
                out["tick_value"] = float(info.trade_tick_value)
                out["tick_size"] = float(info.trade_tick_size)
            else:
                out["symbol_visible"] = None
                out["error"] = f"symbol_info({symbol}) returned None"
        else:
            out["symbol_visible"] = False
            out["error"] = f"symbol_select({symbol}) failed: {mt5.last_error()}"
    except Exception as exc:  # defensive: probe must never crash the caller
        out.setdefault("error", f"probe exception: {exc!r}")
    finally:
        try:
            if out.get("initialize"):
                mt5.shutdown()
        except Exception:
            pass
    return out


def _mt5_items(mt5: dict) -> list[dict]:
    items: list[dict] = []
    if not mt5.get("initialize"):
        items.append({
            "item": "mt5_terminal",
            "status": "FAILED",
            "detail": mt5.get("error", "MT5 initialize failed"),
        })
        return items

    connected = mt5.get("terminal_connected") is True
    algo = mt5.get("terminal_algo_trading") is True
    items.append({
        "item": "mt5_terminal",
        "status": "OK" if (connected and algo) else "FAILED",
        "detail": (
            f"connected={connected} algo_trading={algo} "
            f"login={mt5.get('account_login')} server={mt5.get('account_server')}"
        ),
        "connected": connected,
        "algo_trading_enabled": algo,
    })

    acct_ok = (
        mt5.get("account_trade_allowed") is True
        and mt5.get("account_trade_expert") is True
    )
    items.append({
        "item": "mt5_account_permissions",
        "status": "OK" if acct_ok else "FAILED",
        "detail": (
            f"account_trade_allowed={mt5.get('account_trade_allowed')} "
            f"account_trade_expert={mt5.get('account_trade_expert')} "
            f"margin_mode={mt5.get('margin_mode')} "
            f"(hedging={mt5.get('margin_mode') == MARGIN_MODE_RETAIL_HEDGING})"
        ),
    })

    mode = mt5.get("symbol_trade_mode")
    visible = mt5.get("symbol_visible") is True
    # CLOSEONLY/DISABLED/unknown are HARD real-execution blockers: they make
    # the whole readiness verdict NOT_READY, never merely degraded.
    openable = mode in OPENABLE_SYMBOL_TRADE_MODES
    tradable = visible and openable
    items.append({
        "item": "mt5_symbol_spec",
        "status": "OK" if tradable else "FAILED",
        "detail": (
            f"{SYMBOL} visible={visible} "
            f"trade_mode={_SYMBOL_TRADE_MODE_NAMES.get(mode, mode)} "
            f"openable={openable} "
            f"stops_level={mt5.get('stops_level_points')}pts "
            f"volume_min={mt5.get('volume_min')} "
            f"volume_step={mt5.get('volume_step')} "
            f"tick_value={mt5.get('tick_value')}"
        ),
    })
    return items


def check_live_readiness(*, symbol: str | None = None, probe_mt5: bool = True) -> dict:
    """Full readiness check. Pure inspection; never mutates anything.

    Returns a dict with per-item status OK / FAILED / DEGRADED / SKIPPED and a
    top-level verdict READY / NOT_READY. FAILED blocks real execution;
    DEGRADED (Telegram unconfigured) only blocks alerts, not execution.
    """
    symbol = symbol or SYMBOL
    gate = double_gate_state()
    items: list[dict] = []

    items.append({
        "item": "real_execution_double_gate",
        "status": "OK" if gate["real_execution_possible"] else "SKIPPED",
        "detail": gate["detail"],
        "live_trading_enable": gate["live_trading_enable"],
        "allow_real_execution": gate["allow_real_execution"],
    })

    tg = telegram_delivery_status()
    bot = tg.get("bot_configuration_detected") == "yes"
    chat = tg.get("chat_destination_configured") == "yes"
    items.append({
        "item": "telegram_alerts",
        "status": "OK" if (bot and chat) else "DEGRADED",
        "detail": (
            f"bot={tg.get('bot_configuration_detected')} "
            f"chat={tg.get('chat_destination_configured')} "
            "(alerts only; execution does not depend on this)"
        ),
    })

    mt5_probe: dict = {"initialize": False, "skipped": True}
    if probe_mt5:
        mt5_probe = _probe_mt5(symbol)
        mt5_probe.pop("skipped", None)
        items.extend(_mt5_items(mt5_probe))
    else:
        items.append({
            "item": "mt5_terminal",
            "status": "SKIPPED",
            "detail": "probe_mt5=False (offline check)",
        })

    blocking = [i["item"] for i in items if i["status"] == "FAILED"]
    degraded = [i["item"] for i in items if i["status"] == "DEGRADED"]
    skipped = [i["item"] for i in items if i["status"] == "SKIPPED"]
    # The double-gate item is informational (its OFF state is the safe
    # default); it must not drag the verdict to PARTIAL.
    unverified = [s for s in skipped if s != "real_execution_double_gate"]
    # Honest verdicts: FAILED -> NOT_READY; unknown-but-not-failing (skipped
    # probes) -> PARTIAL (never claim READY on unverified components).
    if blocking:
        verdict = "NOT_READY"
    elif unverified:
        verdict = "PARTIAL"
    else:
        verdict = "READY"
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "verdict": verdict,
        "real_execution_possible": gate["real_execution_possible"],
        "blocking_items": blocking,
        "degraded_items": degraded,
        "skipped_items": skipped,
        "items": items,
        "mt5_probe": mt5_probe,
    }


def format_readiness(report: dict) -> str:
    """Compact operator-facing summary (plain text, Telegram-safe)."""
    lines = [
        "Pre-flight live-readiness check",
        f"Symbol: {report['symbol']}",
        f"Verdict: {report['verdict']}",
        f"Real execution possible: {report['real_execution_possible']}",
        "",
    ]
    icon = {
        "OK": "[OK]",
        "FAILED": "[FAIL]",
        "DEGRADED": "[WARN]",
        "SKIPPED": "[SKIP]",
    }
    for item in report["items"]:
        lines.append(f"{icon.get(item['status'], '[?]')} {item['item']}: {item['detail']}")
    if report["blocking_items"]:
        lines.append("")
        lines.append(f"Blocking: {', '.join(report['blocking_items'])}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_readiness(check_live_readiness()))
