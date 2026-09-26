"""Compatibility gate for source-aligned SP2L research runs.

This gate prevents research runners from silently presenting an implementation
variant as the current manifest-compatible Author-Replica candidate.

It does NOT make unresolved geometry canonical.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "research" / "SP2L_RESEARCH_RULE_MANIFEST_20260926.md"

MANIFEST_CHECKPOINT = "3778152049ec374830769007ed91f84b301187bb"
DETECTOR_REVISION = "AR-20260926-01"

EXPECTED_CANDIDATE = {
    "p_gap_price": 1.0,
    "spike_multiplier": 1.5,
    "max_sl_distance": 10.0,
    "tp_r": 1.0,
}


def _same(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= 1e-12


def assert_manifest_compatible(
    *,
    p_gap_price: float,
    spike_multiplier: float,
    max_sl_distance: float,
    tp_r: float,
    detector_revision: str = DETECTOR_REVISION,
) -> dict:
    if not MANIFEST.is_file():
        raise RuntimeError(f"SP2L compatibility gate: manifest missing: {MANIFEST}")

    text = MANIFEST.read_text(encoding="utf-8")
    required = (
        "Frozen Geometry: BLOCKED",
        "P-Gap exact formula",
        "F10 exact SL boundary",
        "F13 order lifecycle",
        "F14 AB=CD anchors",
        "Fill semantics",
    )
    missing = [x for x in required if x not in text]
    if missing:
        raise RuntimeError(
            "SP2L compatibility gate: manifest content is incomplete; "
            f"missing markers={missing}"
        )
    if MANIFEST_CHECKPOINT not in text:
        raise RuntimeError(
            "SP2L compatibility gate: manifest source-evidence checkpoint "
            f"does not match expected {MANIFEST_CHECKPOINT}"
        )
    if detector_revision != DETECTOR_REVISION:
        raise RuntimeError(
            f"SP2L compatibility gate: detector revision {detector_revision!r} "
            f"!= expected {DETECTOR_REVISION!r}"
        )

    actual = {
        "p_gap_price": float(p_gap_price),
        "spike_multiplier": float(spike_multiplier),
        "max_sl_distance": float(max_sl_distance),
        "tp_r": float(tp_r),
    }
    mismatches = {
        key: {"expected": value, "actual": actual[key]}
        for key, value in EXPECTED_CANDIDATE.items()
        if not _same(actual[key], value)
    }
    if mismatches:
        raise RuntimeError(
            "SP2L compatibility gate: candidate parameters differ from the "
            f"manifest-compatible Author-Replica candidate: {mismatches}"
        )

    return {
        "status": "PASS",
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "manifest_source_checkpoint": MANIFEST_CHECKPOINT,
        "detector_revision": DETECTOR_REVISION,
        "candidate_parameters": actual,
        "canonical": False,
        "gate_scope": "research_compatibility_only",
        "unresolved_geometry_remains_blocked": True,
    }
