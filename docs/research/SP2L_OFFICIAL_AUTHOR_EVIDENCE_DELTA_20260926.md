# SP2L Official Author Evidence Delta — 2026-09-26

## Purpose
This checkpoint records new source evidence found on the official author SP2L page during the post-ceiling evidence hunt.

Source hierarchy is preserved: official author material outranks third-party indicators and research implementations. The new evidence may narrow unresolved fields, but it does not authorize inventing missing execution semantics.

## New official-source evidence

### F12 — trigger reference
The official author page states:
- In an uptrend, wait for the corrective candle to reach the low of the previous candle.
- In a downtrend, wait for the corrective candle to reach the high of the previous candle.

Source implication:
- The directional trigger reference is now SOURCE-CONFIRMED at the relation level: previous-candle Low for bullish and previous-candle High for bearish.

Still unresolved:
- whether reach means touch, penetration, cross, or close beyond;
- exact candle indexing when multiple structural candles are present;
- exact entry price anchor;
- pending-order fill semantics;
- interaction with signal-bar/key-bar confirmations;
- cancellation/expiry semantics.

Status: F12 REFERENCE RELATION SOURCE-CONFIRMED; EXECUTION SEMANTICS UNRESOLVED.

### F13 — 2X relation
The official author page states that, in addition to the initial entry, a secondary entry can be added at 50% of the distance from the entry point to the stop-loss.

Source implication:
- The 2X placement relation is SOURCE-CONFIRMED at the stated 50%-of-entry-to-SL relationship.

Still unresolved:
- exact order type and activation timing;
- whether the 50% level is always a pending order or another execution method;
- position sizing/risk allocation for the secondary entry;
- fill/cancel/replacement semantics;
- deterministic lifecycle in the bearish case.

Status: F13 PLACEMENT RELATION SOURCE-CONFIRMED; EXECUTION/SIZING LIFECYCLE UNRESOLVED.

### F10 — stop anchor
The official author page states that the SL is placed behind the candle from which the spike originated.

Source implication:
- The structural origin-candle relationship is SOURCE-CONFIRMED.

Still unresolved:
- exact OHLC boundary: wick extreme, body edge, open, close, or another level;
- buffer/spread treatment;
- whether the same boundary applies deterministically to every example.

Status: F10 ORIGIN-CANDLE RELATION SOURCE-CONFIRMED; EXACT PRICE BOUNDARY UNRESOLVED.

### F15 — bearish mirror
The same official page explicitly describes the bearish case: the corrective candle reaches the high of the previous candle, and the trade direction follows the downward spike.

Source implication:
- The basic bearish trigger relation is independently source-confirmed and does not need to be derived by mechanically reversing research code.

Still unresolved:
- bearish P-Gap candle mapping;
- exact bearish entry price anchor and fill semantics;
- exact bearish SL boundary;
- full bearish pending lifecycle;
- bearish 2X execution/sizing lifecycle.

Status: F15 BEARISH TRIGGER RELATION SOURCE-CONFIRMED; COMPLETE EXECUTABLE MIRROR UNRESOLVED.

## What this evidence does NOT establish
- No exact universal P-Gap OHLC formula is supplied.
- No exact AB=CD A/B/C/D OHLC anchors are supplied.
- No equality tolerance is supplied for Leg1 = Leg2.
- No touch/penetration/close rule is supplied for the trigger.
- No broker/spread/fill semantics are supplied.
- No deterministic pending replacement threshold or sizing equation is supplied.

## Canonical gate impact
- F10: narrower, but exact SL price remains unresolved.
- F12: previous-candle High/Low reference is now source-confirmed; trigger semantics remain unresolved.
- F13: 50% Entry-to-SL relation is source-confirmed; execution/sizing remains unresolved.
- F15: bearish previous-candle High relation is source-confirmed; complete mirror remains unresolved.
- P-Gap: unchanged — exact SP2L formula remains unresolved.
- F14 AB=CD: unchanged — anchors/tolerance remain unresolved.
- Frozen Geometry: BLOCKED.
- Untouched Validation: LOCKED.
- Fresh Holdout: LOCKED.
- Production: OFF.

## Source policy
These newly confirmed relations may be represented as source facts and fixture expectations. They must not be expanded into unverified OHLC or execution rules.

Third-party indicator descriptions found during the search were not used to promote canonical rules because they are not primary author evidence.

## Evidence references
- Official author SP2L page: https://poursamadi.com/sp2l-strategy/
- Official author English SP2L page: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

## Checkpoint identity
- Date: 2026-09-26
- Previous checkpoint: 6f14192b0f3402b508c7f306d74a82ed2a533b9c
- Result: OFFICIAL AUTHOR EVIDENCE DELTA
- Frozen Geometry: BLOCKED
- Production: OFF
