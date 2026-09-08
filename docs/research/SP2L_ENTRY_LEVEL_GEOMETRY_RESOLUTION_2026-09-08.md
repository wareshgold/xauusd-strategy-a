# SP2L / Strategy A — Entry-Level Geometry Resolution

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION  
**Status:** `PROGRESSING — ENTRY SEMANTICS RESOLVED, EXACT PRICE ANCHOR UNRESOLVED`

## Purpose

This note isolates the entry-level question from the broader P-Gap and AB=CD questions. The objective is to determine exactly what the source author means by the pending order, without promoting a visually plausible price level to canonical geometry.

## 1. Direct source evidence

### Transcript: correction and pending Limit

The source states that once the next candle begins correction, correction is described as price moving below the first low (bullish case), and an order can be placed there manually or as a pre-set Limit. The same section explains that the order may already be placed during the first three candles and later becomes activated.

**Interpretation locked:** the strategy uses a pending order during correction; a later close-reclaim is not an equivalent canonical implementation.

### Visual frame: Buy Limit

Frame `g2380.jpg` shows a bullish three-candle teaching diagram with a handwritten `Buy Limit` label, a horizontal order line, and a separate `SL` line below. The order line is visibly inside the rising structure rather than at the final market price.

### Visual frame: order line

Frame `g2400.jpg` shows the same bullish construction with a horizontal order line crossing the rising sequence. The line is an explicitly drawn order level; it is not sufficient to identify it as an OHLC anchor.

### Visual frame: Delete / order management

Frame `g2420.jpg` shows the horizontal order line with `Delete` written beside it and an additional downward annotation. This corroborates that the line represents a pending order whose placement can be revised/deleted as the structure develops.

## 2. What is now source-supported

The following semantics can be treated as source-confirmed/strong:

1. Entry is a **pending Limit order**, not a market order triggered by a later close.
2. The Limit can be placed before fill, during the correction phase.
3. The pending order has an associated structural SL.
4. The pending order can be deleted/replaced if the developing structure changes the risk distance materially.
5. In the bullish example, the source discusses correction in relation to the first low; this is evidence about the correction condition, not by itself proof that the order price equals that low.

## 3. What remains unresolved

The visual evidence does **not** uniquely establish which exact price is used for the pending Limit.

Surviving hypotheses include, but are not limited to:

- H1: a source-defined correction boundary/level;
- H2: an OHLC anchor from one of the Spike candles;
- H3: a later structural level selected after correction begins;
- H4: classical A/B/C terminology mapped to the entry level;
- H5: another source-specific level not recoverable from the current low-resolution teaching frame alone.

No hypothesis is canonical yet.

## 4. Important negative finding

The `Buy Limit` line in `g2380.jpg` / `g2400.jpg` visually intersects the rising candle sequence, but the frame does not expose numerical OHLC values or an unambiguous A/B/C label. Therefore:

- `entry = C` is **not** source-confirmed;
- `entry = first low` is **not** source-confirmed;
- `entry = last spike candle open/close/high/low` is **not** source-confirmed;
- `entry = 50% retracement` is **not** source-confirmed;
- no fib percentage may be introduced merely because it fits the drawing.

## 5. Relation to AB=CD

The source separately demonstrates `AB=CD` and a second leg equal to the first leg. That does not prove that the pending Limit price is point C. The source's classical AB=CD discussion explicitly moves from abstract A/B/C/D terminology toward candle-level execution, so anchor mapping must be recovered from the actual teaching examples before implementation.

Therefore the current source-aligned implementation must continue to accept the correction/entry price as an externally source-confirmed input rather than deriving it from an invented C formula.

## 6. Synthetic fixture requirements added

The next fixture set must distinguish at minimum:

| Fixture | Purpose |
|---|---|
| E1 | first-low equals candidate Limit |
| E2 | first-low differs from candidate Limit |
| E3 | Limit equals a Spike-candle OHLC level |
| E4 | Limit lies inside Spike candle body but is not an OHLC value |
| E5 | correction reaches level but pending order is placed elsewhere |
| E6 | pending order is deleted/replaced after structural risk changes |
| E7 | price later closes/reclaims the level without ever filling the Limit |
| E8 | Limit fills intrabar before candle close |

These fixtures are discriminators only. They do not choose a hypothesis without source evidence.

## 7. Decision

**Entry semantics:** `RESOLVED / STRONG`  
**Exact entry price formula:** `UNRESOLVED`  
**Entry = C:** `UNRESOLVED`  
**Entry = first low/high:** `UNRESOLVED`  
**Market close-reclaim substitute:** `REJECTED`

This decision does not authorize historical DEV or production changes.

## 8. Next source-resolution action

Resolve the entry anchor jointly with A/B/C/D rather than in isolation:

1. mine every transcript statement around 36:20–42:00 for named levels;
2. inspect the real-chart A/B/C/D example around ~62:30;
3. compare those labels with the educational Buy Limit diagram;
4. determine whether the same geometric level is reused;
5. only if the source provides a unique mapping, freeze the entry formula;
6. otherwise retain `UNRESOLVED` and continue source research.

**Gate rule:** no profitability result may be used to select among E1–E8.
