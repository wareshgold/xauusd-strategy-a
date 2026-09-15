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

The review focused on the source-sensitive windows already identified by transcript/source research. Frames were inspected at frame-level around slide transitions, annotations, candle constructions, entry/SL lifecycle, target diagrams, and the bearish example. Representative transition/state timestamps are recorded below so the evidence can be re-located deterministically.

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

## Key frame references

### C01 — P-Gap

- `35:53` — three numbered spike constructions; shaded P-Gap regions and `Valid BO = P-Gap` visible.
- `36:16` — three constructions shown simultaneously; each has a shaded P-Gap region.
- `36:30` — `Valid BO = P-Gap` and handwritten `AB=CD` visible.
- `36:45–37:20` — repeated AB=CD / P-Gap construction across the same source example and timeframe annotations.

**Source conclusion:** P-Gap is a source-defined validity concept associated with the breakout/spike construction. The visual material does not uniquely state the exact OHLC formula needed for deterministic implementation.

### C02 + C08 — Entry, correction and invalidation

- `38:40` — corrective sequence and lower reference levels are annotated.
- `39:40` — explicit `Buy Limit` and `SL` annotations.
- `39:50–40:10` — Buy Limit placement is emphasized relative to the horizontal reference and SL.
- `40:20–40:40` — explicit `Delete` annotation and subsequent pending-order lifecycle discussion.

**Source conclusion:** corrective entry, separate SL, and deletion/update behavior are directly visible. The exact candle/price anchor and deterministic refresh/invalidation threshold are not uniquely specified by the visual evidence.

### C03 — Leg 2 / AB=CD

- `36:30` — handwritten `AB=CD` above the construction.
- `36:35–37:20` — AB=CD repeated with `1M / 5M` annotations and the same candle-level construction.
- The source presentation is candle-level and does not provide a classical Fibonacci/online-AB=CD definition that can safely be substituted.

**Source conclusion:** the source supports the semantic expectation that the second leg corresponds to the first leg in the presented construction. It does not uniquely identify A/B/C/D anchors or a numerical tolerance.

### C04 — TP1 / TP2 / 2X

- `41:45–42:20` — `Buy`, `2X`, `SL`, and position/risk annotations appear sequentially.
- `42:30` — clean diagram explicitly labels `TP1`, `TP2`, `Entry`, and `SL`.
- `44:30` — handwritten point-distance examples (`250 point`, `500 point`) appear.

**Source conclusion:** the source clearly distinguishes TP1/TP2 and a 2X/second-position concept. The frames do not uniquely provide a general executable formula that can be safely encoded as canonical geometry.

### C05 — Bearish example

- `62:30–63:45` — bearish chart sequence with red highlighted region and declining structure.
- `64:00–64:40` — continued bearish movement and later setup/target markings.

**Source conclusion:** bearish continuation exists in the source. The video does not explicitly provide a complete bullish-to-bearish mirror mapping for every unresolved Strategy A field. No symmetry inference is allowed.

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
