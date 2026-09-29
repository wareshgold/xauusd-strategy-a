"""Research-only V2 signal-population parity harness.

Replays the recovered V2 historical interval with the same MT5 acquisition
family as the reference backtest (copy_rates_range), then emulates the current
forward runner's 10-bar rolling window + latest-candidate selection + session
gate. It does NOT place orders and does NOT emit production decisions.

The purpose is attribution, not optimization:
- reference V2 signal ledger
- signals visible inside the forward runner's 10-bar window
- first surfaced candidate under latest-candidate selection
- session-gated candidates
- reference signals never visible/surfaced by the 10-bar runner window
- level mismatches, if any

The forward runner currently uses copy_rates_from_pos(..., 10). This harness
uses copy_rates_range only to acquire the same historical data deterministically
and then emulates the rolling 10-bar view locally.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5
import numpy as np

P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0
ROLLING_BARS = 10

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = ROOT / "artifacts" / "backtest-mt5-local" / "SP2L_STRATEGY_A_V2_MT5_20260928T074842Z.json"
OUT_DIR = ROOT / "artifacts" / "forensic" / "2026-09-29"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LONDON_TZ = ZoneInfo("Europe/London")
NEW_YORK_TZ = ZoneInfo("America/New_York")


def resolve_symbol(requested: str) -> str:
    names = {str(s.name) for s in (mt5.symbols_get() or [])}
    candidate = requested.upper()
    for name in (candidate, f"{candidate}.ecn", f"{candidate}.ECN", f"{candidate}m", f"{candidate}.c.ecn"):
        if name in names:
            return name
    normalized = "".join(ch for ch in candidate if ch.isalnum())
    matches = [
        name for name in names
        if "".join(ch for ch in name.upper() if ch.isalnum()) == normalized
        or "".join(ch for ch in name.upper() if ch.isalnum()).startswith(normalized)
    ]
    if matches:
        return sorted(matches, key=lambda x: (len(x), x))[0]
    raise RuntimeError(f"symbol discovery failed: {requested}")


def fetch_rates(symbol: str, start: datetime, end: datetime) -> np.ndarray:
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"symbol_select failed: {symbol} {mt5.last_error()}")
    chunks = []
    cursor = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=7), end)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, cursor, chunk_end)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"history failed {cursor.isoformat()}..{chunk_end.isoformat()}: {mt5.last_error()}")
        chunks.append(rates.copy())
        cursor = chunk_end + timedelta(minutes=1)
    rates = np.concatenate(chunks)
    rates.sort(order="time")
    _, idx = np.unique(rates["time"], return_index=True)
    return rates[np.sort(idx)]


def body(c, direction):
    return abs(float(c["close"]) - float(c["open"]))


def detect_setup(candles):
    if len(candles) < 3:
        return None
    before, spike, after = candles[-3], candles[-2], candles[-1]
    ao, ah, al, ac = map(float, (before["open"], before["high"], before["low"], before["close"]))
    bo, bh, bl, bc = map(float, (spike["open"], spike["high"], spike["low"], spike["close"]))
    co, ch, cl, cc = map(float, (after["open"], after["high"], after["low"], after["close"]))
    spike_body = body(spike, "BUY")
    before_body = body(before, "BUY")
    after_body = body(after, "BUY")
    buy = (
        cc > bc and co > bo and bc > ac and bo > ao
        and cc > co and bc > bo and ac > ao
        and cl > ah + P_GAP_PRICE
        and spike_body > SPIKE_MULTIPLIER * before_body
        and spike_body > SPIKE_MULTIPLIER * after_body
    )
    sell = (
        cc < bc and co < bo and bc < ac and bo < ao
        and cc < co and bc < bo and ac < ao
        and ch < al - P_GAP_PRICE
        and spike_body > SPIKE_MULTIPLIER * before_body
        and spike_body > SPIKE_MULTIPLIER * after_body
    )
    if buy == sell:
        return None
    return {
        "direction": "BUY" if buy else "SELL",
        "setup_after_time": int(after["time"]),
    }


def first_entry(candles, start_index, setup):
    direction = setup["direction"]
    for j in range(start_index + 1, len(candles)):
        prev, cur = candles[j - 1], candles[j]
        if direction == "BUY":
            if float(cur["low"]) >= float(prev["low"]):
                continue
            entry = float(cur["low"])
            sl = float(candles[start_index - 2]["low"])
            risk = entry - sl
            if risk <= 0 or risk > MAX_SL_DISTANCE:
                return None
            return {
                "direction": "BUY", "trigger_time": int(cur["time"]),
                "theoretical_entry": entry, "sl": sl, "risk": risk,
                "tp": entry + TP_R * risk,
            }
        if float(cur["high"]) <= float(prev["high"]):
            continue
        entry = float(cur["high"])
        sl = float(candles[start_index - 2]["high"])
        risk = sl - entry
        if risk <= 0 or risk > MAX_SL_DISTANCE:
            return None
        return {
            "direction": "SELL", "trigger_time": int(cur["time"]),
            "theoretical_entry": entry, "sl": sl, "risk": risk,
            "tp": entry - TP_R * risk,
        }
    return None


def latest_candidate(window):
    candidates = []
    for setup_end in range(2, len(window) - 1):
        setup = detect_setup(window[setup_end - 2:setup_end + 1])
        if not setup:
            continue
        candidate = first_entry(window, setup_end, setup)
        if candidate is not None:
            candidates.append(candidate)
    return max(candidates, key=lambda x: (trigger_time(x), x["direction"])) if candidates else None


def session_allowed(ts):
    utc_dt = datetime.fromtimestamp(int(ts), timezone.utc)
    london = utc_dt.astimezone(LONDON_TZ)
    new_york = utc_dt.astimezone(NEW_YORK_TZ)
    start = london.replace(hour=8, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    end = new_york.replace(hour=17, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    return start <= utc_dt <= end


def trigger_time(s):
    """Normalize reference-ledger and forward-emulation trigger naming."""
    if "trigger_time" in s:
        return int(s["trigger_time"])
    return int(s["entry_time"])


def entry_price(s):
    if "theoretical_entry" in s:
        return float(s["theoretical_entry"])
    return float(s["entry"])


def key(s):
    return (trigger_time(s), str(s["direction"]))


def comparable(a, b):
    return (
        a["direction"] == b["direction"]
        and entry_price(a) == entry_price(b)
        and float(a["sl"]) == float(b["sl"])
        and float(a["risk"]) == float(b["risk"])
        and float(a["tp"]) == float(b["tp"])
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--start", default="2026-06-28T00:00:00Z")
    ap.add_argument("--end", default="2026-09-25T00:00:00Z")
    ap.add_argument("--mt5-path", default=None)
    args = ap.parse_args()

    reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
    reference_signals = list(reference.get("signal_ledger") or [])
    ref_by_key = {key(s): s for s in reference_signals}

    start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))
    initialized = mt5.initialize(path=args.mt5_path) if args.mt5_path else mt5.initialize()
    if not initialized:
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        symbol = resolve_symbol(args.symbol)
        rates = fetch_rates(symbol, start, end)
        rows = []
        first_seen = {}
        visible_keys = set()

        # The forward runner's 10-bar call is emulated at each observed M1 bar.
        # We record every candidate produced by the rolling window, then apply
        # the runner's latest-candidate + seen-trigger behavior.
        seen = set()
        surfaced = []
        gated = []
        for i in range(ROLLING_BARS - 1, len(rates)):
            window = rates[i - ROLLING_BARS + 1:i + 1]
            candidate = latest_candidate(window)
            if candidate is None:
                continue
            k = key(candidate)
            visible_keys.add(k)
            first_seen.setdefault(k, int(rates[i]["time"]))
            if k in seen:
                continue
            seen.add(k)
            allowed = session_allowed(candidate["trigger_time"])
            record = {
                **candidate,
                "observed_at": int(rates[i]["time"]),
                "session_allowed": allowed,
            }
            surfaced.append(record)
            if not allowed:
                gated.append(record)

        surfaced_by_key = {key(s): s for s in surfaced}
        reference_keys = set(ref_by_key)
        visible_reference = reference_keys & visible_keys
        surfaced_reference = reference_keys & set(surfaced_by_key)

        missed_visibility = reference_keys - visible_keys
        missed_surface = reference_keys - set(surfaced_by_key)
        surfaced_non_reference = set(surfaced_by_key) - reference_keys

        mismatches = []
        for k in sorted(reference_keys & set(surfaced_by_key)):
            if not comparable(ref_by_key[k], surfaced_by_key[k]):
                mismatches.append({
                    "key": list(k),
                    "reference": ref_by_key[k],
                    "forward_emulation": surfaced_by_key[k],
                })

        categories = {
            "reference_signals": len(reference_signals),
            "forward_visible_unique_candidates": len(visible_keys),
            "forward_surfaced_unique_candidates": len(surfaced),
            "forward_surfaced_reference_signals": len(surfaced_reference),
            "forward_surfaced_non_reference_signals": len(surfaced_non_reference),
            "reference_visible_in_10_bar_window": len(visible_reference),
            "reference_not_visible_in_10_bar_window": len(missed_visibility),
            "reference_visible_but_not_surfaced": len(missed_visibility ^ missed_surface) if False else len(visible_reference - surfaced_reference),
            "reference_surfaced_but_session_gated": sum(1 for k in surfaced_reference if not surfaced_by_key[k]["session_allowed"]),
            "reference_level_mismatches": len(mismatches),
        }

        # Attribution buckets are deliberately non-overlapping.
        not_visible = []
        visible_not_surfaced = []
        surfaced_gated = []
        surfaced_allowed = []
        for k in sorted(reference_keys):
            if k not in visible_keys:
                not_visible.append(k)
            elif k not in surfaced_by_key:
                visible_not_surfaced.append(k)
            elif not surfaced_by_key[k]["session_allowed"]:
                surfaced_gated.append(k)
            else:
                surfaced_allowed.append(k)

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_SP2L_V2_SIGNAL_POPULATION_PARITY",
            "canonical": False,
            "reference_artifact": str(Path(args.reference).as_posix()),
            "symbol_requested": args.symbol,
            "symbol_used": symbol,
            "period": {"start_utc": start.isoformat(), "end_utc": end.isoformat()},
            "rolling_window_bars": ROLLING_BARS,
            "forward_emulation": {
                "signal_key_normalization": "reference entry_time == forward trigger_time; reference entry == forward theoretical_entry",
                "acquisition": "copy_rates_range",
                "window": "last 10 M1 bars at each observed bar",
                "candidate_selection": "latest trigger time",
                "seen_behavior": "first unseen trigger key only",
                "session_filter": "London 08:00 through New York 17:00",
            },
            "reference": {
                "signals": len(reference_signals),
                "contract": reference.get("contract"),
                "history": reference.get("history"),
            },
            "history": {
                "bars": int(len(rates)),
                "first_bar_utc": datetime.fromtimestamp(int(rates[0]["time"]), timezone.utc).isoformat(),
                "last_bar_utc": datetime.fromtimestamp(int(rates[-1]["time"]), timezone.utc).isoformat(),
            },
            "counts": categories,
            "attribution": {
                "not_visible_in_10_bar_window": [list(k) for k in not_visible],
                "visible_but_not_surfaced_by_latest_candidate": [list(k) for k in visible_not_surfaced],
                "surfaced_but_session_gated": [list(k) for k in surfaced_gated],
                "surfaced_and_session_allowed": [list(k) for k in surfaced_allowed],
            },
            "level_mismatches": mismatches,
            "limits": [
                "Research-only reconciliation; no orders are placed.",
                "This emulates the forward runner's rolling window, not its live polling cadence.",
                "It does not prove broker fill/execution parity.",
                "It does not promote any geometry to canonical Strategy A.",
            ],
        }

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_V2_SIGNAL_POPULATION_PARITY_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"status": "COMPLETE", "report": str(path), "counts": categories}, indent=2))
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
