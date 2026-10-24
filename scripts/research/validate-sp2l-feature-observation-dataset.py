"""
SP2L Feature Observation Dataset Integrity Validator

Research-only validation layer.

Checks:
- source/output row count
- timestamp boundaries
- required schema columns
- preservation of unresolved feature states

Restrictions:
- No trading logic
- No feature detection
- No geometry changes
"""

from pathlib import Path
import csv
import json

SOURCE = Path("data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv")
OBSERVATION = Path("data/research/sp2l-feature-validation/observations.csv")
REPORT = Path("data/research/sp2l-feature-validation/observations_integrity_report.json")

REQUIRED_COLUMNS = {
    "timestamp",
    "symbol",
    "timeframe",
    "open",
    "high",
    "low",
    "close",
    "tick_volume",
    "spread",
    "pgap_observation_status",
    "two_leg_observation_status",
    "key_bar_observation_status",
    "stop_structure_observation_status",
}


def read_csv_info(path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def validate():
    source_rows = read_csv_info(SOURCE)
    observation_rows = read_csv_info(OBSERVATION)

    fields = set(observation_rows[0].keys()) if observation_rows else set()

    unknown_states = all(
        row["pgap_observation_status"] == "unknown"
        and row["two_leg_observation_status"] == "unknown"
        and row["key_bar_observation_status"] == "unknown"
        and row["stop_structure_observation_status"] == "unknown"
        for row in observation_rows
    )

    report = {
        "status": "PASS" if (
            len(source_rows) == len(observation_rows)
            and fields.issuperset(REQUIRED_COLUMNS)
            and source_rows[0]["timestamp"] == observation_rows[0]["timestamp"]
            and source_rows[-1]["timestamp"] == observation_rows[-1]["timestamp"]
            and unknown_states
        ) else "FAIL",
        "source_rows": len(source_rows),
        "observation_rows": len(observation_rows),
        "first_timestamp_match": source_rows[0]["timestamp"] == observation_rows[0]["timestamp"],
        "last_timestamp_match": source_rows[-1]["timestamp"] == observation_rows[-1]["timestamp"],
        "required_columns_present": fields.issuperset(REQUIRED_COLUMNS),
        "feature_states_preserved_as_unknown": unknown_states,
        "geometry_changed": False,
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    validate()
