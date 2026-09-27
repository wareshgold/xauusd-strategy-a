# SP2L Historical Forward Replay — 2026-09-27

## PURPOSE

Freeze the one-month research checkpoint for the current Forward Test execution model before Demo Forward starts.

## CHECKPOINT

Window: 2026-08-26T00:00:00Z .. 2026-09-25T23:59:59Z  
Requested symbol: XAUUSD  
Resolved symbol: XAUUSD.ecn  
Timeframe: M1  
Volume: 0.01  
Mode: HISTORICAL_FORWARD_REPLAY_RESEARCH  
Canonical: false

## CURRENT FORWARD-STYLE CONFIG

- P-Gap: 1.0 price unit
- Spike multiplier: 1.5
- Max SL distance: 10.0
- TP: 1R
- Trigger: first post-setup lower-low / higher-high
- Entry: trigger candle Low / High
- SL: before-spike candle extreme
- Order mode: PENDING_LIMIT_RESEARCH
- Pending TTL: 30 minutes
- Session: London 08:00 -> New York 17:00
- F13 2X: relation-only; not executed
- Fill model: M1 touch at theoretical limit
- Exit model: M1 SL/TP touch; same-M1 dual touch ambiguous

## RESULT

- Bars: 31,574
- Filled: 281
- Closed: 281
- Wins: 150
- Losses: 123
- Expired: 18
- Net: +27R
- Net USD at 0.01 lot: +$84.84
- Open at end: 0
- Pending at end: 0

Artifact:
`artifacts/forward-test-replay/SP2L_HISTORICAL_FORWARD_REPLAY_20260927T123511Z.json`

## INTERPRETATION

This is a reproducible research checkpoint for the current Forward-style replay only. It is not a canonical Strategy A result and must not replace or modify the source-aligned V2 geometry.

The +27R / +$84.84 result is the baseline to compare against the upcoming Demo Forward Test.

Historical M1 replay cannot reproduce live bid/ask, intrabar polling timing, broker fill price, slippage, or broker rejection exactly. Therefore no live-performance guarantee is implied.

## NEXT USE

The Demo Forward Test should use the same Forward configuration above so its observed performance can be compared directly against this checkpoint.

No production promotion is authorized by this checkpoint.
