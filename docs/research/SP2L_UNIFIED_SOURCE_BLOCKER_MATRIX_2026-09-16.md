# SP2L Unified Source Blocker Matrix — 2026-09-19

## Purpose
Current source-resolution control surface for Strategy A. This matrix consolidates C01–C08 with F08–F16. It does not infer missing geometry and does not authorize trading.

## Matrix
| ID | Topic | Source boundary / confirmed observation | Exact canonical geometry still required | Status |
|---|---|---|---|---|
| C01 / P-Gap | P-Gap | Distinct from Common/E-Gap and associated with valid SP2L breakout | Current-SP2L candle indexing, bearish mirror, OHLC/wick-body, boundary/threshold semantics | UNRESOLVED |
| C02 / SL | Structural SL | SL associated with / behind spike-origin candle; separate from entry/risk budget | Exact bullish/bearish OHLC anchor, wick/body, buffer, invalidation event | UNRESOLVED |
| C03 / AB=CD | AB=CD | Second-leg magnitude expected equal/approximately equal to first | A/B/C/D endpoints, measurement convention, tolerance | UNRESOLVED |
| C04 / TP1-TP2-2X | Management levels | TP1/TP2/2X concepts source-described | Exact target anchors, 2X formula/sizing/lifecycle | UNRESOLVED |
| C05 / M15-MA50 | Context | MA50 context appears in working/source material | Canonical timeframe, MA definition, direction/filter semantics | UNRESOLVED |
| C06 / Pending | Pending Limit | Pending Limit and qualitative delete/re-place behavior demonstrated | Exact replacement predicate, replacement price, fill semantics | UNRESOLVED |
| C07 / Trigger | Trigger family | 1/2/3-candle plus Bar/Key-Bar variants source-described | Deterministic classifier and precedence | UNRESOLVED |
| C08 / Correction | Correction/invalidation | Correction is an entry phase; invalidation is distinct | Exact swing/OHLC and breach semantics | UNRESOLVED |
| F08 | Relevant swing | Local structural points are relevant; bullish correction references structural low | Universal swing/pivot selection, wick/body, precedence, dynamic update, mirror | PARTIAL / UNRESOLVED |
| F09 | Entry vs Leg-2 start | Source-discriminated separation | Exact universal anchors | SOURCE_DISCRIMINATED boundary only |
| F10 | Invalidation / SL | Spike-origin structural relationship and Entry-vs-SL separation source-confirmed | Exact price field, buffer, touch/penetration/close, execution semantics | PARTIAL / UNRESOLVED |
| F11 | Pending refresh | Pending order can persist, be deleted, and be replaced | Mandatory predicate, timeout, replacement construction, precedence, fill semantics | PARTIAL / UNRESOLVED |
| F12 | Trigger family | Multiple trigger constructions and variants source-described | Acceptance classifier and precedence | PARTIAL / UNRESOLVED |
| F13 | 2X | Optional second-position concept and half-target/R examples source-described | Reference anchor, price formula, sizing, activation, lifecycle/fill | PARTIAL / UNRESOLVED |
| F14 | AB=CD | Leg2 approximately equals Leg1 magnitude | A/B/C/D anchors, observed/projected D, measurement convention, tolerance | PARTIAL / UNRESOLVED |
| F15 | Bearish mirror | Synthetic symmetry can be tested only as a fixture | Primary-source bearish geometry | UNRESOLVED |
| F16 | Round Level | Round Level concept and 250/500/1000-point examples source-confirmed | Unit, rounding function, purpose, mandatory/optional status, interactions | PARTIAL / UNRESOLVED |

## Canonicalization rule
A field may enter Frozen Geometry only when its executable meaning is uniquely determined by primary-source evidence. SOURCE_DISCRIMINATED boundaries are not equivalent to SOURCE_CONFIRMED executable geometry.

## Explicit non-inferences
Do not promote without new source evidence:
- generic three-candle FVG formula as P-Gap;
- any legacy P-Gap candidate as canonical;
- SL = spike candle Low/High;
- fixed pip/point SL buffers;
- candle-count or time-based pending deletion;
- newest-candidate-wins refresh;
- fill = C;
- conventional harmonic A/B/C/D pivots;
- arbitrary AB=CD tolerance;
- exact 2X equation or sizing inferred from one example;
- Round Level = 250/500/1000 as a universal interval;
- broker-specific fill semantics.

## Current gate — 2026-09-19
| Gate | Status |
|---|---|
| Source Resolution | PARTIAL PASS |
| Frozen Geometry | BLOCKED |
| Historical Validation | LOCKED |
| Robustness / Parameter Stability | RESEARCH EVIDENCE ONLY |
| Fresh Holdout | WAITING — no eligible post-boundary bars |
| Production | BLOCKED |
| Live Trading | DISABLED |

## Research priority
1. P-Gap exact current-SP2L indexing + bearish mirror + boundary semantics.
2. F10 exact invalidation/SL boundary.
3. F12 trigger acceptance / precedence.
4. F11 pending-order delete/refresh predicate.
5. F14 A/B/C/D endpoint and equality measurement.
6. F13 2X complete lifecycle/formula.
7. F08 universal swing selection.
8. F15 source-confirmed bearish geometry.
9. F16 Round Level executable role/algorithm.

These are evidence-acquisition priorities, not performance-based optimization targets.

## Gate guard
The research harness must fail closed for canonical promotion unless every required executable geometry field is SOURCE_CONFIRMED. Synthetic fixtures may test discrimination and guard behavior but may not decide the canonical rule.

## Conclusion
The repository has one current blocker matrix rather than parallel action matrices. Frozen Geometry remains BLOCKED because executable geometry is not yet fully source-confirmed.

No backtest, robustness result, parameter search, or implementation convenience may resolve these source blockers.
