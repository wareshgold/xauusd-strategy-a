# Strategy A trailing semantics — source-resolution checkpoint (2026-10-25)

## Status

**UNRESOLVED — RESEARCH ONLY — NOT CANONICAL.**

This note records an evidence gap and a deterministic next step. It does not select a trailing rule, alter Strategy A geometry, or authorize production execution. No runner, signal, order, fill, stop, target, or production-decision code is changed by this note.

## Question to resolve

Does the authoritative SP2L source explicitly define *when* a trailing stop activates, and, if so, what threshold, price series, bar/tick timing, and stop-update semantics does it prescribe?

Until a primary source answers that question, the activation gate and the distance `0.40` must remain research assumptions. Backtest performance is not evidence of source meaning.

## Evidence currently available

### 1. GitHub source-audit implementation

The source-audit implementation on branch `research/monthly-matrix-source-audit-20261024` explicitly describes itself as a source-aligned **candidate replay**, not an execution backtest. Its recorded Strategy A constants include P-Gap, spike multiplier, maximum stop distance, target R, and pending TTL; it does not establish canonical trailing activation semantics.

Reference: [monthly_matrix_source_audit.py](https://github.com/wareshgold/xauusd-strategy-a/blob/research/monthly-matrix-source-audit-20261024/scripts/research/monthly_matrix_source_audit.py)

### 2. OHLC proxy implementation

The proxy on branch `research/monthly-matrix-ohlc-proxy-20261024` sets `A_TRAIL_DISTANCE = 0.40` and labels the trail as a sensitivity proxy. Its implementation updates the stop from the best completed-bar high/low, with the update effective only on a later bar. These are explicit proxy assumptions, not proof that the author prescribed them.

Reference: [monthly_matrix_ohlc_proxy_backtest.py](https://github.com/wareshgold/xauusd-strategy-a/blob/research/monthly-matrix-ohlc-proxy-20261024/scripts/research/monthly_matrix_ohlc_proxy_backtest.py)

### 3. Local V1/V3 sensitivity comparison (reported; not reproducible from this branch alone)

The local V1 and V3 generators and their 462-row CSVs were not present in the inspected GitHub tree at this checkpoint. The following numbers are therefore recorded as reported local diagnostics, not independently reproduced by this repository commit:

- V1: `195.093909R` total closed-proxy R.
- V3: `192.710301R` total closed-proxy R.
- Difference (V3 minus V1): `-2.383608R`.
- Matched valid-R rows: 461; one unresolved row excluded.
- Matched rows: 413 unchanged, 35 better under V3, 13 worse under V3.
- All 13 reported V3 deteriorations had best favorable excursion below the assumed `0.40` activation threshold before the V1 proxy exit. The three largest examples had excursions `0.39`, `0.36`, and `0.36` price units.

These observations explain the difference between the two *implementations*. They do not validate either implementation as the source rule or establish executable broker outcomes.

## Implementation difference under test (descriptive, not normative)

- **V1 proxy:** BUY uses `stop = max(stop, best - 0.40)` after each eligible bar; SELL uses `stop = min(stop, best + 0.40)` after each eligible bar. There is no separate `0.40` favorable-excursion activation gate.
- **V3 proxy:** the same stop update is applied only after BUY's best high reaches `entry + 0.40`, or SELL's best low reaches `entry - 0.40`.

Neither behavior is declared canonical here. Do not infer that V1's immediate update or V3's threshold gate is correct from the reported results.

## Required primary-source evidence

Before freezing any trailing geometry, attach or identify the authoritative source artifact and capture an exact locator (document title/version plus page/section, or video/audio timestamp and transcript/source excerpt) that resolves, or explicitly fails to resolve, each item:

1. Is trailing-stop behavior specified by the SP2L author/source at all?
2. Is `0.40` a source-defined price distance, a broker-specific setting, or only a research parameter?
3. Is there an activation gate? If yes, what exact condition activates it?
4. Which price is used to track favorable movement (bid, ask, last, candle high/low, close, or another source-defined value)?
5. Is the stop updated intrabar or only after a completed candle? When does the updated stop become effective?
6. What are the exact BUY/SELL inequalities and the initial-stop interaction?
7. If the source does not specify one of these details, record it as **UNRESOLVED**. Do not fill the gap with a backtest-selected rule.

Do not resolve fill semantics, intrabar ordering, spread/slippage, or execution behavior from OHLC candles alone. Those require separate source resolution and/or suitable tick/broker evidence.

## Gate and next action

**Current gate: SOURCE RESOLUTION BLOCKED.**

Next action: locate the original author material (and any contemporaneous source notes already maintained by the project), cite the precise passage for trailing behavior, and map each item above to **SOURCE-CONFIRMED**, **SOURCE-CONTRADICTED**, or **UNRESOLVED**. If no primary-source passage exists, preserve the unresolved status; do not promote either proxy to canonical.

No synthetic fixtures, frozen geometry, or production behavior should be changed on the basis of this checkpoint alone.
