# SP2L Source-Video Frame Audit — 2026-09-15

## Status

`SOURCE_EVIDENCE_AUDIT_COMPLETE — NO_CANONICAL_GEOMETRY_FROZEN`

This document records a targeted frame-level audit of the original SP2L source video supplied for the remaining unresolved geometry dimensions. It is a persistent research reference so future sessions can use the recorded evidence without repeatedly requesting the source video.

The audit is evidence-only. It does **not** adjudicate source meaning, freeze geometry, define execution semantics, or authorize BUY/SELL.

## Source identity

- Artifact: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Source video ID: `7HEC5mO3d3U`
- Duration: `4155.6667 s` (~69:15.7)
- Frame rate: `30 fps`
- Frame count: `124670`
- Resolution: `640x360`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
- Frame addressing rule: `round(t * 30)`

The SHA-256 matches the previously registered source fingerprint. Therefore this audit is tied to the same source artifact already used by the SP2L source-resolution work.

## Audit method

The review used deterministic frame extraction from the supplied binary at the registered 30 fps address rule, with finer inspection around the source-sensitive windows. The audit covered slide transitions, annotated candle constructions, P-Gap diagrams, correction/entry/SL lifecycle, delete behavior, target diagrams, point-distance examples, and the bearish chart sequence.

No generic trading convention was used to fill missing boundaries. Visual similarity was not promoted into a canonical formula. Where the video shows a concept but does not uniquely expose the executable OHLC rule, the dimension remains unresolved.

## Evidence index

| Candidate | Dimension(s) | Source-visible evidence | What remains unresolved | Current research state |
|---|---|---|---|---|
| C01 | `p_gap` | Multiple constructions explicitly label `Valid BO = P-Gap`; shaded P-Gap regions appear across three spike cases. | Exact OHLC boundary/anchor and executable P-Gap formula are not uniquely exposed. | `REMAINS_BLOCKED` pending human adjudication |
| C02 | `entry_anchor` | Corrective `Buy Limit` is explicitly shown; entry/reference horizontal level is visually separated from SL. | Exact source-defined candle/price anchor and placement rule are not uniquely specified. | `REMAINS_BLOCKED` pending human adjudication |
| C03 | `leg2_start` | Source presents Spike → correction → second-leg constructions and labels AB=CD. | Exact Leg-2 start candle/price anchor is not uniquely identified as an executable rule. | `REMAINS_BLOCKED` pending human adjudication |
| C04 | `targets_2x` | TP1, TP2, Entry, SL are explicitly shown; `2X` / second-position concept is shown in the entry sequence. | Exact reproducible formulas/anchors for TP1, TP2 and 2X are not fully specified. | `REMAINS_BLOCKED` pending human adjudication |
| C05 | `bearish_mirror` | Bearish continuation is visibly demonstrated in the later chart example. | Explicit source-stated mapping from bullish geometry to bearish geometry is not established; symmetry cannot be inferred. | `REMAINS_BLOCKED` pending human adjudication |
| C06 | `pending_refresh` | `Delete` is explicitly annotated in the corrective entry lifecycle; later frames show the pending setup being removed/changed. | Exact deterministic delete/replace/retain trigger and threshold are not stated. | `REMAINS_BLOCKED` pending human adjudication |
| C07 | `trigger_classifier` | Three numbered constructions are visibly presented; source treats multiple spike constructions as valid forms. | Exact exhaustive 1/2/3-candle classifier and boundary conditions are not fully specified. | `REMAINS_BLOCKED` pending human adjudication |
| C08 | `structural_invalidation` | Source explicitly discusses return to the cited lower level invalidating the scenario; visual invalidation examples are present. | Exact OHLC boundary and indexing semantics remain unresolved. | `REMAINS_BLOCKED` pending human adjudication |

## Detailed frame-level micro-audit

### C01 — P-Gap discriminator

**35:53–36:17**

- The source displays the SP2L slide with three numbered constructions.
- The blue/gray shaded regions are repeatedly associated with the text `Valid BO = P-Gap`.
- A red-X example is shown separately from the valid constructions.
- The repeated constructions establish that P-Gap is not merely a generic chart label added later; it is part of the source's own breakout-validity vocabulary.

**36:17–36:30**

- The three numbered examples remain visible while the source transitions into the AB=CD explanation.
- The shaded P-Gap regions remain visual reference areas.

**36:30–37:20**

- `Valid BO = P-Gap` remains visible in the construction.
- `AB=CD` is handwritten above the example.
- `1M / 5M` annotations appear, reinforcing that the explanation is tied to candle/example construction rather than a published universal formula.

**Adjudication boundary:** the video makes the semantic discriminator strong, but the exact top/bottom OHLC boundary of the shaded region and the exact candle-index formula are not uniquely stated. Therefore no executable P-Gap formula is promoted.

### C02 — Entry anchor

**38:40–39:30**

- The correction sequence is shown with a horizontal reference level.
- The narration/annotation moves from the spike/continuation construction into corrective entry placement.

**39:40–40:10**

- `Buy Limit` is explicitly written next to the horizontal entry/reference line.
- `SL` is explicitly marked below the setup.
- The entry level and SL are visually distinct; the source does not present them as the same price.
- The pending entry is shown during the corrective phase rather than as a market entry after an arbitrary later candle.

**Adjudication boundary:** the source clearly establishes corrective Buy Limit semantics and separate SL placement, but it does not expose a uniquely reproducible rule such as exact candle high/low/body/open/close selection. No such anchor is inferred.

### C03 — Leg-2 start / AB=CD

**36:30–37:20**

