# SP2L Evidence Candidate Package — 2026-09-15

## Status

`READY_FOR_HUMAN_MANUAL_ADJUDICATION`

This package records source-grounded candidates for human review. It does not promote executable geometry, resolve ambiguity autonomously, or authorize execution.

## Governance boundary

- Source meaning outranks implementation convenience.
- No backtest or optimization result is used to adjudicate source meaning.
- No generic technical-analysis convention is used as authority.
- No inferred symmetry is used to fill missing source semantics.
- No undocumented buffer, threshold, formula, candle indexing, fill rule, or execution rule is introduced.
- `SOURCE_DISCRIMINATED` may only be recorded by a human adjudicator using the manual-adjudication contract.
- Until then, every candidate remains non-canonical and execution-disabled.

## Candidate C01 — P-Gap semantic discriminator

- Candidate ID: `C01-PGAP-003`
- Dimension: `p_gap`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `00:36:30`
- Frame: `65700`
- Transcript support: source transcript window around 36:00–37:00
- Source observation: the visual source labels the construction with `Valid BO = P-Gap` and also displays `AB=CD` in the same teaching sequence.
- Before hypothesis: P-Gap is source-defined semantically as a validity condition associated with the breakout, but its exact executable OHLC boundary remains unresolved.
- After hypothesis: the cited frame provides direct source evidence that the named P-Gap is explicitly associated with a valid breakout; exact executable boundary remains unresolved.
- Discriminator claim: source wording/annotation discriminates the semantic role of P-Gap from an arbitrary generic imbalance label, but does not by itself uniquely determine the executable boundary.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Does this source evidence uniquely determine the candle/price boundary required for execution, or only the semantic role?

## Candidate C02 — Corrective Buy Limit / SL visual separation

- Candidate ID: `C02-ENTRY-SL-003`
- Dimensions: `entry_anchor`, `structural_invalidation`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `00:39:40–00:40:20`
- Frames: `71400–72600`
- Transcript support: source transcript window around 38:38–40:20
- Source observation: the source shows a `Buy Limit`, a lower `SL` reference, a horizontal entry/reference level, and later a `Delete` annotation.
- Before hypothesis: corrective entry and invalidation are distinct source concepts, but the exact OHLC anchor and fill semantics are unresolved.
- After hypothesis: direct visual evidence supports the existence of a corrective pending-entry level distinct from the lower stop/invalidation reference; exact executable anchors remain unresolved.
- Discriminator claim: the source distinguishes the roles of entry and lower invalidation/stop references, but does not uniquely establish exact price-boundary semantics.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Does the source uniquely identify the entry candle/price and invalidation boundary, or only their distinct roles?

## Candidate C03 — AB=CD / Leg-2 magnitude semantics

- Candidate ID: `C03-ABCD-MAG-003`
- Dimensions: `abcd_anchors`, `abcd_tolerance`, `leg2_start`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `00:36:30–00:37:00`
- Frames: `65700–66600`
- Transcript support: source transcript window around 35:10–37:08
- Source observation: the teaching sequence visibly annotates `AB=CD`; transcript evidence states the second leg equals the first leg in magnitude at candle level.
- Before hypothesis: the source supports an AB=CD/Leg-2 equality concept, but A/B/C/D anchors, tolerance, and exact Leg-2 start are unresolved.
- After hypothesis: source evidence supports the magnitude-equality semantic claim while leaving executable anchors/tolerance/start unresolved.
- Discriminator claim: evidence narrows the interpretation toward candle-level leg-magnitude equality rather than requiring a classical Fibonacci/ABCD convention, but it does not uniquely define executable anchors or tolerance.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Which, if any, candle boundaries are explicitly identified by the source as A/B/C/D and what exact tolerance is source-supported?

## Candidate C04 — TP1 / TP2 / 2X semantic evidence

- Candidate ID: `C04-TARGETS-003`
- Dimensions: `targets_2x`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `00:42:30`
- Frame: `76500`
- Additional source window: `00:58:04–00:59:08`
- Transcript support: source transcript windows around 40:57–42:37 and 58:04–59:08
- Source observation: source examples explicitly show Entry/SL and TP1/TP2 concepts; bearish example also references 2X and a lower target.
- Before hypothesis: TP1/TP2/2X are source concepts, but exact formulas, anchors, and execution semantics remain unresolved.
- After hypothesis: source evidence confirms these are named target concepts used in examples, without uniquely determining their executable formulas.
- Discriminator claim: source evidence distinguishes named target concepts from invented labels, but does not uniquely determine formula/anchor semantics.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Does the source provide an exact reproducible target formula, or only target labels/visual relationships?

