from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_v3_exit_robustness.py"
SPEC = importlib.util.spec_from_file_location("audit_v3_exit_robustness", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _fixture(tmp_path: Path):
    trades = tmp_path / "trades.csv"
    rows = []
    variants = [
        "RR1_NO_TRAIL",
        "RR1_ACT3_D1",
        "RR1_ACT5_D1",
        "RR2_ACT3_D2",
    ]
    for vi, variant in enumerate(variants):
        for day, value in enumerate((0.5, -0.2, 0.3), start=1):
            rows.append({
                "variant": variant,
                "trigger_time": str(1_800_000_000 + day * 86400),
                "ambiguous": "false",
                "realized_R": str(value + vi * 0.01),
                "reason": "TP" if value > 0 else "SL",
            })
        # An unresolved row is not silently scored as a loss or a decisive trade.
        rows.append({
            "variant": variant,
            "trigger_time": str(1_800_000_000 + 4 * 86400),
            "ambiguous": "false",
            "realized_R": "",
            "reason": "OPEN_OR_UNRESOLVED",
        })
    with trades.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema": "SP2L_V3_DISCOVERY_EVIDENCE_MANIFEST_V1",
        "audit_status": "PASS",
        "research_only": True,
        "run": {"variants": len(variants), "frozen_entry_rows": 4},
        "artifacts": {
            "trades_csv": {
                "path": str(trades),
                "sha256": hashlib.sha256(trades.read_bytes()).hexdigest(),
                "rows": len(rows),
            }
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path, trades


def test_load_inputs_accepts_audited_manifest_and_preserves_unresolved(tmp_path):
    manifest_path, _ = _fixture(tmp_path)
    manifest, rows, _ = MODULE.load_inputs(manifest_path)
    assert manifest["audit_status"] == "PASS"
    assert len(rows) == 16
    assert sum(r["realized_R"] is None for r in rows) == 4
    result = MODULE.summarize([r for r in rows if r["variant"] == "RR1_NO_TRAIL"])
    assert result["decisive"] == 3
    assert result["unresolved"] == 1
    assert result["non_decisive"] == 1


def test_load_inputs_rejects_trade_hash_mismatch(tmp_path):
    manifest_path, trades = _fixture(tmp_path)
    trades.write_text(trades.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    try:
        MODULE.load_inputs(manifest_path)
    except MODULE.RobustnessError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("expected hash mismatch to fail closed")


def test_day_cluster_max_stat_bootstrap_is_deterministic():
    matrix = [
        [0.2, -0.1, 0.3, 0.0, 0.1],
        [0.1, -0.2, 0.2, 0.0, 0.1],
    ]
    first = MODULE.max_stat_bootstrap(matrix, iterations=250, seed=17)
    second = MODULE.max_stat_bootstrap(matrix, iterations=250, seed=17)
    assert first == second
    assert 0.0 < first["familywise_max_t_p_value"] <= 1.0


def test_day_cluster_bootstrap_requires_three_days():
    try:
        MODULE.max_stat_bootstrap([[1.0, -1.0]], iterations=200, seed=1)
    except MODULE.RobustnessError as exc:
        assert "three distinct" in str(exc)
    else:
        raise AssertionError("expected insufficient days to fail closed")


def test_daily_matrix_keeps_unresolved_and_ambiguous_days_missing():
    rows = [
        {"variant": "RR1_NO_TRAIL", "day": "2026-01-01", "ambiguous": False, "realized_R": 0.5},
        {"variant": "RR1_NO_TRAIL", "day": "2026-01-02", "ambiguous": False, "realized_R": None},
        {"variant": "RR1_NO_TRAIL", "day": "2026-01-03", "ambiguous": True, "realized_R": None},
        {"variant": "RR1_ACT3_D1", "day": "2026-01-01", "ambiguous": False, "realized_R": -0.2},
        {"variant": "RR1_ACT3_D1", "day": "2026-01-03", "ambiguous": False, "realized_R": 0.3},
    ]
    names, days, matrix, _ = MODULE.build_daily_matrix(rows)
    assert names == ["RR1_ACT3_D1", "RR1_NO_TRAIL"]
    assert days == ["2026-01-01", "2026-01-02", "2026-01-03"]
    assert matrix[1] == [0.5, None, None]
    # No signal for this variant/day is a true zero-return calendar day.
    assert matrix[0] == [-0.2, 0.0, 0.3]


def test_bootstrap_excludes_missing_days_without_zero_imputation():
    matrix = [
        [0.2, None, -0.1, 0.3, None, 0.1],
        [0.1, -0.2, None, 0.2, 0.0, 0.1],
    ]
    first = MODULE.max_stat_bootstrap(matrix, iterations=250, seed=19)
    second = MODULE.max_stat_bootstrap(matrix, iterations=250, seed=19)
    assert first == second
    assert first["eligible_variants"] == 2
    assert first["excluded_variants_fewer_than_three_known_days"] == 0
    assert first["minimum_valid_bootstrap_replicates_per_variant"] >= 125
    assert "missingness masks travel with sampled dates" in first["method"]


def test_bootstrap_preserves_irregular_calendar_missingness_deterministically():
    # Each None remains attached to its calendar date during block sampling;
    # the algorithm must not first compress each variant to a shorter series.
    matrix = [
        [0.4, None, None, -0.1, 0.2, None, 0.1, 0.3],
        [None, 0.2, -0.2, None, 0.1, 0.0, None, 0.2],
    ]
    first = MODULE.max_stat_bootstrap(matrix, iterations=500, seed=20261101)
    second = MODULE.max_stat_bootstrap(matrix, iterations=500, seed=20261101)
    assert first == second
    assert first["known_daily_returns_by_variant_min"] == 5
    assert first["known_daily_returns_by_variant_max"] == 5
    assert first["minimum_valid_bootstrap_replicates_per_variant"] >= 250
