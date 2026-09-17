# SP2L MT5 Historical Session Resolution — 2026-09-17

## Purpose

Resolve whether the current XAUUSD.ecn session calendar can be applied to historical MT5 data, without silently converting unavailable session minutes into missing-data failures or changing SP2L strategy geometry.

## Source-confirmed current calendar

Native MQL5 session metadata observed on 2026-09-17 for `OtetGroup-MT5 / XAUUSD.ecn` reported Monday-Friday `01:00:00` through `00:00:00` UTC and no Saturday/Sunday session. The evidence is explicitly marked `historical_applicability=UNVERIFIED` in `SP2L_MT5_SESSION_CALENDAR_XAUUSD_ECN_2026-09-17.json`.

Therefore the current calendar is valid as an observation of the terminal's current schedule, but is not yet canonical evidence for July 2026 or earlier periods.

## New external source evidence — July 2026

The official Otet Markets July 2026 financial-holidays page documents an XAUUSD-specific holiday exception: **3 July 2026 — Close at 20:00**; 1 July is listed as Normal Hours. citeturn3search0

The official Otet Markets financial-holidays page also states that its published trading-schedule times are shown in **MT5 server time** and that the market calendar is updated monthly. citeturn2view1

This is useful historical evidence for a July 2026 holiday/session exception, but it does **not** establish the complete regular Monday-Friday session boundaries for `OtetGroup-MT5 / XAUUSD.ecn`, nor does it establish the exact UTC conversion needed for every July timestamp. It therefore cannot, by itself, resolve the historical calendar used by the July M1 acquisition.

Important distinction:

- **Confirmed:** Otet published a July 3, 2026 XAUUSD early-close exception at 20:00 in its stated MT5-server-time convention. citeturn3search0turn2view1
- **Not confirmed:** the full historical daily session calendar for the specific `XAUUSD.ecn` symbol on `OtetGroup-MT5` throughout July 2026.
- **Not confirmed:** that the current native-MQL5 `01:00-00:00 UTC` schedule was already in force throughout July 2026.

## July 2026 probe

Audit manifest: `artifacts/xauusd-ecn-m1-2026-07-audit.json` (local acquisition artifact; not committed as canonical market data).

Observed under the current-calendar assumption:

- expected active bars: `31,740`
- returned bars: `31,483`
- missing expected timestamps: `257`
- unexpected timestamps: `0`
- invalid timestamp jumps: `14`
- audit status: `AUDITED_FAIL`

The missing timestamps are strongly clustered around recurring session boundaries. The first block begins at `2026-07-03T20:01:00Z` and runs through `23:59:00Z`. Additional evidence includes repeated Friday-to-Monday jumps and weekday jumps around `23:58/23:59 -> 01:00`.

This pattern is evidence that the assumed `01:00-23:59 UTC` calendar does not describe the July data as audited. It is **not** by itself sufficient to define a historical canonical calendar.

## Deterministic resolution policy

1. Do not fill, shift, interpolate, fabricate, or delete candles to make the July audit pass.
2. Do not redefine the calendar solely because a backtest or audit improves.
3. Treat the July result as `AUDITED_FAIL` under the current calendar.
4. Treat historical session applicability as `UNRESOLVED` until independent historical evidence is available.
5. A candidate historical calendar may be tested as a diagnostic hypothesis, but must remain explicitly non-canonical until source evidence supports it.
6. Only an `AUDITED_PASS` dataset using a historically supported calendar may enter published stability/validation datasets.

## Next evidence gate

The source search found useful broker-published July 2026 holiday evidence, but not enough evidence to reconstruct the complete historical session calendar for the exact MT5 symbol/server. The next evidence gate is therefore narrower:

- obtain the historical symbol specification/session schedule for `OtetGroup-MT5 / XAUUSD.ecn`, preferably from the broker/terminal or an archived broker schedule;
- preserve the source date/evidence and server-time convention;
- version the resulting historical calendar separately from the current calendar;
- rerun the unchanged July acquisition audit against that historical calendar.

If no historical source can establish the schedule, the correct research outcome is to leave July historical applicability unresolved rather than infer a canonical calendar from the observed candle pattern.

## SP2L boundary

This resolution concerns only data availability/session semantics. It does not define or modify P-Gap, Spike geometry, AB=CD, entry, stop, target, fill semantics, lifecycle, or production signal rules.
