# SP2L Source Forensics Ledger — F09–F14 — 2026-09-16

## Purpose

Record the next source-forensics pass against the six unresolved geometry fields identified in Batch 6. This ledger is evidence-traceable and does not promote any production geometry.

## Search scope

- Repository branch: `research/sp2l-batch6-trigger-abcd-2x-2026-09-16`
- Repository-wide code/file search for `transcript SP2L`, `Key-Bar`, and `AB=CD Leg 2` returned no indexed matches.
- `docs/research/` directory was inspected directly on the active branch. Existing source-evidence and forensic artifacts are present, but no raw transcript artifact was exposed by the inspected directory listing.
- Existing Batch 6 evidence was re-read before making any promotion decision.
- Public web search was attempted for source-specific terms around Poursamadi SP2L, 2X, trigger, Key-Bar, and Leg 2. The returned results did not provide a sufficiently reliable, source-primary worked example with executable numeric anchors.

## Evidence currently available

The existing Batch 6 source-evidence record states that the indexed SP2L training material explicitly identifies 2X and trigger-taking as source topics, while indexed text does not expose executable numeric definitions. It also records public descriptions of Spike + AB=CD and the AB/CD continuation concept without uniquely defining A/B/C/D OHLC anchors or tolerance.

Reference: `docs/research/SP2L_BATCH6_SOURCE_EVIDENCE_2026-09-16.md`.

## F09 — Entry anchor vs Leg-2 start

**Status: UNRESOLVED.**

Known source boundary: the source permits Limit placement during the initial structure/correction. That does not uniquely establish whether the executable entry price equals a Leg-2 structural origin, a retracement level, or another point.

Required promotion evidence: one worked source example where the entry price and the later Leg-2 origin can both be identified unambiguously.

## F10 — Stop-loss anchor / invalidation

**Status: UNRESOLVED.**

Known source boundary: invalidation is structurally related, but the exact wick/body/pivot anchor and any buffer semantics are not uniquely evidenced.

Required promotion evidence: an explicit source example tying invalidation/SL to a named structural price point and showing whether wick or body semantics are used.

## F11 — Pending Limit refresh

**Status: UNRESOLVED.**

Known source boundary: the source discusses deleting/replacing or refreshing the Limit when the distance to SL changes. The mandatory replacement condition and numeric threshold remain unknown.

Required promotion evidence: explicit wording or worked example showing when an existing Limit must be replaced, including the condition that triggers replacement.

## F12 — Trigger family / precedence

**Status: UNRESOLVED.**

Known source boundary: source material describes one-, two-, and three-candle structures and Bar/Key-Bar confirmation concepts. This does not uniquely define a deterministic classifier, precedence, or acceptance condition.

Required promotion evidence: a worked executed setup that identifies which candle structure qualified and why competing trigger forms did or did not qualify.

## F13 — 2X execution semantics

**Status: CONCEPT CONFIRMED / EXACT FORMULA UNRESOLVED.**

Known source boundary: the source index explicitly includes a dedicated 2X entry topic. Indexed text does not uniquely establish whether 2X is a price-distance multiple, structural anchor, retracement relation, or another rule, nor does it uniquely establish sizing/target/stop semantics.

Required promotion evidence: a worked 2X example with numeric entry, stop, target, and/or explicit relationship to the primary position.

## F14 — AB=CD anchors and tolerance

**Status: UNRESOLVED.**

Known source boundary: public descriptions connect Spike with AB and continuation with CD, but do not uniquely specify A/B/C/D OHLC anchors, wick/body semantics, or equality tolerance.

Required promotion evidence: a worked AB=CD source example with all four anchors and an explicit measurement convention. No tolerance will be inferred from performance.

## Gate decision

No F09–F14 field is promoted by this forensics pass. The absence of a source-primary worked example is itself recorded evidence against freezing geometry.

- Source Resolution: 🟡 Partial
- Synthetic Fixtures: 🟢 Advanced
- Frozen Geometry: 🔴 BLOCKED
- Untouched Validation: 🔒 LOCKED
- Robustness/Stability: 🔒 LOCKED
- Fresh Holdout: 🔒 LOCKED
- Production: 🔴 OFF

## Next evidence acquisition

1. Locate the original/source transcript or a source-primary recording with accessible transcript/captions.
2. Extract worked examples rather than relying on strategy summaries or backtest implementations.
3. For each F09–F14 item, require unique executable semantics before promotion.
4. If the source remains non-deterministic or inaccessible, preserve `UNRESOLVED` and do not substitute engineering convention.

## Non-negotiables

- No invented P-Gap formula.
- No invented AB=CD anchors or tolerance.
- No invented 2X formula.
- No invented fill semantics, stop buffer, or refresh threshold.
- No profitability-based geometry selection.
- No production BUY/SELL logic.
