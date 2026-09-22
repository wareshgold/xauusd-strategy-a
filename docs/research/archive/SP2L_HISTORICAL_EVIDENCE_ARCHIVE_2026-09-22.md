# SP2L Historical Evidence Archive — 2026-09-22

This archive consolidates information worth retaining from old branch families before redundant refs are removed.

## Source-resolution evidence retained

### 2026-09-08 source-resolution checkpoint
Source video evidence confirmed:
- SP2L Strategy / Spike-2Leg.
- AB = CD is explicitly shown.
- Valid BO = P-Gap is explicitly shown.
- 1M / 5M notation is visible.

Still unresolved from the available raster evidence:
- exact A/B OHLC anchors;
- exact C anchor;
- executable P-Gap OHLC formula;
- exact deterministic Spike grammar;
- AB=CD tolerance.

Therefore the correct state remained: G4 BLOCKED, G5 BLOCKED, P-Gap formula BLOCKED, G6 RESOLVED, canonical geometry freeze BLOCKED.

Important negative evidence:
- pending-limit fill price is not established as C;
- generic three-candle imbalance is not established as the teacher's P-Gap;
- historical performance must not select among geometric interpretations.

Original branch family: research/sp2l-gate-preparation-v19 and related gate-preparation snapshots.

### Source-to-code synchronization conclusion

The historical source-aligned audit established that legacy deterministic modules were not a canonical implementation of the source semantics.

Retained distinctions:
- P-Gap semantic relationship is source-confirmed, but its executable formula was unresolved.
- Spike detector heuristics are research heuristics, not source grammar.
- Legacy correction-extreme reclaim is not a substitute for demonstrated pending-limit entry semantics.
- AB=CD may be preserved as a relationship only after A/B/C anchors are source-confirmed.
- Fill price must not be silently substituted for C.

Historical source-aligned implementation was deliberately guarded against promotion.

## MT5 execution-layer evidence retained

The 2026-09-15 MT5 execution work is retained as an execution-layer boundary, not Strategy A geometry.

Confirmed engineering boundaries:
- position modification request carries position identity, direction, current SL and proposed SL;
- invalid identity/non-finite prices are rejected;
- unknown broker stop/freeze constraints cause refusal;
- proposed SL must not loosen an existing SL;
- no native .mq5 EA was authorized;
- no trailing distance, activation threshold, step, tick/bar convention, broker numeric limits, or fill semantics were frozen;
- no production BUY/SELL generation was introduced.

Trailing-stop validation remained planned/off:
- unit tests for disabled/invalid configurations and favorable-direction SL movement;
- MT5 tester/runtime validation only after execution parameters are frozen;
- baseline must remain trailing OFF;
- treatment, if ever enabled, must be separately frozen and compared without optimizing from realized performance.

Historical branch family: checkpoint/session-snapshot-2026-09-15* plus research/mt5-trailing-stop-execution-2026-09-15.

The old implementation/test files are not required by the current forward-test runtime; their durable engineering constraints are preserved here.


## 2026-09-15 session snapshot — unique checkpoint

Commit `3682250ec551ac84fcac07ea7a658a9d5c7e8a2e` recorded a distinct 2026-09-15 session snapshot that is not represented by the other duplicate snapshot refs.

Durable items preserved:
- C01 P-Gap was classified SOURCE_DISCRIMINATED, while executable geometry remained governed rather than frozen.
- C02 SL was a working fixed test rule (50/60/70/80 pips; RR 1:2), explicitly non-canonical.
- C03 AB=CD / Leg-2 equality remained blocked at that checkpoint.
- C04 TP1/TP2/2X was source-discriminated.
- C05 M15/MA50 was a working fixed test rule, non-canonical.
- C06 pending-order behavior was source-discriminated.
- C07 trigger classifier and C08 correction/invalidation remained blocked.
- MT5 trailing stop was explicitly optional execution/position management, production OFF and absent from the no-trailing research baseline.
- No trailing distance, activation threshold, step, tick/bar convention, broker numeric constraint, fill semantics, or production BUY/SELL rule was frozen.
- PR #196 was an open draft at that checkpoint; its GitHub-reported head was `a49fa5134336c0c9bb78bf3693afe13494da95c5`, with an explicit synchronization/CI verification item preserved.

The unique checkpoint does not authorize canonical geometry or production execution.

## Cleanup decision rule

