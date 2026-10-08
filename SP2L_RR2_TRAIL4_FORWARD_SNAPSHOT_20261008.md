# SP2L RR2/TRAIL4 Forward Snapshot — 2026-10-08

## Purpose

Frozen handoff for the RR2/TRAIL4 research forward run on XAUUSD.ecn.
This snapshot records the state before the Thursday/Friday forward observation. The Saturday follow-up should append the real MT5 result without changing the profile retrospectively.

## Research status

- Profile: `SP2L_V3_XAUUSD_RR2_TRAIL4_20261001`
- Mode: `RESEARCH_AUTHOR_REPLICA_MULTI_SYMBOL_FORWARD_TEST`
- Canonical: `false`
- Instrument: `XAUUSD.ecn`
- Account: `847788` / `OtetGroup-MT5`
- Volume: `0.01`
- Order mode: `PENDING_LIMIT_RESEARCH`
- SL anchor: `SPIKE_CANDLE_EXTREME_RESEARCH`
- Pending TTL: `30 min`
- Magic: `26092201`
- TP_R: `2.0`
- TRAIL_PIPS: `4.0`
- Historical profile XAU pip size: `0.1` price/pip
- Historical TRAIL_DISTANCE_PRICE: `0.4`
- Live MT5 symbol point: `0.01`
- Live runner reports pip method: `POINT_FOR_NON_FX_DIGITS`
- No canonical Strategy A rule is being promoted by this experiment.

## Official forward baseline

- Start UTC: `2026-10-08T06:07:37.135003+00:00`
- START_TELEGRAM: `HTTP_200`
- Telegram delivery: `REAL`
- This is the clean forward baseline for today's run.
- Earlier 2026-10-08 starts at 05:16, 05:49 and 05:57 UTC are excluded from the official forward result because Telegram/configuration was incomplete and those runner instances were stopped/restarted.
- Do not tune, replay, or alter the RR2/TRAIL4 profile during this observation window.

## Backtest / research replay baseline

Daily replay was run with the existing RR2/TRAIL4 configuration and is research-only.

### 2026-10-05

- Signals: 16
- Decisive: 16
- Wins: 14
- Losses: 2
- Win rate: 87.50%
- Net: +2.164167 R
- Profit factor: 2.082080
- Ambiguous: 0
- Result SHA: `68943796afd4430919a33182a9bff76d83677f0486a5823c98de451540daea82`

### 2026-10-07

- Signals: 9
- Decisive: 9
- Wins: 8
- Losses: 1
- Win rate: 88.8889%
- Net: +1.345765 R
- Profit factor: 2.345765
- Ambiguous: 0
- Result SHA: `940b17adc4f6e72022e141b742bbacd6fa4769fbc75768c31881c4c89fc0ce37`

### Combined research replay

- Signals: 25
- Wins: 22
- Losses: 3
- Win rate: 88.00%
- Net: +3.509932 R
- Ambiguous: 0

**Important:** These replay results are a pre-forward research baseline, not proof of live edge and not a source for canonical geometry.

## Saturday result — TO BE FILLED

### Real MT5 forward

- Observation window: 2026-10-08 onward
- Official baseline: `2026-10-08T06:07:37.135003Z`
- Signals:
- Trades:
- Wins:
- Losses:
- Ambiguous:
- Blocked:
- Net R:
- Net USD:
- Profit factor:
- Max drawdown:
- TP exits:
- Original SL exits:
- Trail SL exits:
- Telegram lifecycle:
- MT5 reconciliation:
- Final assessment:

## Integrity rules for the follow-up

1. Preserve this pre-forward baseline.
2. Append actual MT5 results; do not rewrite the backtest numbers.
3. Do not tune RR2/TRAIL4 using Thursday/Friday observations before recording the result.
4. Any later comparison must clearly distinguish research replay from real MT5 forward.
5. This experiment does not establish canonical Strategy A geometry or production BUY/SELL authority.
