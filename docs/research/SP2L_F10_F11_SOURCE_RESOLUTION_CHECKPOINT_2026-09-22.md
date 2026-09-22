# SP2L F10/F11 Source Resolution Checkpoint — 2026-09-22

## Scope
Re-audit F10 stop/invalidation geometry and F11 pending-order lifecycle using the current primary-source records, visual triangulation, and author-implementation crosswalk. No historical performance is used to choose a rule.

## F10 — Stop / invalidation anchor

### Source-confirmed
- Primary author-controlled material ties SL to the candle from which the Spike originated.
- Archived visual evidence shows the SL remaining below the original/base structural area while the pending Buy Limit can move upward with the evolving higher-low sequence.
- Entry and structural invalidation are distinct.

### Strong implementation cross-confirmation
- The inspected author implementation uses BUY `low[-4]` and SELL `high[-4]` for the basic origin-candle stop reference.
- The same implementation fixes the local setup window around `-4/-3/-2/-1`.

### Canonical decision
F10 remains **PARTIALLY RESOLVED / NOT FROZEN**.

The implementation evidence materially narrows the candidate to the origin candle's directional extreme, but implementation is not primary source meaning. The canonical gate still lacks a uniquely authoritative specification of:
- wick extreme versus body/open/close boundary;
- any broker/spread/buffer treatment;
- exact invalidation event and evaluation timing.

Therefore `BUY SL = low[-4]` / `SELL SL = high[-4]` remains an author-implementation candidate, not a frozen Strategy A rule.

## F11 — Pending-order lifecycle

### Source-confirmed
- Pending Limit is part of the demonstrated execution model.
- The source permits deleting an existing order and placing a new order when the structure develops and the distance to SL changes.
- Visual evidence shows the pending Buy Limit reference moving upward to the currently relevant completed higher-low in the demonstrated bullish sequence.

### Still unresolved
- Whether refresh is mandatory or optional in each circumstance.
- Exact predicate for retaining versus replacing the order.
- Exact replacement-price construction across all Spike variants.
- Any timeout/expiry rule.
- Candidate precedence when multiple structural levels coexist.

### Implementation cross-confirmation
The author implementation provides a pending setup/state transition before second-leg trigger and reinforces separation between setup detection and later activation. This strengthens the lifecycle model but does not close the source ambiguity around refresh/replacement.

## Important non-promotions
- No fixed timeout such as 1–2 candles is promoted from earlier provisional notes.
- No exact refresh threshold is invented.
- No `Entry = C` or `Fill = C` assumption is introduced.
- No market-close-reclaim rule is promoted as a replacement for the pending Limit model.
- No backtest result is used to select F10 or F11 geometry.

## Gate result
| Item | Status |
|---|---|
| F10 origin-candle concept | SOURCE-CONFIRMED |
| F10 exact executable price | UNRESOLVED |
| F10 invalidation event | UNRESOLVED |
| F11 Pending Limit concept | SOURCE-CONFIRMED |
| F11 refresh/replacement concept | SOURCE-CONFIRMED |
| F11 deterministic replacement predicate | UNRESOLVED |
| Frozen Geometry | BLOCKED |
| Untouched Validation | LOCKED |
| Fresh Holdout | LOCKED |
| Production | OFF |

## Next discriminating evidence
The highest-value remaining source artifact is a labelled primary chart/worked example that simultaneously identifies the Spike-origin candle, exact SL line placement, current pending-limit level, and the candle/event that causes order replacement. If that artifact is unavailable at auditable resolution, F10/F11 remain explicitly unresolved.

No canonical production code was changed.