## Candidate C05 — Bearish continuation example

- Candidate ID: `C05-BEARISH-MIRROR-003`
- Dimension: `bearish_mirror`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `01:02:41–01:04:32`
- Source observation: the source presents bearish trigger/continuation examples with SL and target annotations.
- Before hypothesis: bearish examples exist, but a deterministic mirror of every bullish rule is unresolved.
- After hypothesis: source evidence confirms a bearish counterpart exists in the teaching material, while exact mirror mapping remains unresolved.
- Discriminator claim: evidence supports bearish ordering/continuation as a source phenomenon, but does not authorize inferred symmetry for unresolved bullish geometry.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Which bearish rules are explicitly source-defined, and which would require inferred symmetry from bullish rules?

## Candidate C06 — Pending-order deletion/update behavior

- Candidate ID: `C06-PENDING-REFRESH-003`
- Dimension: `pending_refresh`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `00:40:20`
- Frame: `72600`
- Additional transcript support: source transcript window around 38:38–39:48 and 56:44–57:45
- Source observation: a `Delete` annotation is shown after the pending-entry construction; later source discussion shows Buy Limit activation and continuation concepts.
- Before hypothesis: pending-order lifecycle may depend on subsequent structure, but deterministic delete/replace/retain thresholds are unresolved.
- After hypothesis: source evidence supports that pending-order state can change during the setup, while exact deterministic refresh conditions remain unresolved.
- Discriminator claim: the source demonstrates lifecycle behavior rather than a static one-shot order assumption, but does not uniquely specify a refresh algorithm.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Does the source state a reproducible condition for delete/replace/retain, or only demonstrate an example?

## Candidate C07 — Trigger family

- Candidate ID: `C07-TRIGGER-FAMILY-003`
- Dimension: `trigger_classifier`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `00:35:10–00:36:31`
- Transcript support: source transcript window around 33:10–36:31
- Source observation: the teaching material presents three spike cases / a 1-2-3 candle trend family and breakout plus follow-through.
- Before hypothesis: trigger is a 1/2/3-candle family, but the exact deterministic classifier remains unresolved.
- After hypothesis: source evidence confirms multiple candle-count constructions are part of the source family; exact classifier remains unresolved.
- Discriminator claim: source distinguishes a family of constructions from a single fixed three-candle convention, but does not uniquely specify executable classification rules.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Are the three cases explicitly exhaustive, and what exact candle conditions distinguish them?

## Candidate C08 — Correction / invalidation relationship

- Candidate ID: `C08-CORRECTION-INVALIDATION-003`
- Dimensions: `structural_invalidation`, `entry_anchor`
- Tier: `TIER_1`
- Artifact: `source-video-7HEC5mO3d3U`
- Timestamp: `00:38:38–00:39:48`
- Transcript support: source transcript window around 38:38–39:48
- Source observation: correction begins after the first leg; Buy Limit may be placed during the first three candles; return to the cited level invalidates the scenario.
- Before hypothesis: correction, entry placement, and invalidation are source concepts but exact candle/price boundaries are unresolved.
- After hypothesis: source evidence narrows the relationship among correction, pending entry, and invalidation, while exact executable boundaries remain unresolved.
- Discriminator claim: source supports a temporal/structural relationship without uniquely defining the OHLC implementation.
- Proposed disposition: `READY_FOR_MANUAL_ADJUDICATION`
- Human question: Which exact source-visible candle/price is the cited invalidation level, and is that same level the entry anchor?

## Adjudication rule

These candidates are intentionally **not adjudicated by this package**. The human reviewer must create a separate `ManualAdjudication` record for each candidate. A candidate may only become `SOURCE_DISCRIMINATED` if the cited source uniquely and reproducibly determines the executable dimension without invention. Otherwise it must remain blocked and preserve the remaining hypotheses.

## Current conclusion

The package increases traceability and narrows several hypotheses, but it does **not** freeze any of the ten Strategy A geometry dimensions and does not authorize execution.
