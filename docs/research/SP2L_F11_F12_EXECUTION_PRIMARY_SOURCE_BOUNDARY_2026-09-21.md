# SP2L F11/F12 Execution Semantics Primary-Source Boundary — 2026-09-21

## F11 — Pending-order lifecycle

### Source-supported
The source supports a **Pending Limit** entry and qualitative refresh/update of the pending setup as the correction/structure develops.

### Not uniquely specified
Primary-source evidence available in the archive does not uniquely determine:
- the exact pending-order price field;
- the event that makes the pending order invalid;
- the numerical or structural replacement threshold;
- time-based expiry versus structure-based expiry;
- whether replacement is cancel/re-place or in-place modification;
- precedence when invalidation and a new trigger occur on the same candle.

Therefore F11 remains unresolved at executable lifecycle level.

## F12 — Trigger / activation / fill

### Source-supported
The source describes a family of **1-, 2-, and 3-candle corrective developments** and a second-leg trigger based on the corrective candle reaching the relevant previous-candle level.

For bearish/downtrend examples, the independently verified source wording uses the previous candle's High. For bullish examples, the corresponding source wording uses the previous candle's Low.

### Not uniquely specified
The archive does not uniquely establish:
- touch versus breach versus close as the trigger event;
- whether trigger and broker fill are the same event;
- exact pending-order activation semantics;
- exact candle precedence in multi-candle developments;
- slippage/fill semantics.

### Implementation boundary
The current close-reclaim EntryTrigger implementation remains research-only and must not be interpreted as source-canonical F11/F12 execution.

## Gate
- F11 source concept: SOURCE-CONFIRMED-PARTIAL
- F11 exact lifecycle: UNRESOLVED
- F12 source trigger family: SOURCE-CONFIRMED-PARTIAL
- F12 exact trigger/fill semantics: UNRESOLVED
- Frozen Geometry: BLOCKED
- Production: DISABLED

## Canonicalization firewall
No touch/breach/close, fill, timeout, replacement, or broker-execution rule is promoted without direct source discrimination.
