"""Build a frozen SP2L V3.1 entry population from a preserved M1 CSV.GZ.

Offline/read-only research utility. It never imports or initializes MetaTrader5,
never sends orders, and never changes the input dataset. The V3.1 config is the
sole signal/entry definition; exit outcomes are left blank for later replay.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sp2l_v3_1_rr4_act40_config as cfg

M1_FIELDS = [
    "time", "time_utc", "open", "high", "low", "close",
    "tick_volume", "spread_points", "real_volume",
]
ENTRY_FIELDS = [
    "strategy", "variant", "direction", "setup_time_utc", "entry_time_utc",
    "entry_proxy", "sl_initial", "target", "risk_price", "exit_time_utc",
    "exit_price", "exit_reason", "status", "r_multiple",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_iso(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat().replace("+00:00", "Z")


def find_m1_gaps(bars):
    """Return every missing-minute interval; never infer or synthesize candles."""
    gaps = []
    for previous, current in zip(bars, bars[1:]):
        delta = int(current["time"]) - int(previous["time"])
        if delta > 60:
            gaps.append({
                "after_utc": utc_iso(int(previous["time"])),
                "before_utc": utc_iso(int(current["time"])),
                "missing_minutes": delta // 60 - 1,
            })
    return gaps


def split_contiguous_segments(bars):
    """Split on timestamp discontinuities so signal and entry logic cannot bridge gaps."""
    if not bars:
        return []
    segments = []
    start = 0
    for index in range(1, len(bars)):
        if int(bars[index]["time"]) - int(bars[index - 1]["time"]) != 60:
            segments.append(bars[start:index])
            start = index
    segments.append(bars[start:])
    return [segment for segment in segments if segment]


def load_m1_csv_gz(path: Path, expected_sha256: str):
    raw = path.read_bytes()
    observed = sha256(raw)
    if observed.lower() != expected_sha256.lower():
        raise ValueError(f"M1 CSV.GZ SHA-256 mismatch: expected={expected_sha256} observed={observed}")

    bars = []
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != M1_FIELDS:
            raise ValueError(f"M1 CSV header mismatch: expected exact schema {M1_FIELDS}; got {reader.fieldnames}")
        previous = None
        for row_no, row in enumerate(reader, start=2):
            ts = int(row["time"])
            parsed = datetime.fromisoformat(row["time_utc"].replace("Z", "+00:00"))
            if parsed.tzinfo is None or int(parsed.timestamp()) != ts or ts % 60:
                raise ValueError(f"invalid UTC/epoch/M1 timestamp at CSV row {row_no}")
            if previous is not None and ts <= previous:
                raise ValueError(f"duplicate or out-of-order M1 timestamp at CSV row {row_no}")
            previous = ts
            values = {k: float(row[k]) for k in ("open", "high", "low", "close")}
            if not all(math.isfinite(v) and v > 0 for v in values.values()):
                raise ValueError(f"invalid OHLC value at CSV row {row_no}")
            if values["high"] < max(values["open"], values["close"], values["low"]):
                raise ValueError(f"invalid high at CSV row {row_no}")
            if values["low"] > min(values["open"], values["close"], values["high"]):
                raise ValueError(f"invalid low at CSV row {row_no}")
            bars.append({
                "time": ts, **values,
                "tick_volume": int(row["tick_volume"]),
                "spread": int(row["spread_points"]),
                "real_volume": int(row["real_volume"]),
            })
    if len(bars) < 10:
        raise ValueError("insufficient M1 bars")
    return bars, observed, len(raw)


def build_population(bars, symbol: str):
    population = []
    seen = set()
    for segment in split_contiguous_segments(bars):
        if len(segment) < 4:
            continue
        for i in range(2, len(segment) - 1):
            setup = cfg.detect(segment[i - 2:i + 1], symbol)
            if not setup:
                continue
            # The entry search is deliberately confined to this uninterrupted segment.
            candidate = cfg.find_first_entry(segment, i, setup)
            if not candidate:
                continue
            key = (int(candidate["trigger_time"]), candidate["direction"])
            if key in seen:
                continue
            seen.add(key)
            entry_idx = next(
                (k for k in range(i + 1, len(segment))
                 if int(segment[k]["time"]) == int(candidate["trigger_time"])),
                None,
            )
            if entry_idx is None:
                continue
            population.append({
                "strategy": "SP2L",
                "variant": cfg.VERSION,
                "direction": candidate["direction"],
                "setup_time_utc": utc_iso(int(segment[i]["time"])),
                "entry_time_utc": utc_iso(int(candidate["trigger_time"])),
                "entry_proxy": f'{float(candidate["theoretical_entry"]):.10g}',
                "sl_initial": f'{float(candidate["sl"]):.10g}',
                # Exit targets belong to the replay variant, not the frozen entry population.
                "target": "",
                "risk_price": f'{float(candidate["risk"]):.10g}',
                "exit_time_utc": "",
                "exit_price": "",
                "exit_reason": "",
                "status": "",
                "r_multiple": "",
            })
    population.sort(key=lambda row: (
        row["entry_time_utc"], row["setup_time_utc"], row["direction"]
    ))
    return population


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m1-csv-gz", required=True)
    ap.add_argument("--m1-sha256", required=True)
    ap.add_argument("--symbol", default="XAUUSD.ecn")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    source = Path(args.m1_csv_gz).resolve()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    bars, source_sha, source_bytes = load_m1_csv_gz(source, args.m1_sha256)
    gaps = find_m1_gaps(bars)
    population = build_population(bars, args.symbol)
    if not population:
        raise RuntimeError("V3.1 configuration produced an empty entry population")

    csv_path = out / "SP2L_V3_1_FROZEN_ENTRY_POPULATION.csv"
    with csv_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=ENTRY_FIELDS)
        writer.writeheader()
        writer.writerows(population)
    population_sha = sha256(csv_path.read_bytes())

    config_path = Path(cfg.__file__).resolve()
    builder_path = Path(__file__).resolve()
    config_sha = sha256(config_path.read_bytes())
    builder_sha = sha256(builder_path.read_bytes())
    manifest = {
        "research_only": True,
        "canonical": False,
        "source": "PRESERVED_M1_CSV_GZ",
        "source_path": str(source),
        "source_sha256": source_sha,
        "source_byte_size": source_bytes,
        "source_rows": len(bars),
        "source_first_utc": utc_iso(int(bars[0]["time"])),
        "source_last_utc": utc_iso(int(bars[-1]["time"])),
        "source_gap_count": len(gaps),
        "source_gaps": gaps,
        "gap_policy": "SIGNAL_AND_ENTRY_SEARCH_SPLIT_AT_EACH_GAP; NO_CROSS_GAP_SETUPS_OR_ENTRIES; DOWNSTREAM_REPLAY_MUST_MARK_GAP_EXPOSED_OPEN_TRADES_AMBIGUOUS",
        "symbol": args.symbol,
        "timeframe": "M1",
        "entry_config_version": cfg.VERSION,
        "entry_config_file": "scripts/sp2l_v3_1_rr4_act40_config.py",
        "entry_config_sha256": config_sha,
        "entry_config_tp_r_metadata_only": cfg.TP_R,
        "builder_file": "scripts/build_sp2l_v3_1_frozen_population_from_m1.py",
        "builder_sha256": builder_sha,
        "population_rows": len(population),
        "population_sha256": population_sha,
        "population_policy": "ONE_FIXED_V3_1_ENTRY_POPULATION_SHARED_BY_ALL_EXIT_VARIANTS",
        "entry_fields_only": ["direction", "setup_time_utc", "entry_time_utc", "entry_proxy", "sl_initial", "risk_price"],
        "excluded_exit_fields": ["target", "exit_time_utc", "exit_price", "exit_reason", "status", "r_multiple"],
        "notes": [
            "Uses the declared V3.1 research config without claiming canonical Strategy A source resolution.",
            "No MT5 connection, order API, runner process, or dashboard is used.",
            "This artifact freezes entries only; all management variants must consume the exact CSV SHA.",
            "The RR4 TP_R value is config metadata only and no target price is written to the entry CSV.",
            "All source timestamp gaps are preserved in the manifest; signal and entry searches are segmented at each gap.",
            "Entry geometry and fill semantics remain research assumptions, not source-resolved facts.",
        ],
    }
    manifest_path = out / "SP2L_V3_1_FROZEN_ENTRY_POPULATION_MANIFEST.json"
    manifest_raw = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with manifest_path.open("xb") as stream:
        stream.write(manifest_raw)
    manifest_sha = sha256(manifest_raw)
    print(json.dumps({
        "status": "COMPLETE",
        "population_csv": str(csv_path),
        "population_rows": len(population),
        "population_sha256": population_sha,
        "manifest": str(manifest_path),
        "manifest_sha256": manifest_sha,
        "entry_config_sha256": config_sha,
        "builder_sha256": builder_sha,
        "source_sha256": source_sha,
        "source_rows": len(bars),
        "source_gap_count": len(gaps),
        "first_utc": manifest["source_first_utc"],
        "last_utc": manifest["source_last_utc"],
        "config": cfg.VERSION,
        "research_only": True,
        "mt5_accessed": False,
        "orders_possible": False,
    }, indent=2))


if __name__ == "__main__":
    main()
