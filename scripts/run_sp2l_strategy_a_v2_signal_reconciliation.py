"""Deterministic research-only reconciliation of V2 vs source-aligned SP2L signals.

This tool does not optimize parameters and does not promote any geometry.
It runs both existing research detectors against the same MT5 M1 history and
classifies:
- COMMON: same direction and same three setup-candle timestamps
- V2_ONLY
- SOURCE_ALIGNED_ONLY

For COMMON cases it compares trigger/entry, SL, risk and TP. The artifact is
intended to explain signal-count divergence at rule level before any further
backtest interpretation.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5
import numpy as np

from mt5_terminal_resolver import find_mt5_terminal
from sp2l_author_replica_detector import detect as source_detect
from sp2l_strategy_a_v2_detector import detect_setup as v2_detect_setup
from sp2l_strategy_a_v2_detector import find_first_entry as v2_find_first_entry

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "backtest-mt5-local"

P_GAP_PRICE = 1.0
SPIKE_MULTIPLIER = 1.5
MAX_SL_DISTANCE = 10.0
TP_R = 1.0

SESSION_FILTER_ENABLED = True
LONDON_SESSION_OPEN = "08:00"
NEW_YORK_SESSION_CLOSE = "17:00"
LONDON_TZ = ZoneInfo("Europe/London")
NEW_YORK_TZ = ZoneInfo("America/New_York")


def resolve_symbol(requested: str) -> tuple[str, str]:
    symbols = list(mt5.symbols_get() or [])
    exact = {str(s.name): s for s in symbols}
    candidate = requested.upper()
    if candidate in exact:
        return candidate, "EXACT"
    for suffix in (".ecn", ".ECN", "m", ".m", "_ecn", "-ECN"):
        resolved = candidate + suffix
        if resolved in exact:
            return resolved, f"SUFFIX:{suffix}"
    normalized = "".join(ch for ch in candidate if ch.isalnum())
    matches = [
        name for name in exact
        if "".join(ch for ch in name.upper() if ch.isalnum()).startswith(normalized)
    ]
    if matches:
        return sorted(matches, key=lambda x: (len(x), x))[0], "DISCOVERED_PREFIX"
    raise RuntimeError(
        f"symbol discovery failed: requested={requested} available_count={len(symbols)}"
    )


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
            raise RuntimeError(
                f"history failed {cursor.isoformat()}..{chunk_end.isoformat()}: {mt5.last_error()}"
            )
        chunks.append(rates.copy())
        cursor = chunk_end + timedelta(minutes=1)
    rates = np.concatenate(chunks)
    rates.sort(order="time")
    _, idx = np.unique(rates["time"], return_index=True)
    return rates[np.sort(idx)]


def _parse_hhmm(value: str) -> tuple[int, int]:
    h, m = (int(x) for x in value.split(":", 1))
    return h, m


def _in_session(ts: int) -> bool:
    if not SESSION_FILTER_ENABLED:
        return True
    dt = datetime.fromtimestamp(int(ts), timezone.utc)
    lh, lm = _parse_hhmm(LONDON_SESSION_OPEN)
    nh, nm = _parse_hhmm(NEW_YORK_SESSION_CLOSE)
    london = dt.astimezone(LONDON_TZ).replace(
        hour=lh, minute=lm, second=0, microsecond=0
    )
    ny = dt.astimezone(NEW_YORK_TZ).replace(
        hour=nh, minute=nm, second=0, microsecond=0
    )
    return london.astimezone(timezone.utc) <= dt <= ny.astimezone(timezone.utc)


def filter_session(rates: np.ndarray) -> np.ndarray:
    if not SESSION_FILTER_ENABLED:
        return rates
    mask = np.array([_in_session(int(t)) for t in rates["time"]], dtype=bool)
    return rates[mask].copy()


def _bar(r) -> dict:
    return {
        "time": int(r["time"]),
        "open": float(r["open"]),
        "high": float(r["high"]),
        "low": float(r["low"]),
        "close": float(r["close"]),
    }


def contiguous_segments(rates: np.ndarray) -> list[np.ndarray]:
    if len(rates) == 0:
        return []
    cuts = [0]
    for i in range(1, len(rates)):
        if int(rates[i]["time"]) - int(rates[i - 1]["time"]) != 60:
            cuts.append(i)
    cuts.append(len(rates))
    return [rates[a:b] for a, b in zip(cuts, cuts[1:]) if b - a >= 3]


def collect_v2(rates: np.ndarray) -> list[dict]:
    records = []
    for segment in contiguous_segments(rates):
        bars = [_bar(x) for x in segment]
        for c_pos in range(2, len(bars) - 1):
            setup = v2_detect_setup(bars[c_pos - 2:c_pos + 1])
            if setup is None:
                continue
            entry = v2_find_first_entry(bars, c_pos, setup)
            if entry is None:
                continue
            # Preserve every setup for geometry reconciliation. Entry-key
            # deduplication belongs to execution/backtest lifecycle handling,
            # not to setup existence or geometry comparison.
            records.append({
            "direction": entry["direction"],
            "before_spike_time": int(entry["before_spike_time"]),
            "spike_time": int(entry["spike_time"]),
            "after_spike_time": int(entry["after_spike_time"]),
            "setup_time": int(entry["setup_time"]),
            "trigger_time": int(entry["entry_time"]),
            "entry_time": int(entry["entry_time"]),
            "entry": float(entry["entry"]),
            "sl": float(entry["sl"]),
            "risk": float(entry["risk"]),
            "tp": float(entry["tp"]),
            "source": "V2",
        })
    return sorted(records, key=lambda x: (x["trigger_time"], x["direction"]))


def collect_source(rates: np.ndarray) -> list[dict]:
    records = []
    for segment in contiguous_segments(rates):
        bars = [_bar(x) for x in segment]
        for i in range(4, len(bars) - 1):
            candidate = source_detect(
                bars[: i + 1],
                p_gap_price=P_GAP_PRICE,
                spike_multiplier=SPIKE_MULTIPLIER,
                max_sl_distance=MAX_SL_DISTANCE,
                tp_r=TP_R,
            )
            if candidate is None:
                continue
            records.append({
                "direction": candidate["direction"],
                "before_spike_time": int(bars[i - 4]["time"]),
                "spike_time": int(bars[i - 3]["time"]),
                "after_spike_time": int(bars[i - 2]["time"]),
                "setup_time": int(bars[i - 2]["time"]),
                "trigger_time": int(candidate["signal_time"]),
                "entry_time": int(candidate["signal_time"]),
                "entry": float(candidate["entry"]),
                "sl": float(candidate["sl"]),
                "risk": float(candidate["risk"]),
                "tp": float(candidate["tp"]),
                "source": "SOURCE_ALIGNED",
            })
    return records


def setup_key(record: dict) -> tuple:
    return (
        record["direction"],
        record["before_spike_time"],
        record["spike_time"],
        record["after_spike_time"],
    )


def compare(v2: list[dict], source: list[dict]) -> dict:
    v2_map = {setup_key(x): x for x in v2}
    source_map = {setup_key(x): x for x in source}
    common_keys = sorted(set(v2_map) & set(source_map))
    v2_only = sorted(set(v2_map) - set(source_map))
    source_only = sorted(set(source_map) - set(v2_map))

    common = []
    for key in common_keys:
        a = v2_map[key]
        b = source_map[key]
        common.append({
            "key": list(key),
            "v2": a,
            "source_aligned": b,
            "same_trigger_time": a["trigger_time"] == b["trigger_time"],
            "same_entry": abs(a["entry"] - b["entry"]) <= 1e-9,
            "same_sl": abs(a["sl"] - b["sl"]) <= 1e-9,
            "risk_delta": a["risk"] - b["risk"],
            "entry_delta": a["entry"] - b["entry"],
            "sl_delta": a["sl"] - b["sl"],
        })

    return {
        "counts": {
            "v2": len(v2),
            "source_aligned": len(source),
            "common_setup": len(common),
            "v2_only": len(v2_only),
            "source_aligned_only": len(source_only),
        },
        "common": common,
        "v2_only": [v2_map[k] for k in v2_only],
        "source_aligned_only": [source_map[k] for k in source_only],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--mt5-path", default=None)
    args = parser.parse_args()

    start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))

    initialized = mt5.initialize(path=args.mt5_path) if args.mt5_path else mt5.initialize()
    if not initialized:
        terminal = find_mt5_terminal()
        if terminal is None or not mt5.initialize(path=str(terminal)):
            print(json.dumps({
                "status": "MT5_INIT_FAILED",
                "error": mt5.last_error(),
            }, indent=2))
            return 2

    try:
        symbol, resolution = resolve_symbol(args.symbol)
        raw_rates = fetch_rates(symbol, start, end)
        rates = filter_session(raw_rates)

        v2 = collect_v2(rates)
        source = collect_source(rates)
        comparison = compare(v2, source)

        report = {
            "status": "COMPLETE",
            "mode": "RESEARCH_ONLY_SP2L_STRATEGY_A_SIGNAL_RECONCILIATION",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "symbol_requested": args.symbol,
            "symbol_used": symbol,
            "symbol_resolution": resolution,
            "period": {
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
            },
            "timeframe": "M1",
            "history": {
                "raw_bars": int(len(raw_rates)),
                "session_filtered_bars": int(len(rates)),
                "contiguous_segments": len(contiguous_segments(rates)),
            },
            "research_session_filter": {
                "enabled": SESSION_FILTER_ENABLED,
                "window": "London open -> New York close",
                "canonical": False,
            },
            "geometry": {
                "p_gap_price": P_GAP_PRICE,
                "spike_multiplier": SPIKE_MULTIPLIER,
                "max_sl_distance": MAX_SL_DISTANCE,
                "tp_r": TP_R,
                "canonical": False,
            },
            "comparison": comparison,
            "matching_definition": (
                "COMMON means same direction and identical before/spike/after "
                "setup timestamps; trigger/entry/SL/risk are compared separately."
            ),
            "semantic_limits": [
                "This artifact explains detector-level divergence only; it does not establish canonical Strategy A geometry.",
                "The P-Gap threshold 1.0 is a research comparator, not source-resolved canonical geometry.",
                "The session filter is retained to match the prior source-aligned replay context and is not canonical.",
                "No optimization, parameter selection, or production BUY/SELL decision is performed.",
            ],
        }

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = OUT_DIR / f"SP2L_STRATEGY_A_V2_SIGNAL_RECONCILIATION_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print(json.dumps({
            "status": report["status"],
            "report": str(path),
            "history": report["history"],
            "counts": comparison["counts"],
        }, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
