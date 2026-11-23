# SP2L V3.1 XAUUSD Runner — ACT40 / TRAIL40 Audit
Date: 2026-11-23
Scope: Read-only source inspection and reconciliation with the observed 2026-11-23 trade. No runner, MT5, account, position, configuration, or runtime-state changes were made.

## 1. Runner identity and operating context
- Runner: `SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101`
- Entry script: `scripts/run_sp2l_v3_1_xauusd_forward_test.py`
- Config module: `scripts/sp2l_v3_1_rr4_act40_config.py`
- Trailing state module: `scripts/sp2l_trailing_state.py`
- Trailing rules module: `scripts/sp2l_trailing_rules.py`
- Account context previously recorded: OtetGroup-MT5 Demo, login 847788.
- Symbol: XAUUSD.ecn; magic: 26092301.
- Current posture at time of audit: leave the existing runner unchanged; do not stop or restart it as part of this audit.

## 2. Configuration values read from source
The config source explicitly sets:
```python
TP_R = 4.0
TRAIL_PIPS = 4.0
XAU_PIP_SIZE_PRICE = 0.1
TRAIL_DISTANCE_PRICE = TRAIL_PIPS * XAU_PIP_SIZE_PRICE
```
Therefore `TRAIL_DISTANCE_PRICE = 0.40` XAU price units.

## 3. Activation logic confirmed from source
The live runner imports `trailing_activation_reached` from `sp2l_trailing_state.py` and calls it with `cfg.TRAIL_DISTANCE_PRICE`:
```python
if not trailing_activation_reached(
    direction, entry, favorable_extreme, cfg.TRAIL_DISTANCE_PRICE
):
    continue
```
The function computes favorable movement as:
- BUY: `favorable_extreme - entry`
- SELL: `entry - favorable_extreme`

Activation returns true when:
```python
favorable_move(direction, entry, favorable_extreme) >= float(activation_distance)
```
Thus ACT40 is source-confirmed as a favorable price excursion of at least 0.40 for either direction.

## 4. Trailing stop distance confirmed from source
The config's `trail_stop` function calculates:
- BUY: `favorable_extreme - TRAIL_DISTANCE_PRICE`
- SELL: `favorable_extreme + TRAIL_DISTANCE_PRICE`

Thus TRAIL40 is source-confirmed as a 0.40 price-unit trailing distance from the best favorable extreme.

## 5. Additional execution safeguards visible in the runner
- Favorable extremes are updated from completed M1 bar high/low.
- The source comment states trailing is evaluated from the latest completed M1 bar.
- Before sending SLTP, the runner refreshes the current symbol info and quote.
- It normalizes the proposed SL and checks broker stop/freeze distance and whether the new SL improves the old SL.
- It persists favorable-extreme state before attempting broker modification.
These are source observations, not a complete proof that every failure/recovery path is bug-free.

## 6. Observed trade evidence — 2026-11-23
For the observed SELL position:
- Entry: 3616.23
- First logged deferred trailing attempt: quote/broker-distance condition; no SL modification was sent in that attempt.
- Successful `TRAIL_UPDATE`: favorable_move approximately 0.81; trail_pips=4.0; trail_distance_price=0.40; new SL 3615.82; success=true; retcode=10009.
- Subsequent position snapshot showed SL 3615.82.
- Closing deal: exit 3615.83; reason SL; gross profit +0.40; commission -0.05; swap 0; net +0.35.
The trade is consistent with the configured ACT40/TRAIL40 behavior and demonstrates a successful broker SL modification. Because the first successful update was logged after favorable movement had already reached approximately 0.81, this trade alone does not establish the exact first instant at which the 0.40 activation threshold was crossed.

## 7. Audit conclusion and limitations
- ACT40: CONFIRMED from config + function + live call site.
- TRAIL40: CONFIRMED from config + stop formula + successful live update telemetry.
- BUY/SELL activation formulas: both explicitly confirmed in source.
- Observed live SL modification: successful, MT5 retcode 10009.
- No defect was identified in this scoped inspection. This is not a claim that the entire runner is bug-free or that all recovery, retry, broker, Telegram, and history-query paths have been exhaustively validated.
- No settings were changed; no restart was requested or performed.
- This is an operational/source audit record only, not a canonical Strategy A rule decision or production approval.

## 8. Next-start check-in preference
User requested that when they next ask to start the runner, the startup process should include a check-in/connect at the "10-minute" point. Exact interpretation still needs confirmation: 10 minutes after successful startup versus a specific clock time (10:00). Do not assume until clarified.
