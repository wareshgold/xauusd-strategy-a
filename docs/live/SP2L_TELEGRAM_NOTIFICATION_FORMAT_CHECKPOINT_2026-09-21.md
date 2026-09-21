# SP2L Telegram Notification Format Checkpoint — 2026-09-21

## Status

FORMAT REGISTERED — RESEARCH / DEMO NOTIFICATION LAYER ONLY

This checkpoint records the operator-approved Telegram presentation format for the
current MT5 DEMO forward-test infrastructure.

It does not promote any Strategy A geometry, execution semantics, or signal logic
to canonical status.

## Signal message

Required presentation:

```text
🟢 XAUUSD BUY

Entry: 4353.15
SL: 4350.59
TP: 4355.71

SL: -2.56
TP: +2.56

Time: 09:42
Date: 21/09/2026
```

SELL uses the corresponding red/down direction marker.

## Result message

Required presentation:

```text
✅ XAUUSD BUY — TP

Entry: 4353.15
Exit: 4355.71

TP: +2.56
SL: -2.56

Time: 10:18
Date: 21/09/2026
```

For an SL result, the result label and realized amount must reflect the SL exit.

## Required fields

- XAUUSD direction
- Entry
- SL
- TP
- TP/SL price-distance amounts
- Tehran local time (Asia/Tehran)
- Tehran local date

## Explicitly excluded from Telegram presentation

Do NOT display:

- Volume
- Signal ID
- Internal status labels such as DEMO EXECUTED
- Research-only / non-canonical disclaimer text

Those values may remain in machine-readable journals/artifacts and are not
part of the operator-facing Telegram message.

## Safety / semantics

- Telegram is notification/reporting infrastructure only.
- It must not discover, modify, or define Strategy A geometry.
- It must not autonomously create BUY/SELL decisions.
- Forward-test messages remain research/DEMO infrastructure messages.
- Actual TP/SL result notifications must be based on an observed MT5 position/deal
  outcome; a theoretical target must never be reported as a realized result.
- Time conversion for Telegram presentation is Asia/Tehran, regardless of MT5
  server time or UTC storage timestamps.
