"""Research-only signal parity forensic between recorded replay artifacts and current detector.

This tool does not define or promote canonical Strategy A geometry. It answers one
narrow question: with the same MT5 acquisition family (copy_rates_from), interval
filter, and recorded geometry, do the current detector's candidate signals match
the historical replay artifacts?

Run on the user's Windows MT5 terminal. The historical JSON artifacts must exist
under artifacts/backtest-multi.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mt5_terminal_resolver import find_mt5_terminal
from sp2l_author_replica_detector import detect


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "backtest-multi"


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_artifact(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_old_style(symbol: str, start: datetime, end: datetime):
    # Historical artifacts requested the exact minute-span count from
    # copy_rates_from, then filtered the returned epoch timestamps to [start,end).
    count = int((end - start).total_seconds() // 60) + 1
    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, start, count)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"copy_rates_from failed: {mt5.last_error()}")
    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())
    rates = rates[(rates["time"] >= start_ts) & (rates["time"] < end_ts)].copy()
    rates.sort(order="time")
    return rates, count


def current_detector_signals(rates, p_gap: float, spike: float, max_sl: float, tp_r: float):
    out = []
    last_signal_time = None
    for i in range(4, len(rates) - 1):
        candidate = detect(
            rates[: i + 1],
            p_gap_price=p_gap,
            spike_multiplier=spike,
            max_sl_distance=max_sl,
            tp_r=tp_r,
        )
        if candidate is None or candidate["signal_time"] == last_signal_time:
            continue
        last_signal_time = candidate["signal_time"]
        out.append({
            "index": i,
            "time": int(candidate["signal_time"]),
            "time_utc": datetime.fromtimestamp(int(candidate["signal_time"]), timezone.utc).isoformat(),
            "direction": candidate["direction"],
            "entry": float(candidate["entry"]),
            "sl": float(candidate["sl"]),
            "tp": float(candidate["tp"]),
        })
    return out


def compare(old_signals, new_signals):
    old_by_time = {int(x["time"]): x for x in old_signals}
    new_by_time = {int(x["time"]): x for x in new_signals}
    common = sorted(set(old_by_time) & set(new_by_time))
    missing = sorted(set(old_by_time) - set(new_by_time))
    extra = sorted(set(new_by_time) - set(old_by_time))

    geometry_mismatches = []
    for ts in common:
        a, b = old_by_time[ts], new_by_time[ts]
        fields = {}
        for field in ("direction", "entry", "sl", "tp"):
            if a.get(field) != b.get(field):
                fields[field] = {"old": a.get(field), "current": b.get(field)}
        if fields:
            geometry_mismatches.append({
                "time": ts,
                "time_utc": datetime.fromtimestamp(ts, timezone.utc).isoformat(),
                "differences": fields,
            })

    return {
        "old_signals": len(old_signals),
        "current_signals": len(new_signals),
        "same_signal_time": len(common),
        "missing_from_current": len(missing),
        "extra_in_current": len(extra),
        "geometry_mismatches_on_common_time": len(geometry_mismatches),
        "missing_examples": [
            old_by_time[x] for x in missing[:20]
        ],
        "extra_examples": [
            new_by_time[x] for x in extra[:20]
        ],
        "geometry_mismatch_examples": geometry_mismatches[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mt5-path", required=True)
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--p-gap", type=float, default=1.0)
    parser.add_argument("--spike", type=float, default=1.5)
    parser.add_argument("--max-sl", type=float, default=10.0)
    parser.add_argument("--tp-r", type=float, default=1.0)
    parser.add_argument("--months", default="07,08,09")
    args = parser.parse_args()

    terminal = Path(args.mt5_path)
    if not terminal.exists():
        raise SystemExit(f"MT5 terminal not found: {terminal}")
    if not mt5.initialize(path=str(terminal)):
        fallback = find_mt5_terminal()
        if fallback is None or not mt5.initialize(path=str(fallback)):
            raise SystemExit(f"MT5_INIT_FAILED: {mt5.last_error()}")

    try:
        rows = []
        for month in [x.strip() for x in args.months.split(",") if x.strip()]:
            if month == "07":
                start, end = datetime(2026, 7, 1, tzinfo=timezone.utc), datetime(2026, 8, 1, tzinfo=timezone.utc)
            elif month == "08":
                start, end = datetime(2026, 8, 1, tzinfo=timezone.utc), datetime(2026, 9, 1, tzinfo=timezone.utc)
            elif month == "09":
                start, end = datetime(2026, 9, 1, tzinfo=timezone.utc), datetime(2026, 9, 23, tzinfo=timezone.utc)
            else:
                raise SystemExit(f"Unsupported month fixture: {month}")

            path = ARTIFACTS / f"SP2L_replay_XAUUSD_ecn_month{month}.json"
            artifact = load_artifact(path)
            rates, raw_count = fetch_old_style(args.symbol, start, end)
            current = current_detector_signals(rates, args.p_gap, args.spike, args.max_sl, args.tp_r)
            old = artifact["signals"]

            result = compare(old, current)
            result.update({
                "month": month,
                "artifact": str(path.relative_to(ROOT)),
                "requested_interval_utc": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
                "copy_rates_from_count": raw_count,
                "filtered_bars": int(len(rates)),
                "artifact_filtered_bars": artifact.get("filtered_bars_in_interval"),
                "artifact_signal_count": artifact.get("signals_detected"),
                "geometry": {
                    "pGapPrice": args.p_gap,
                    "spikeMultiplier": args.spike,
                    "maxSlPrice": args.max_sl,
                    "tpR": args.tp_r,
                },
            })
            rows.append(result)
            print(
                f"[{month}] old={result['old_signals']} current={result['current_signals']} "
                f"same_time={result['same_signal_time']} missing={result['missing_from_current']} "
                f"extra={result['extra_in_current']} geometry_mismatch={result['geometry_mismatches_on_common_time']}",
                flush=True,
            )

        out = {
            "status": "COMPLETE",
            "research_only": True,
            "purpose": "recorded-replay-vs-current-detector-signal-parity",
            "source": "CONNECTED_MT5_TERMINAL.copy_rates_from",
            "timestamp_basis": "MT5 epoch rendered as UTC; historical mapping remains unresolved",
            "results": rows,
        }
        out_path = ROOT / "artifacts" / "forensic" / "2026-09-29" / "SP2L_SIGNAL_PARITY_COPY_RATES_FROM_20260929.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(json.dumps({"report": str(out_path), "status": "COMPLETE"}, indent=2))
        return 0
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
