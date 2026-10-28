# V4 Phase 12 — Signal Identity Blocker Report

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Branch/HEAD:** `research/strategy-v4-xauusd-20261028` / `d3a7357f`  
**Status:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`  
**Date:** 2026-10-28  

## Finding
After reviewing source docs (strategy-a.md), design freeze, source rule register, batch resolutions (35/36/37/38/40), live forward events, trade CSV schema, and prior audits (Phase 4/6), there is **no authoritative source artifact that defines a stable, source-authenticated identity for each SP2L signal**.

## Evidence

### What exists (implementation/operational)
- **Live forward events** construct `signal_id` as `"<SYMBOL>:<trigger_time>:<DIRECTION>"` (e.g., `XAUUSD.ecn:1791452760:BUY`). `trigger_time` is the trigger/bar time in epoch seconds. (`research/manifests/original_history_snapshot_20261028_085035/forward_events.jsonl`, `research/source_audit/observed_disk/artifacts/forward-test/SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl`)
- **Live docs** describe duplicate-protection by `signal_id` but explicitly note: *"`signal_id` remains only an index key."* and *"Previous behavior allowed an exact `signal_id` match to select an event even when the event's embedded raw `candidate.trigger_time` disagreed with the historical candidate timestamp."* (`docs/research/SP2L_TEST_FAILURE_FIXES_20260926.md:19,25`)
- **Telegram/reporting docs** refer to `signal_id` as an operational identifier (e.g., `BT-...`, `SIG-...`), not as a canonical source identity. (`docs/research/SP2L_WEEKLY_BACKTEST_TELEGRAM_VALIDATION_2026-09-20.md:49`, `docs/LIVE_MT5_TELEGRAM_GATEWAY.md:52`)
- **Trade CSV** uses `signal_time` (epoch seconds) and `direction` as the comparison key; paired records use `comparison_type=PAIRED_COMMON_SIGNAL`. No source-provided immutable ID field exists in the CSV schema. (`research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_trades.csv` header)

### What does not exist (source-authenticated)
- **Strategy docs** (`docs/strategy-a.md`) define SP2L structure/concepts (spike, legs, P-Gap context, TP1 concept) but do not define a canonical "signal ID" field or numbering scheme.
- **Design freeze** fixes detector/entry/SL/TP/trailing/cost assumptions as research variants but does not define source-authenticated signal identity. (`research/design/V4_DESIGN_FREEZE.md`)
- **Source rule register** lists rules but has no rule defining signal identity; many rules remain `UNRESOLVED` or `CODE_OBSERVED`. (`research/source_audit/V4_SOURCE_RULE_REGISTER.csv`)
- **Batch resolutions** resolve formulas/concepts but do not establish a canonical signal numbering/ID from the original author source.
- **Prior audits** (Phase 4/6) concluded `SIGNAL_IDENTITY_NOT_ESTABLISHED` and showed match counts depend on key definition (`signal_timestamp+direction` vs stricter composites); no source-authenticated immutable key was found.

## Conclusion
`signal_timestamp + direction` (and `symbol + trigger_time + direction` in live ops) is a **deterministic implementation/operational key** derived from the detected trigger, not a **source-authenticated immutable signal identity**. The source material does not establish a separate canonical ID that would guarantee identity across implementations or survive definition changes. As a result, paired-signal matching is contingent on the chosen key definition and cannot be treated as proof of source-identical signals.

## Minimum evidence needed to resolve
To establish source-authenticated signal identity, one or more of the following is required from an authoritative source (original author notes/spreadsheet/trade log with canonical IDs):
1. **Explicit signal list** with a stable, immutable `signal_id` assigned by the original source for each signal occurrence in the analyzed periods, independent of implementation.
2. **Canonical definition** stating the identity key/numbering rule as defined by the source (not inferred from code), with examples.
3. **Cross-implementation mapping** showing the source-assigned IDs map to signals in both baseline and V4 implementations without ambiguity.
4. **Provenance** linking each analyzed trade/signal to its source-assigned ID with audit trail.

Without this, any identity-based comparison remains a key-dependent match, not a source-authenticated identity match.

## Recommendation
- Keep `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`. Do not promote key-based matches to proof of identity or edge.
- Continue to label all match/unmatch counts by key definition and object type (rows vs distinct keys). Keep paired rows separate from independent variant rows.
- If obtaining authoritative source IDs is not possible, document this limitation in all performance claims and treat paired comparisons as heuristic only.