Historical raw code, duplicate reports, generated outputs, and temporary workflows are not copied merely because they differ by path. They are preserved only when they contain unique evidence, a gate decision, a reproducibility identifier, or an unresolved research conclusion still relevant to SP2L.

Duplicate branch names pointing to the same commit do not provide additional evidence.

## Canonical-status safeguard

Nothing in this archive:
- freezes P-Gap geometry;
- chooses A/B/C/D anchors;
- defines AB=CD tolerance;
- defines fill semantics;
- promotes research parameters;
- authorizes production execution.

The active forward-test branch remains the operational research anchor.


## 2026-09-09 source-resolution evidence

The 2026-09-09 entry/trigger/P-Gap research established durable source boundaries:
- pending-limit entry is source-confirmed; exact Entry price anchor and wick/body edge remain unresolved;
- structural invalidation is source-confirmed; exact anchor and deterministic replacement threshold remain unresolved;
- source examples include 1-, 2-, and 3-candle trigger constructions, but no universal trigger taxonomy/acceptance rule is frozen;
- 2X is source-confirmed terminology/concept, but its exact formula/reference levels remain unresolved;
- P-Gap is source-confirmed as a valid-breakout concept distinct from E-Gap/Common-Gap, but its executable formula and price/candle anchors remain unresolved;
- AB=CD is source-confirmed as the Leg-2 relationship, while A/B/C/D anchors and equality tolerance remain unresolved;
- Entry = Leg2Start is not authorized as a canonical assumption;
- market-close reclaim, fixed-distance stop, arbitrary ATR/pip/percentage replacement thresholds, generic BOS/MSS, generic FVG/three-candle imbalance, and unconfirmed bearish mirrors remain non-canonical.

These findings came from the 2026-09-09 source ledger and discrimination fixtures. They preserve evidence boundaries only and do not freeze Strategy A geometry.

## F11 pending-order refresh evidence — 2026-09-14

F11 established that the source demonstrates pending-order refresh/replacement behavior when subsequent structure materially changes the risk relationship, while the deterministic retain-versus-replace condition remains unresolved.

Preserved boundary:
- market-entry-on-close/reclaim is not a substitute for the source-confirmed pending-Limit model;
- no pip/tick/ATR/percentage/candle-count refresh threshold is source-confirmed;
- no rule requiring movement on every swing is frozen;
- no universal bearish mirror is assumed.

F11 remains SOURCE-DOES-NOT-DISCRIMINATE; it authorizes no engine change and leaves frozen geometry blocked.


## 2026-09-21 Batch 39–46 source-closure evidence

### Batch 39 — F14 AB=CD closure attempt
The primary-source review confirmed:
- AB=CD is explicitly part of the SP2L teaching vocabulary.
- The source supports the magnitude relationship `Leg2 ≈ Leg1`.
- The available primary frames do not uniquely label A/B/C/D endpoints, price fields, wick/body convention, or equality tolerance.
- Bearish worked examples contain Leg-1 references, but do not provide a deterministic A/B/C/D mapping.

Decision preserved:
**F14 remains PARTIAL / UNRESOLVED; Frozen Geometry remains BLOCKED.**
No canonical AB=CD detector, pivot selector, tolerance, or target rule was created.

### Batch 40 — P-Gap canonical-contamination audit
The repository's `PGAPResearch.ts` was audited and found to be explicitly a research three-candle imbalance candidate layer, not a canonical P-Gap detector.

The source audit instead describes P-Gap conceptually as a pressure-gap development:
`10–30 candles of trend pressure → pressure pause/compression → trend-bar → continuation expectation`.

The source does not provide an executable OHLC formula, candle indexing, deterministic threshold, or complete classifier.

Decision preserved:
**No canonical contamination identified. No code promotion. Frozen Geometry remains BLOCKED.**

### Batch 42 — P-Gap + SL synthetic fixture boundary
Research fixtures were specified for:
- a non-canonical pressure-window / pause / directional-trend-bar P-Gap candidate;
- spike shadow/wick plus spread as a reported SL interpretation.

These fixtures are engineering validation only. They do not freeze source geometry or authorize production signals.

Execution semantics intentionally left unresolved include bid/ask side, spread timing, broker stop constraints, tick rounding, slippage, and any additional safety buffer.

