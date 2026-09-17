# SP2L Batch 38 — Author Implementation Crosswalk

Date: 2026-09-17

## Objective

Cross-check unresolved SP2L geometry against the public Python implementation authored by Alireza Sadabadi, whose code header identifies the author and points to his SP2L tutorials.

This batch treats the repository as **author-implementation evidence**, not as an automatic replacement for source meaning. Canonicalization remains source-first.

## Repository evidence

Repository: `AlirezaSadabadi/PythonTraderBot`

Relevant files:
- `code/SP2L/SP2L_Bot.py` — v2.0 author implementation
- `code/SP2L/SP2L_Advanced_Bot.py` — v4.0 advanced/live-oriented implementation
- `code/SP2L/SP2L2_Advanced_Backtest.ipynb` — advanced backtest implementation

The implementation files identify Alireza Sadabadi as author/maintainer and point to his YouTube tutorials.

## Decisive implementation findings

### 1. Four-bar SP2L indexing is explicitly encoded

The advanced implementation documents the live indexing convention:

- `-1` = latest candle
- `-2` = candle after spike
- `-3` = spike candle
- `-4` = candle before spike

The setup detector uses this exact fixed window rather than an open-ended swing search.

This materially changes the status of F8/F12: the author implementation does **not** use an unspecified arbitrary historical swing selector for the basic SP2L trigger. It evaluates a fixed local candle sequence.

### 2. Bullish P-Gap construction is explicitly encoded

The author implementation uses:

`low[-2] > high[-4] + P_GAP_PRICE`

The older author implementation uses the equivalent parameterized form:

`low[-2] > high[-4] + pGapSize`

This matches the previously observed author-attributed educational candidate in orientation and indexing, and is materially stronger than a generic secondary-source reconstruction.

Important: this is still implementation evidence. The exact meaning of `pGapSize` / `PGAP_POINTS`, its canonical threshold, and whether the current SP2L teaching source defines this exact numerical construction must remain source-gated.

### 3. Bearish P-Gap mirror is explicitly encoded

The author implementation uses:

`high[-2] < low[-4] - P_GAP_PRICE`

The older implementation uses the equivalent `pGapSize` form.

This is the first direct author-owned implementation evidence resolving the previously unresolved bearish mirror at the construction level.

### 4. Spike candle is fixed at `-3`

Bullish spike body is:

`close[-3] - open[-3]`

and is compared against the body differences of `-2`, `-4`, and `-1` using a configurable multiplier.

Bearish spike is the exact directional mirror using:

`open[-3] - close[-3]`

and corresponding surrounding candle bodies.

The older implementation uses `spikeCandleSize = 2`; the advanced implementation parameterizes this as `SPIKE_CANDLE_SIZE = 1.5` in the inspected revision. Therefore the **geometry family** is stable across author implementations, but the multiplier is configuration/version dependent and is not canonicalized here.

### 5. Basic bullish/bearish trigger includes immediate local break

The author implementation uses:

- BUY: `low[-1] < low[-2]`
- SELL: `high[-1] > high[-2]`

This is the operational second-leg trigger family observed in the advanced implementation and is consistent with the author-associated source description that the corrective candle reaches the prior candle's low/high depending on direction.

The exact executable fill semantics remain separate: a live implementation can use current market bid/ask while a backtest can model a bar-level trigger. Those are not to be conflated.

### 6. Origin candle is used for the basic stop reference

The older author implementation sets:

- BUY SL = `low[-4]`
- SELL SL = `high[-4]`

This aligns directly with the source-level concept that SL is placed behind the candle from which the spike originated.

The advanced implementation also carries the setup-origin timestamp and SL through the pending-to-entry state.

Exact broker-side invalidation/fill semantics remain unresolved for canonical execution.

### 7. Setup and entry are explicitly separated in the advanced implementation

The advanced bot states that setup detection does **not** enter immediately. A detected setup creates a pending setup; a later trigger check determines entry.

This gives strong author-implementation evidence for the state model:

`setup detected -> pending -> second-leg trigger -> trade setup/open-position state`

It also provides a concrete implementation precedent for our lifecycle harness.

### 8. 50% secondary entry is implemented

The advanced implementation computes the secondary entry from risk as:

- BUY: `entry - risk/2`
- SELL: `entry + risk/2`

The configured volume multiplier is `2.0`.

This matches the author-associated source statement that a secondary entry can be added at 50% of the distance from entry to SL. The location relation is therefore strongly cross-confirmed. Whether `2X` is always active, how it is sized, and its full pending/fill lifecycle remain separate questions.

