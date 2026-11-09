from __future__ import annotations

"""Fully offline Step-Lock research runner for one frozen V3 entry CSV and M1 CSV.

This script deliberately has no MetaTrader5 import or broker API. It never
rebuilds signals/entries, modifies source data, or overwrites evidence.
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from strategy_factory.v3_step_lock_engine import replay_step_lock_no_tp, validate_frozen_risk
from strategy_factory.v3_exit_engine import V3ExitEngineError

M1_FIELDS = [
    "time_epoch_seconds", "time_utc_iso", "open", "high", "low", "close",
    "tick_volume", "spread", "real_volume",
]
ENTRY_FIELDS = [
    "strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
    "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
    "exit_price", "exit_reason", "status", "r_multiple",
]
EXPECTED_ENTRY_SHA = "39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1"
EXPECTED_ENTRY_ROWS = 462
EXPECTED_M1_SHA = "B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"timestamp must include timezone: {value}")
    return parsed.astimezone(timezone.utc)


def load_bars(path: Path, expected_sha: str) -> tuple[list[dict], dict]:
    observed = digest(path)
    if observed.lower() != expected_sha.lower():
        raise ValueError(f"M1 SHA-256 mismatch: expected={expected_sha} observed={observed}")
    bars = []
    previous = None
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != M1_FIELDS:
            raise ValueError(f"M1 CSV header mismatch: {reader.fieldnames}")
        for line_no, row in enumerate(reader, 2):
            ts = int(row["time_epoch_seconds"])
            utc = parse_utc(row["time_utc_iso"])
            if int(utc.timestamp()) != ts or ts % 60:
                raise ValueError(f"M1 UTC/epoch/alignment mismatch at line {line_no}")
            if previous is not None and ts <= previous:
                raise ValueError(f"M1 duplicate/out-of-order timestamp at line {line_no}")
            values = {k: float(row[k]) for k in ("open", "high", "low", "close")}
            if not all(math.isfinite(v) and v > 0 for v in values.values()):
                raise ValueError(f"invalid OHLC at line {line_no}")
            if values["high"] < max(values.values()) or values["low"] > min(values.values()):
                raise ValueError(f"invalid OHLC range at line {line_no}")
            bars.append({
                "time": ts, **values,
                "tick_volume": int(row["tick_volume"]),
                "spread": int(row["spread"]),
                "real_volume": int(row["real_volume"]),
            })
            previous = ts
    if not bars:
        raise ValueError("M1 dataset is empty")
    gaps = []
    for left, right in zip(bars, bars[1:]):
        delta = int(right["time"]) - int(left["time"])
        if delta > 60:
            gaps.append({"from_utc": datetime.fromtimestamp(left["time"], timezone.utc).isoformat(),
                         "to_utc": datetime.fromtimestamp(right["time"], timezone.utc).isoformat(),
                         "missing_minute_slots": delta // 60 - 1})
    report = {
        "bars": len(bars),
        "first_utc": datetime.fromtimestamp(bars[0]["time"], timezone.utc).isoformat(),
        "last_utc": datetime.fromtimestamp(bars[-1]["time"], timezone.utc).isoformat(),
        "gap_count": len(gaps),
        "missing_minute_slots": sum(x["missing_minute_slots"] for x in gaps),
        "largest_gap_minutes": max((x["missing_minute_slots"] + 1 for x in gaps), default=0),
        "gaps": gaps,
        "sha256": observed,
        "byte_size": path.stat().st_size,
    }
    return bars, report


def load_population(path: Path, expected_sha: str, bars: list[dict]) -> tuple[list[dict], dict]:
    observed = digest(path)
    if observed.lower() != expected_sha.lower():
        raise ValueError(f"entry CSV SHA-256 mismatch: expected={expected_sha} observed={observed}")
    index_by_time = {int(bar["time"]): i for i, bar in enumerate(bars)}
    population = []
    seen = set()
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ENTRY_FIELDS:
            raise ValueError(f"entry CSV header mismatch: {reader.fieldnames}")
        for line_no, row in enumerate(reader, 2):
            if row["strategy"].strip().upper() != "SP2L":
                raise ValueError(f"unexpected strategy at entry line {line_no}")
            direction = row["direction"].strip().upper()
            if direction not in {"BUY", "SELL"}:
                raise ValueError(f"invalid direction at entry line {line_no}")
            entry_time = parse_utc(row["entry_time_utc"])
            trigger = int(entry_time.timestamp())
            if trigger not in index_by_time:
                raise ValueError(f"entry timestamp absent from M1 at line {line_no}")
            candidate = {
                "entry_idx": index_by_time[trigger],
                "theoretical_entry": float(row["entry_proxy"]),
                "sl": float(row["sl_initial"]),
                "risk": float(row["risk_price"]),
                "direction": direction,
                "trigger_time": trigger,
                "signal_time_utc": row["entry_time_utc"],
                "setup_time_utc": row["setup_time_utc"],
                "source_variant": row["variant"],
            }
            validate_frozen_risk(candidate)
            identity = (trigger, direction, candidate["theoretical_entry"], candidate["sl"])
            if identity in seen:
                raise ValueError(f"duplicate frozen trade identity at entry line {line_no}")
            seen.add(identity)
            population.append(candidate)
    if len(population) != EXPECTED_ENTRY_ROWS:
        raise ValueError(f"entry row count mismatch: expected={EXPECTED_ENTRY_ROWS}, observed={len(population)}")
    return population, {"rows": len(population), "sha256": observed,
                        "policy": "FROZEN_ENTRY_CSV_ONLY_NO_SIGNAL_REBUILD"}


def summarize(rows: list[dict]) -> dict:
    decisive = [x for x in rows if not x["ambiguous"] and x["realized_R"] is not None]
    wins = [x for x in decisive if x["realized_R"] > 0]
    losses = [x for x in decisive if x["realized_R"] < 0]
    gp = sum(x["realized_usd"] for x in wins)
    gl = abs(sum(x["realized_usd"] for x in losses))
    net = sum(x["realized_usd"] for x in decisive)
    return {
        "signals": len(rows), "decisive": len(decisive),
        "wins": len(wins), "losses": len(losses),
        "ambiguous": len(rows) - len(decisive),
        "gap_exposed": sum(x["reason"] == "M1_GAP_WHILE_OPEN" for x in rows),
        "net_R": sum(x["realized_R"] for x in decisive),
        "profit_factor": (sum(x["realized_R"] for x in wins) /
                          abs(sum(x["realized_R"] for x in losses))) if losses else None,
        "gross_profit_usd": gp, "gross_loss_usd": gl, "gross_usd": net,
        "usd_costs_modeled": False,
        "average_R_per_decisive": (sum(x["realized_R"] for x in decisive) / len(decisive)) if decisive else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m1-csv", required=True)
    parser.add_argument("--m1-sha256", default=EXPECTED_M1_SHA)
    parser.add_argument("--entry-csv", required=True)
    parser.add_argument("--entry-sha256", default=EXPECTED_ENTRY_SHA)
    parser.add_argument("--symbol", default="XAUUSD.ecn")
    parser.add_argument("--point", type=float, required=True)
    parser.add_argument("--contract-size", type=float, required=True)
    parser.add_argument("--volume", type=float, required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    if not all(math.isfinite(x) and x > 0 for x in (args.point, args.contract_size, args.volume)):
        raise ValueError("point, contract-size and volume must be finite positive explicit values")
    m1_path, entry_path, out = Path(args.m1_csv).resolve(), Path(args.entry_csv).resolve(), Path(args.output_dir).resolve()
    if args.m1_sha256.lower() != EXPECTED_M1_SHA.lower():
        raise ValueError("this frozen 30-day runner requires the audited M1 SHA-256")
    if args.entry_sha256.lower() != EXPECTED_ENTRY_SHA.lower():
        raise ValueError("this frozen 30-day runner requires the audited 462-row entry SHA-256")
    if out.exists():
        raise FileExistsError(f"output directory already exists; refusing overwrite: {out}")
    bars, m1_report = load_bars(m1_path, args.m1_sha256)
    population, population_report = load_population(entry_path, args.entry_sha256, bars)

    # The current audited 30-day source must remain exactly the known 29,919-bar snapshot.
    if m1_report["bars"] != 29919:
        raise ValueError(f"unexpected M1 row count: {m1_report['bars']}")
    if m1_report["gap_count"] != 21:
        raise ValueError(f"unexpected M1 gap count: {m1_report['gap_count']}")
    if m1_report["first_utc"] != "2026-09-24T07:57:00+00:00" or m1_report["last_utc"] != "2026-10-23T23:57:00+00:00":
        raise ValueError("M1 coverage does not match the frozen 30-day audit window")
    rows = [replay_step_lock_no_tp(c, bars, contract_size=args.contract_size, volume=args.volume)
            for c in population]
    summary = summarize(rows)

    out.mkdir(parents=True, exist_ok=False)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    stem = f"SP2L_STEP_LOCK_NO_TP_{stamp}"
    trades_path = out / f"{stem}_TRADES.csv"
    summary_path = out / f"{stem}_SUMMARY.json"
    manifest_path = out / f"{stem}_MANIFEST.json"

    trade_fields = list(rows[0].keys())
    with trades_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=trade_fields)
        writer.writeheader()
        writer.writerows(rows)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = {
        "research_only": True, "canonical": False, "backtest_executed": True,
        "mode": "STEP_LOCK_NO_TP", "milestone_unit": "INITIAL_R",
        "rule": "At +nR move stop to +(n-1)R; no final TP",
        "same_bar_policy": "ACTIVE_SL_AND_NEW_MILESTONE_SAME_BAR => AMBIGUOUS",
        "stop_update_policy": "COMPLETED_BAR_UPDATE_ACTIVE_FROM_NEXT_BAR",
        "entry_bar_policy": "EXCLUDED",
        "gap_policy": "OPEN_TRADE_CROSSED_M1_GAP => AMBIGUOUS_NO_FILL",
        "symbol": args.symbol, "timeframe": "M1",
        "execution_assumptions": {"point": args.point, "contract_size": args.contract_size,
                                  "volume": args.volume, "spread_commission_slippage": "NOT_MODELED"},
        "m1": m1_report, "frozen_population": population_report,
        "summary": summary,
        "artifacts": {},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for path in (trades_path, summary_path):
        manifest["artifacts"][path.name] = {"sha256": digest(path), "bytes": path.stat().st_size}
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sums_path = out / f"{stem}_SHA256SUMS.txt"
    with sums_path.open("x", encoding="utf-8", newline="") as stream:
        for path in (trades_path, summary_path, manifest_path):
            stream.write(f"{digest(path)}  {path.name}\n")
    print(json.dumps({"status": "COMPLETE", "mode": "STEP_LOCK_NO_TP",
                      "signals": len(population), "summary": summary,
                      "output_dir": str(out), "manifest": str(manifest_path),
                      "research_only": True, "mt5_accessed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
