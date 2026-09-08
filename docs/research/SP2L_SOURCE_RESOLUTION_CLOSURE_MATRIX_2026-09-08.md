# SP2L Source Resolution Closure Matrix — 2026-09-08

## Purpose

Close the current source-resolution pass by mapping every Strategy A / SP2L semantic component to its strongest source evidence, executable status, unresolved geometry, and next permitted action.

This document is source-first. Historical profitability is not evidence for source meaning.

## Evidence hierarchy

1. Authoritative uploaded source video/transcript.
2. Source visual evidence / extracted frames.
3. Source ledger / semantic contract.
4. Secondary public implementations only as corroboration or contradiction evidence.
5. Backtest results only after geometry is frozen.

## Resolution matrix

| Component | Source-safe meaning | Executable geometry | Status | Next permitted action |
|---|---|---|---|---|
| Context / range | Spike follows a range/context; important levels are relevant context | Exact deterministic level detector not source-frozen | SEMANTIC | Keep contextual; do not optimize level thresholds yet |
| Breakout | Breakout is part of the Spike formation and is associated with follow-through | Exact breakout level/index convention not frozen | SEMANTIC | Preserve relational breakout meaning |
| Follow-through | Next directional continuation / key-bar behavior validates the breakout context | Exact candle-index predicate varies across source examples | SEMANTIC | Do not impose one fixed candle index |
| P-Gap | Valid breakout is associated with P-Gap; accepted examples show non-overlap/gap evidence | OHLC boundaries, candle identity, touch/equality, minimum size unresolved | BLOCKED | No generic FVG formula; source evidence only |
| Spike | Strong directional movement after range/context; source shows multiple constructions | Exact bar-count/power thresholds unresolved | SEMANTIC | Do not import third-party thresholds |
| Correction | After Spike, correction develops; bullish reaches prior/relevant Low; bearish reaches prior/relevant High | Exact candle identity and fixed/revised reference unresolved | SEMANTIC+ | Preserve prior/relevant Low/High semantics |
| Entry | Pending limit can be prepared during correction before fill | Exact candle, wick/body boundary, buffer, and fill/touch rule unresolved | BLOCKED | No market-reclaim substitute |
| Last-Spike breakout | Present in a secondary TradingFinder implementation | Not supported as a required prerequisite by primary source | REJECTED CANONICAL | Keep as secondary hypothesis only |
| Stop / invalidation | Behind the candle where Spike originated | Wick/body, strictness, buffer, exact origin candle unresolved | BLOCKED | Structural anchor only |
| Leg 1 | First leg of Spike/AB=CD structure | Exact OHLC anchors unresolved | BLOCKED | Do not use current heuristic as canonical |
| Leg 2 | Second leg expected to be approximately/equally sized to Leg 1 | Exact projection anchor/tolerance unresolved | BLOCKED | Preserve AB=CD semantic only |
| Target | Base strategy target is TP1 / 1:1; TP2 exists as larger management concept | Exact interaction with 2X/add-on management unresolved | SEMANTIC | Keep 1:1 as base semantic, not a substitute for unresolved fill geometry |
| Session filter | Higher-volume sessions may improve probability | No source-confirmed deterministic session filter | UNRESOLVED / NON-CANONICAL | Do not add session filter |

## Frozen semantic contract

`SPIKE -> P-GAP-valid breakout context -> CORRECTION -> relevant prior Low/High -> PENDING LIMIT -> structural invalidation behind Spike-origin -> SECOND LEG with AB=CD / approximately equal Leg-1 magnitude.`

## Explicitly unresolved executable fields

- P-Gap OHLC boundary.
- P-Gap candle timing/index.
- P-Gap touch/equality rule.
- P-Gap minimum size.
- Entry candle identity.
- Entry price formula.
- Entry wick/body convention.
- Entry buffer.
- Pending-level revision semantics while correction evolves.
- Fill/touch semantics.
- Spike-origin exact candle identity for every variant.
- SL wick/body convention.
- SL buffer.
- Leg-1 exact anchors.
- Leg-2 projection anchor.
- AB=CD tolerance.
- Exact target behavior for multi-position / 2X management.

## Canonical exclusions

The following must remain outside canonical Strategy A until independently source-confirmed:

- generic three-candle FVG as P-Gap;
- liquidity sweep terminology;
- BOS/MSS terminology;
- displacement thresholds;
- fixed spike-size thresholds;
- 65% body rules;
- mandatory last-Spike-candle breakout/reclaim;
- classical harmonic A/B/C/Fibonacci mapping;
- fixed 50% retracement as the base entry;
- session/time filters;
- any optimized threshold chosen from backtest performance.

## Gate decision

SOURCE RESOLUTION: **SEMANTIC CONTRACT COMPLETE / EXECUTABLE GEOMETRY INCOMPLETE**.

FROZEN GEOMETRY: **BLOCKED**.

DEV: **LOCKED**.

UNTOUCHED VALIDATION: **LOCKED**.

ROBUSTNESS / STABILITY: **LOCKED**.

FRESH HOLDOUT: **LOCKED**.

PRODUCTION: **UNCHANGED**.

## Promotion rule

No unresolved field may be promoted by inference from profitable backtests. A new primary-source visual or textual observation must first discriminate the relevant competing hypotheses. If source evidence cannot discriminate them, the ambiguity remains part of the research record and the executable geometry stays blocked.

## Next research action

The source-resolution pass is now consolidated. The next valid gate work is **not optimization**. It is either:

1. obtain a genuinely discriminating primary-source observation for one or more unresolved fields; or
2. if no such evidence remains available, formally freeze the semantic contract while keeping executable geometry blocked and do not enter DEV.

No production implementation change is authorized by this document.