- The source explicitly writes `AB=CD` over the candle construction.
- The visual explanation remains at candle/example level.
- The second-leg construction is presented as the continuation after correction.

**Adjudication boundary:** the source supports a semantic magnitude relationship between the two legs, but the exact A/B/C/D price anchors and the precise point at which Leg 2 begins are not uniquely exposed. Classical Fibonacci or internet AB=CD conventions are not substituted.

### C04 — Targets / 2X

**41:45–42:20**

- `Buy`, `2X`, and `SL` are shown in sequence.
- The source visually distinguishes the normal entry from the secondary/2X position concept.

**42:30–42:40**

- The clean diagram labels `TP1`, `TP2`, `Entry`, and `SL`.
- This confirms that the source has distinct target levels rather than one undifferentiated take-profit.

**44:30–44:50**

- Point-distance examples are written, including `250 point` and `500 point` examples.
- These examples demonstrate that distance/point arithmetic is discussed, but they do not by themselves provide a universal executable TP formula with unambiguous units, anchors, and indexing.

**Adjudication boundary:** TP1/TP2/2X are source-confirmed concepts; the complete formulas remain unresolved.

### C05 — Bearish mirror

**62:35–64:35**

- A bearish chart sequence is visibly shown with declining price structure and highlighted regions.
- The later chart includes bearish continuation/target-style markings.
- The visual sequence is evidence that bearish setups exist in the source.

**Adjudication boundary:** the video does not state a complete field-by-field bullish-to-bearish transformation for every unresolved dimension. In particular, exact P-Gap, entry, invalidation, Leg-2, target, and pending semantics cannot be mirrored by assumption. Bearish existence is source-confirmed; deterministic mirror mapping is not.

### C06 — Pending refresh / delete behavior

**40:20–40:40**

- `Delete` is explicitly annotated in the entry lifecycle.
- The setup is subsequently redrawn/changed, demonstrating that the pending order state is not necessarily immutable after first placement.
- The later annotated state includes a new/changed level and continued discussion of the pending setup.

**Adjudication boundary:** source supports lifecycle change/delete behavior, but does not provide an exhaustive deterministic predicate for delete vs replace vs retain, nor a universal numeric threshold/buffer.

### C07 — Trigger classifier

**35:53–36:17**

- Three constructions are explicitly numbered `1`, `2`, and `3`.
- Each is presented as a valid spike construction within the SP2L explanation.

**36:17–36:30**

- The numbered constructions remain part of the same explanation as `Valid BO = P-Gap`.

**Adjudication boundary:** the source confirms a 1/2/3 construction family, but does not provide an exhaustive machine-testable classifier with all candle-index and boundary conditions. The family should not be converted into an arbitrary 1/2/3-candle algorithm.

### C08 — Correction / structural invalidation

**38:40–39:40**

- The source moves from the spike into correction and places the Buy Limit around a horizontal reference level.
- The correction is tied to a lower reference relative to the bullish construction.

**39:40–40:10**

- The entry and SL are explicitly separated.

**40:20–40:40**

- The `Delete` lifecycle indicates that the setup can be invalidated/removed as subsequent structure develops.

**Adjudication boundary:** the relationship between correction, the cited lower level, and invalidation is source-supported; the exact OHLC boundary and candle indexing are not uniquely stated.

## Key frame references

- `35:53` — three numbered spike constructions / P-Gap context.
- `36:16` — three constructions and shaded P-Gap regions.
- `36:30` — `Valid BO = P-Gap` and `AB=CD`.
- `37:00` — AB=CD construction with timeframe annotations.
- `38:40` — correction sequence.
- `39:40` — `Buy Limit` + `SL`.
- `40:20` — `Delete` lifecycle.
- `42:30` — `TP1` / `TP2` / `Entry` / `SL` diagram.
- `44:30` — point-distance examples.
- `62:35–64:35` — bearish continuation example.

## Important non-findings

The frame audit did **not** establish any of the following as canonical:

- a universal P-Gap OHLC formula;
- an exact Entry candle/price anchor;
- an exact Leg-2 start anchor;
- an exact invalidation OHLC boundary;
- a deterministic pending-order delete/replace/retain threshold;
- an exhaustive 1/2/3-candle trigger classifier;
- unique A/B/C/D anchors for AB=CD;
- an explicit numerical AB=CD tolerance;
- a universal TP1/TP2/2X formula;
- a formally stated bearish mirror mapping;
- any fill/execution rule, spread/buffer, or candle-indexing convention not explicitly present in source.

## Adjudication consequence

The visual audit materially strengthens the provenance of C01–C08 and narrows their hypotheses, but it does not by itself convert the remaining dimensions into executable canonical geometry.

Therefore the correct next gate remains:

`C01–C08 evidence → HUMAN MANUAL ADJUDICATION (#175) → FROZEN GEOMETRY READINESS (#179) → SEPARATE CANONICAL FREEZE DECISION (#180)`

A candidate may become `SOURCE_DISCRIMINATED` only through the defined human adjudication contract when the source itself provides a precise, reproducible discriminator and no invention is required.

## Reuse rule

Future sessions should treat this document, together with the registered source fingerprint and the existing C01–C08 candidate package, as the persistent source-evidence reference. The original video does not need to be re-requested for routine continuity. Re-opening the binary source is only necessary if a future human adjudication disputes a pixel-level detail that is not captured by the recorded evidence references.

## Governance

- No geometry was frozen by this audit.
- No backtest/optimization result was used to resolve source ambiguity.
- No generic TA convention was promoted.
- No inferred bullish/bearish symmetry was promoted.
- No execution/fill semantics were invented.
- No production BUY/SELL authorization was created.
