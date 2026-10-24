import hashlib, json
from pathlib import Path

INPUT = Path("artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json")
OUTPUT = Path("artifacts/SP2L_candle_level_assumption_dependency_2026-09-14_2026-09-18.json")

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def body(c): return abs(c["close"]-c["open"])
def rng(c): return c["high"]-c["low"]

raw = INPUT.read_bytes()
p = json.loads(raw)
candles = {c["index"]: c for c in p["candles"]}

rows = []
for m in p["signal_mappings"]:
    idx = m["detection_context_indices"]
    A,S,C,T,G = (candles[idx[k]] for k in ("a_index","s_index","correction_index","trigger_index","signal_index"))
    direction = m["direction"]
    prev = T["low"] if direction == "BUY" else T["high"]
    corrective = C["low"] if direction == "BUY" else C["high"]
    trigger_relationship = corrective <= prev if direction == "BUY" else corrective >= prev
    entry = m["entry"]; sl = m["sl"]
    context = [A,S,C,T,G]
    sl_distance = abs(entry-sl)
    sl_to_levels = {
        "A_low": abs(sl-A["low"]), "A_high": abs(sl-A["high"]),
        "S_low": abs(sl-S["low"]), "S_high": abs(sl-S["high"]),
        "C_low": abs(sl-C["low"]), "C_high": abs(sl-C["high"]),
        "T_low": abs(sl-T["low"]), "T_high": abs(sl-T["high"]),
        "G_low": abs(sl-G["low"]), "G_high": abs(sl-G["high"]),
    }
    rows.append({
        "archived_signal_index": m["archived_signal_index"],
        "signal_time_utc": m["signal_time_utc"],
        "direction": direction,
        "outcome": m["archived_outcome"],
        "entry": entry, "sl": sl, "tp": m["tp"],
        "context_indices": idx,
        "body_points": {k: body(c) for k,c in zip(("A","S","C","T","G"),context)},
        "range_points": {k: rng(c) for k,c in zip(("A","S","C","T","G"),context)},
        "body_to_range": {k: (body(c)/rng(c) if rng(c) else None) for k,c in zip(("A","S","C","T","G"),context)},
        "observable_trigger_relationship": trigger_relationship,
        "trigger_relationship_definition": "C low <= T low for BUY; C high >= T high for SELL (descriptive measurement only)",
        "entry_sl_distance": sl_distance,
        "sl_to_context_levels": sl_to_levels,
        "pgap_status": "OBSERVABLE_CANDIDATE_MEASUREMENTS_ONLY",
        "swing_sl_status": "OBSERVABLE_DISTANCE_TO_CONTEXT_LEVELS_ONLY",
        "abcd_status": "NOT_ATTRIBUTABLE_FROM_ARTIFACT",
        "pending_lifecycle_status": "NOT_ATTRIBUTABLE_FROM_ARTIFACT",
        "tp_risk_status": "DIRECTLY_OBSERVABLE_NOT_CANONICAL",
    })

status_counts = {}
for r in rows:
    for k in ("pgap_status","swing_sl_status","abcd_status","pending_lifecycle_status","tp_risk_status"):
        status_counts.setdefault(k,{})
        status_counts[k][r[k]] = status_counts[k].get(r[k],0)+1

integrity = {
    "signal_count": len(rows),
    "mapping_summary": p["mapping_summary"],
    "gap_count": p["gap_count"],
    "candle_index_contiguous": all(c["index"] == i for i,c in enumerate(p["candles"])),
    "signal_timestamp_alignment": all(candles[m["signal_candle_index"]]["timestamp_utc_display"] == m["signal_time_utc"] for m in p["signal_mappings"]),
}

out = {
    "research_only": True,
    "artifact_type": "SP2L_CANDLE_LEVEL_ASSUMPTION_DEPENDENCY_ANALYSIS",
    "input_artifact": str(INPUT),
    "input_artifact_sha256": sha256_bytes(raw),
    "frozen_config": p["frozen_config"],
    "integrity": integrity,
    "status_counts": status_counts,
    "canonicalization_guard": "NO_UNRESOLVED_RULE_PROMOTED",
    "notes": [
        "All measurements are descriptive and derived only from archived OHLC/mapping fields.",
        "The trigger relationship is a direct measurement, not a canonical trigger predicate.",
        "No P-Gap formula, indexing, threshold, AB=CD anchors/tolerance, swing rule, fill semantics, or execution rule is inferred.",
        "AB=CD and pending-order lifecycle remain not attributable because required fields are absent.",
    ],
    "signal_rows": rows,
}
payload = json.dumps(out, ensure_ascii=False, indent=2, sort_keys=False).encode()
out["report_sha256"] = sha256_bytes(payload)
OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "status":"ANALYZED",
    "output":str(OUTPUT),
    "input_artifact_sha256":out["input_artifact_sha256"],
    "report_sha256":out["report_sha256"],
    "signals":len(rows),
    "gap_count":p["gap_count"],
    "mapping":p["mapping_summary"],
    "status_counts":status_counts,
}, ensure_ascii=False, indent=2))
