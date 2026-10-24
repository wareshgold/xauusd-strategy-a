# SP2L Fresh Holdout Freeze Audit — 2026-09-19

## Status

- Stage: PRE-HOLDOUT FREEZE AUDIT
- Branch: `research/sp2l-live-mt5-telegram-2026-09-19`
- Development / robustness sample: 2026-08-24 through 2026-09-18
- Fresh holdout boundary: **2026-09-19 00:00:00 UTC onward**
- Fresh holdout execution: NOT YET RUN
- Parameter tuning on holdout: PROHIBITED
- Production/live trading authorization: NOT GRANTED

## Boundary determination

The committed parameter-robustness runner explicitly evaluates these four weekly windows:

1. 2026-08-24 through 2026-08-28
2. 2026-08-31 through 2026-09-04
3. 2026-09-07 through 2026-09-11
4. 2026-09-14 through 2026-09-18

Therefore the first timestamp after the declared development/robustness sample is:

**2026-09-19 00:00:00 UTC**

No later data is included in the 81-combination robustness matrix.

## Frozen research configuration

The holdout must use the existing Author-Replica implementation without changing source interpretation.

### Baseline parameters

- P-Gap price: 1.0
- Spike multiplier: 1.5
- Max SL price: 10.0
- TP: 1.0R
- Symbol: XAUUSD.ecn
- Timeframe: M1

These values are frozen for validation only. The robustness matrix is not used to select a different production parameter set.

## Holdout isolation rules

The following are frozen before the first holdout result is inspected:

- No 3x3x3x3 parameter sweep.
- No optimization of P-Gap, spike multiplier, SL, or TP using holdout outcomes.
- No changing signal geometry because of holdout performance.
- No changing fill semantics because of holdout performance.
- No defining unresolved AB=CD anchors/tolerance from holdout results.
- No promoting Leg1=Leg2 equality to a canonical requirement.
- No changing source interpretation based on holdout performance.
- No discarding individual holdout trades because their outcome is inconvenient.
- No selecting a favorable holdout sub-period after seeing results.

## Data-integrity requirements

The holdout runner must record:

- requested start/end timestamps;
- actual MT5 returned first/last timestamps;
- number of bars returned;
- symbol and timeframe;
- acquisition errors, if any;
- session/calendar observations;
- signal count;
- wins, losses, ambiguous and unresolved outcomes;
- per-trade timestamps and outcome classification;
- the exact code revision used.

Historical MT5 timestamp/session semantics remain a separate validation concern and must not be silently assumed to be UTC.

## Important scope limitation

This audit establishes temporal separation from the **declared four-week robustness sample**. It does not prove that the broader MT5 history is complete, nor does it resolve the previously documented source/geometry uncertainties.

In particular, this audit does not make the following canonical:

- P-Gap formula beyond source-confirmed evidence;
- AB=CD anchors or tolerance;
- fill semantics;
- Leg1=Leg2 equality;
- execution/slippage assumptions.

## Gate disposition

**FREEZE AUDIT: READY FOR UNTOUCHED HOLDOUT**

**FRESH HOLDOUT: NOT YET RUN**

**PARAMETER STABILITY: EVIDENCE POSITIVE / GATE STILL PENDING**

**PRODUCTION: BLOCKED**

The next action is a single-configuration, no-tuning Fresh Holdout run beginning at 2026-09-19 00:00:00 UTC. If the available MT5 data for this boundary is incomplete or not yet sufficiently established, the run must report that condition rather than silently substitute another period.
