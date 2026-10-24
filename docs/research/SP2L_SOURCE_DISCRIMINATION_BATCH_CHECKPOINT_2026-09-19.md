# SP2L Source Discrimination Batch — 2026-09-19

## Batch purpose

Re-audit the current branch after commit `9bd3047` and determine whether the newly added F10/F11/F12/F14 discrimination pack produced any source evidence strong enough to close an executable geometry blocker.

This batch is evidence/audit work only. It does not define geometry, select an interpretation by performance, or authorize execution.

## Five completed checks

### 1. F10 — Invalidation / SL

Reviewed the current F10 audit and its cited primary-source chain.

Confirmed:
- SL is structurally associated with the spike-origin candle.
- Entry and SL are distinct concepts.
- Return toward/through the relevant structure is related to invalidation.

Still unresolved:
- exact OHLC field;
- wick vs body;
- touch/penetration/close;
- numeric buffer/offset;
- broker Bid/Ask and execution semantics.

**Disposition: PARTIAL / UNRESOLVED.**

### 2. F11 — Pending-order lifecycle

Reviewed the current F11 audit and cited source sequence.

Confirmed:
- Buy Limit can exist before activation.
- Existing order can be deleted.
- A replacement/new order can follow.

Still unresolved:
- mandatory deletion predicate;
- numeric candle/time expiry;
- replacement condition and price construction;
- candidate precedence;
- fill semantics.

**Disposition: PARTIAL / UNRESOLVED.**

### 3. F12 — Trigger acceptance / precedence

Reviewed the current F12 audit.

Confirmed:
- Second-Leg trigger concept is source-described.
- Bullish case references previous-candle low; bearish case references previous-candle high.
- 1/2/3-candle structures and Bar/Key-Bar variants are source-described.

Still unresolved:
- universal candle indexing;
- touch/wick/close activation;
- precedence between variants;
- universal Limit-vs-later-confirmation classifier;
- broker fill semantics.

**Disposition: PARTIAL / UNRESOLVED.**

### 4. F14 — AB=CD anchors

Reviewed the current F14 audit.

Confirmed:
- AB=CD is explicitly part of SP2L.
- Leg2 is expected to be approximately/effectively equal in magnitude to Leg1.

Still unresolved:
- exact A/B/C/D endpoints;
- observed vs projected D;
- wick/body/OHLC convention;
- structural-point selection;
- measurement convention;
- equality tolerance.

**Disposition: PARTIAL / UNRESOLVED.**

### 5. Controlling Frozen-Geometry gate

Reconciled F10/F11/F12/F14 against the controlling Frozen Geometry audit.

Result:
- SOURCE_CONFIRMED executable fields remain **0 / 7**.
- Frozen Geometry remains **BLOCKED**.
- No canonical P-Gap formula is introduced.
- No AB=CD formula or tolerance is introduced.
- No fill semantics are introduced.
- Fresh Holdout boundary is not reinterpreted.
- Live trading remains disabled.

## New-evidence determination

The current F10/F11/F12/F14 pack is a discrimination and audit harness. It does not itself constitute new primary-source evidence. The current branch therefore contains **no newly verified source artifact that uniquely closes F10, F11, F12, or F14**.

The correct action is to preserve the blockers rather than convert research candidates into canonical rules.

## Downstream gate

- Source Resolution: **PARTIAL**
- Frozen Geometry: **BLOCKED**
- Historical Validation: **LOCKED**
- Robustness/Stability: **RESEARCH EVIDENCE ONLY**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Production: **BLOCKED**
- Live Trading: **DISABLED**

## Next actionable source requirement

A blocker can move toward closure only when a genuinely discriminating primary-source artifact appears, such as:
- an unambiguous labelled source frame;
- a worked numerical source example;
- direct author transcript/document wording specifying the missing rule;
- equivalent primary evidence that uniquely determines the executable semantics.

Backtest performance, robustness, conventional trading definitions, or implementation convenience cannot substitute for that evidence.

## Checkpoint

This batch closes the audit task for the current evidence set without closing the geometry blockers.