### Batch 43 — P-Gap forensic comparison
On the MT5 M1 research dataset, deterministic forensic partitioning produced:
- Candidate V1: 1,755
- existing three-candle imbalance: 7,402
- overlap: 290
- candidate-only: 1,465
- imbalance-only: 7,112

These counts prove reproducibility of the partition only; they do not identify Candidate V1 as the teacher's P-Gap.

Candidate parameters such as pause length 2, compression factor 0.75, and trend-body factor 1.5 remain implementation choices and non-canonical.

### Batch 44/45 — P-Gap source-to-code reconciliation and closure decision
Author implementation evidence narrows one executable candidate to a four-candle construction:
- `-4`: before-spike/origin-side candle
- `-3`: spike candle
- `-2`: post-spike candle
- `-1`: latest/trigger-side candle

Author-code candidate inequalities:
- BUY: `low[-2] > high[-4] + P_GAP_PRICE`
- SELL: `high[-2] < low[-4] - P_GAP_PRICE`

However, primary-source evidence does not directly bind these exact endpoints/indexing/mirror to the P-Gap label. Wick/body semantics, threshold, compression boundary, executable trend-bar definition, and formula binding remain unresolved.

Deterministic canonical status:
**P-Gap concept = SOURCE-CONFIRMED.**
**P-Gap executable formula = AUTHOR-IMPLEMENTATION-SUPPORTED / PRIMARY-SOURCE-UNRESOLVED.**
**Canonical P-Gap detector = NOT FROZEN.**

The generic gap convention must not be silently substituted for the author implementation candidate, and author parameters must not be promoted from code alone.

### Batch 46 — remaining source-blocker closure pass
The parallel closure pass retained these boundaries:
- F08 universal swing algorithm: unresolved.
- F10 exact structural OHLC stop anchor: unresolved; wick/body/base/latest-opposite-swing alternatives remain open.
- F11 pending refresh: qualitative behavior supported, exact delete/replace predicate and timeout unresolved.
- F12/C07 trigger: 1/2/3-candle family supported, exact taxonomy/indexing/activation unresolved.
- F13/C04 2X: concept confirmed, exact TP1/TP2/second-position numeric semantics unresolved.
- F14 AB=CD: magnitude relationship confirmed, anchors/tolerance unresolved.
- F15 bearish mirror: synthetic symmetry can be tested, but universal bearish source geometry remains unresolved.

Gate state after Batch 46:
**Source Resolution = PARTIAL**
**P-Gap executable geometry = UNRESOLVED**
**F08/F10/F11/F12/F13/F14/F15 = unresolved**
**Frozen Geometry = BLOCKED**
**Untouched Validation = LOCKED**
**Robustness/Stability = LOCKED**
**Fresh Holdout = BLOCKED**
**Production = BLOCKED / DISABLED**

No backtest-selected anchors, tolerance optimization, invented P-Gap formula, guessed fill semantics, or canonical promotion was authorized.


## 2026-09-16 Batch 5–8 gate evidence

### Batch 5 source-discrimination / engineering boundary
Batch 5 established a clean separation between repository engineering failures and Strategy A source geometry.

Preserved findings:
- isolated source-boundary assertions and synthetic fixture infrastructure passed in the recorded run;
- full regression was blocked/unverified when the build failed, so no PASS was claimed from skipped tests;
- engineering repairs were limited to imports, optional-field typing, restored execution-layer modules, legacy test interfaces, and workflow diagnostics;
- no P-Gap formula, swing selection, structural stop anchor, wick/body rule, pending-refresh threshold, trigger taxonomy, AB=CD tolerance, 2X formula, TP/TP2 formula, session semantics, or 125R treatment was changed;
- the Batch 5 source-discrimination audit found no new primary-source discriminator for F08, F10, F11, F15 or executable P-Gap geometry.

Gate remained:
**Source Resolution PARTIAL PASS; Synthetic Fixtures PASS as infrastructure; Frozen Geometry BLOCKED; validation/holdout locked; Production OFF.**

### Batch 5 gate reassessment
The source-discrimination search did not uniquely freeze executable geometry. Batch 6 remained the next source-discrimination track for F12 trigger taxonomy, F14 AB=CD anchors/tolerance, and F13 2X semantics.

### Batch 6–8 branch family
The historical Batch 6 trigger/ABCD/2X, Batch 7 validation-gate, and Batch 8 statistical-holdout refs did not add a newer retained gate state beyond the later source-resolution and forward-test records. They remain historical checkpoints only; no validation or holdout authorization was created by these refs.


