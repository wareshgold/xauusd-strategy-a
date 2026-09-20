"""
SP2L Feature Observation Dataset Builder

Research-only adapter.

Purpose:
- Convert MT5 acquisition OHLC data into an observation dataset.
- Preserve data quality context.
- Prepare forward MFE/MAE analysis fields.

Restrictions:
- No signal generation.
- No BUY/SELL decisions.
- No P-Gap detector.
- No AB=CD rule implementation.
- No frozen geometry changes.
"""

from pathlib import Path
import csv

INPUT = Path("data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv")
OUTPUT = Path("data/research/sp2l-feature-validation/observations.csv")


def build_observation_dataset():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with INPUT.open("r", encoding="utf-8") as source, OUTPUT.open("w", newline="", encoding="utf-8") as target:
        reader = csv.DictReader(source)

        fields = [
            "timestamp",
            "symbol",
            "timeframe",
            "open",
            "high",
            "low",
            "close",
            "tick_volume",
            "spread",
            "data_quality_context",
            "market_context_observation",
            "pgap_observation_status",
            "two_leg_observation_status",
            "key_bar_observation_status",
            "stop_structure_observation_status",
            "forward_window",
            "mfe",
            "mae",
        ]

        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()

        for row in reader:
            writer.writerow({
                "timestamp": row["timestamp"],
                "symbol": "XAUUSD.ecn",
                "timeframe": "M1",
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "tick_volume": row["tick_volume"],
                "spread": row["spread"],
                "data_quality_context": "observed",
                "market_context_observation": "unknown",
                "pgap_observation_status": "unknown",
                "two_leg_observation_status": "unknown",
                "key_bar_observation_status": "unknown",
                "stop_structure_observation_status": "unknown",
                "forward_window": 60,
                "mfe": "",
                "mae": "",
            })


if __name__ == "__main__":
    build_observation_dataset()
    print(f"Created {OUTPUT}")