### 9. TP = 1R is implemented

The advanced implementation configures `TP_R = 1.0`, consistent with the author-associated SP2L page's default 1:1 target concept.

This is useful for the engineering baseline but does not by itself resolve all TP lifecycle semantics.

## What this does NOT resolve

### F14 — AB=CD

Search of the author repository did not expose an explicit `AB=CD` implementation in the inspected SP2L Python files/notebook search surface.

Therefore the bot should **not** be used to invent A/B/C/D anchors or tolerance. The primary video remains the correct source target for F14.

### Exact P-Gap canonical threshold

The code exposes configurable values (`pGapSize`, `PGAP_POINTS`, `P_GAP_PRICE`) and the geometry/indexing relation, but configuration is not automatically canonical source meaning.

### Exact entry/fill semantics

The author code contains both live-market and backtest implementations. The live bot can use market bid/ask while the advanced backtest uses deterministic bar logic. This is valuable engineering evidence but does not prove the project's desired canonical touch/wick/close/bid/ask/slippage/partial-fill semantics.

### Filters

EMA60, trend filters, ADX/range filtering, and session filtering are implementation/configuration features. They must not be promoted to canonical SP2L rules merely because they can improve historical performance.

## F8–F16 crosswalk after Batch 38

| Feature | Primary/source evidence | Author implementation evidence | Canonical status |
|---|---|---|---|
| F8 swing/point selection | local points visible; exact algorithm previously unresolved | fixed `-4/-3/-2/-1` sequence in basic detector | **Source confirmation still required before freeze** |
| F9 second-leg trigger | source says corrective candle reaches prior low/high | BUY `low[-1] < low[-2]`; SELL `high[-1] > high[-2]`; pending state | **Strong cross-confirmation; fill semantics unresolved** |
| F10 SL | origin-candle concept | BUY `low[-4]`; SELL `high[-4]` in v2 implementation | **Strong cross-confirmation; exact invalidation semantics unresolved** |
| F11 lifecycle | pending/delete/worked-trade evidence | explicit pending setup state and transition in advanced bot | **Engineering semantics strengthened; canonical lifecycle still source-gated** |
| F12 P-Gap | valid spike requires P-Gap | exact indexed bullish/bearish construction implemented | **Implementation-resolved geometry candidate; source threshold/semantics gate remains** |
| F13 2X | source confirms 50% secondary-entry relation | exact ±risk/2 calculation + volume multiplier 2.0 | **50% relation source-confirmed; full 2X lifecycle unresolved** |
| F14 AB=CD | explicit in primary artifact | no explicit AB=CD code found | **Unresolved** |
| F15 bearish mirror | source confirms up/down trigger mirror | bearish P-Gap and spike mirror implemented | **Strongly strengthened; source freeze still required** |
| F16 round level | visible concept/examples | no decisive round-level algorithm found in inspected SP2L code | **Unresolved** |

## Gate decision

This batch **does not freeze geometry** and does not alter canonical backtest rules.

It does, however, materially reduce the unresolved search space:

1. P-Gap indexing/mirror now has direct author-implementation evidence.
2. The basic SP2L candle window is explicitly fixed in the author's implementation.
3. Second-leg trigger and origin-candle SL are independently reinforced.
4. Pending -> trigger -> entry is reinforced as an author implementation state model.
5. 50% secondary-entry geometry is independently implemented and source-confirmed.
6. AB=CD and Round Level remain the major geometry gaps in the inspected code path.

## Next research sequence

1. **Batch 39 — primary-video F14 AB=CD forensic:** extract the exact A/B/C/D visual anchors and any tolerance/measurement rule from the video.
2. Cross-check F14 against the author's implementation/history if later code exposes an equivalent geometric computation.
3. Return to F8 only if the primary video conflicts with the fixed four-candle implementation window; otherwise record the implementation evidence without inventing a swing algorithm.
4. Perform a final P-Gap source-to-code reconciliation: threshold, exact candle labels, and whether the code's configured 100 points is a test setting or source rule.
5. Freeze only the subset whose source meaning is explicit and reproducible.
6. Build deterministic synthetic fixtures from the frozen subset, then proceed through canonical backtest and untouched validation.

## Non-canonical performance note

The author's repository reports strong historical performance in its own README/backtest artifacts, but those results use particular configurations and filters and are not evidence that every implementation detail is canonical SP2L or that the same edge will reproduce on our untouched dataset. Performance is therefore retained as **external implementation evidence**, not as a geometry definition or production decision rule.