## G413 source-geometry reconciliation — 2026-09-14

G413 narrowed the source questions without freezing executable geometry.

Durable source-aligned findings:
- P-Gap is source-distinguished from E-Gap/Common-Gap; generic three-candle range/body/wick separation was not promoted.
- A source-specific pressure-gap construction remained the retained semantic hypothesis, but exact candle pair, OHLC fields, magnitude/tolerance and non-overlap sufficiency remained unresolved.
- AB=CD / `Leg2 magnitude = Leg1` is source-confirmed.
- Arbitrary A/B/C/D candle selectors and fixed equality tolerance were not promoted.
- `fill = C` was explicitly not authorized.
- The worked example strengthened the research question toward source-defined structural swing origins, but did not establish a deterministic selector.
- Pending-limit execution is source-confirmed; market-close reclaim is not a substitute.
- Entry in the correction/first-low area was narrowed but not frozen; touch/overshoot and exact price-field semantics remained unresolved.
- Structural invalidation is source-supported, but wick/body, OHLC field, buffer and exact pre-fill cancellation boundary remained unresolved.
- TP1 / R=1 was source-confirmed as the primary target convention; TP2 as a larger alternative was source-confirmed; exact geometric mappings remained unresolved.
- Broker time, European opening and contextual MA/trend observations were not promoted to mandatory deterministic session filters.

G413 gate state:
**G413 PASS — SOURCE CANDIDATE RECONCILIATION**
**G400 BLOCKED**
**Frozen Geometry NOT AUTHORIZED**
**DEV NOT AUTHORIZED**
**Validation protected**
**Production BLOCKED**

Required next evidence was direct visual resolution of 34:14–35:50 P-Gap, 36:15–37:10 AB=CD anchors, 38:18–40:16 Buy Limit/update boundary, 41:18–42:48 stop/TP mapping, and 1:04:00–1:04:42 deep-leg/R mapping.

The later G416 visual-artifact gate already records that the required frame bundle was not available, so these G413 narrowing results do not constitute a canonical freeze.


## G349/G350 official-source audit family — 2026-09-12

Durable evidence preserved from the official-source bridge:
- Official Poursamadi web pages were identified as potentially authoritative extensions of the source package.
- SP2L sequence (spike → correction/second leg → entry) is consistent with the preserved lesson.
- P-Gap is presented as a validity condition for a valid spike, but the official page still does not define executable endpoints, OHLC fields, candle count, magnitude or overlap rule.
- The official page gives a directional second-leg trigger candidate, but the relationship between that trigger and the pending-limit placement remains unresolved.
- Stop-loss is tied to the spike-origin candle; wick/body/OHLC-field and offset remain unresolved.
- A 50% secondary/add-on entry is described, but its exact distance reference, sizing interaction and relation to the primary order remain unresolved.
- Default TP 1:1 is described on the official page, while the original lesson also discusses R1/R2, 2X/3X and AB=CD contexts; executable TP scope remains unresolved.
- AB=CD / Leg2≈Leg1 remains source-supported from the lesson.
- Higher-volume/New York session preference is contextual, not a deterministic session gate.

G349 gate:
**PASS — NEW OFFICIAL SOURCE MATERIAL IDENTIFIED; SOURCE BRIDGE OPEN, GEOMETRY STILL UNRESOLVED.**

**Frozen Geometry BLOCKED; DEV BLOCKED; Validation protected; Fresh Holdout locked; Production blocked.**

The G350 family is retained only as historical official-source audit lineage; no evidence from it authorizes canonical geometry or production.

## G368 hypothesis-layer family — 2026-09-12

The G368 family is a hypothesis/research layer, not canonical source resolution. Its durable role was to provide:
- an explicit hypothesis registry/schema and research boundary;
- synthetic/fixture-oriented investigation of unresolved SP2L geometry;
- a handoff into adversarial/minimal-pair discrimination work;
- separation between hypothesis execution and source-confirmed canonical rules.

G368 did not authorize promotion of hypotheses to canonical Strategy A geometry. Hypothesis results remain subordinate to source evidence and do not override unresolved P-Gap, A/B/C/D, entry, stop, TP, fill or execution semantics.

Therefore the historical G368 branch family can be removed after this archive preservation; deleting those branches does not promote or discard canonical evidence.
