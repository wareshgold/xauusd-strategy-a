# SP2L Session Snapshot — 2026-09-17

## 1. Purpose

This snapshot records the project state after the MT5 session-aware acquisition work and the first historical-coverage probe. It is a recovery checkpoint, not a strategy-rule freeze.

## 2. Project objective

Build a source-aligned, deterministic, statistically validated XAUUSD Strategy A system based on SP2L (Spike → 2 Leg).

Primary principle:

> Source meaning outranks backtest performance.

Only source-confirmed rules may become canonical. Unresolved geometry remains explicitly unresolved.

AI may assist research, engineering, validation, documentation, and analytics, but must not autonomously define canonical rules or generate production BUY/SELL decisions.

## 3. Required workflow

SOURCE RESOLUTION
→ SYNTHETIC FIXTURES
→ FROZEN GEOMETRY
→ DEV
→ UNTOUCHED VALIDATION
→ ROBUSTNESS/STABILITY
→ FRESH HOLDOUT
→ PRODUCTION

Production is gated. The current project is still in research/data-resolution stages and is not production-ready.

## 4. What has been completed

### A. MT5 provenance and acquisition contract

Established the required provenance for the MT5 source:
- Terminal: Otet Group MT5 Terminal
- Server: OtetGroup-MT5
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Provider: MetaTrader5 terminal API

Acquisition requirements include exact UTC normalization, actual first/last timestamps, count, continuity/session audit, raw artifact materialization, SHA-256, acquisition revision, and downstream configuration identity.

### B. Strict acquisition diagnostics

The initial `copy_rates_range` behavior exposed endpoint/count mismatches. Diagnostics compared:
- `copy_rates_range`
- `copy_rates_from`
- `copy_rates_from_pos`

The project was changed to fail closed rather than silently shifting, filling, or fabricating candles.

### C. Native MQL5 session metadata

Native MQL5 `SymbolInfoSessionQuote` / `SymbolInfoSessionTrade` was compiled successfully and executed.

Observed current metadata for XAUUSD.ecn:
- Monday–Friday: 01:00:00 → 00:00:00 UTC
- Saturday/Sunday: no sessions

The calendar is explicitly marked `historical_applicability=UNVERIFIED`; current observation is not treated as historical proof.

### D. Session-aware audit

A session-aware audit was implemented. It permits timestamp jumps only when every minute strictly between the jump endpoints is inactive under the supplied calendar. It still fails on missing active-session timestamps, duplicates, non-chronological data, unexpected timestamps, and invalid jumps.

A controlled 2026-09-16 22:00 → 2026-09-17 02:00 test passed under the observed current calendar:
- expected active bars: 181
- returned bars: 181
- missing: 0
- unexpected: 0
- unique: true
- chronological: true
- jump 23:59 → 01:00 accepted as session boundary
- audit: `AUDITED_PASS`

### E. Historical coverage probe

A historical coverage probe was scoped for July, August, September, June, May, and April 2026.

The first July 2026 probe used the current observed calendar only as a diagnostic calendar; it was not treated as historically validated.

### F. July 2026 result

Dataset: `xauusd-ecn-m1-2026-07`

Audit result:
- expected active bars: 31,740
- returned bars: 31,483
- missing: 257
- unexpected: 0
- invalid jumps: 14
- status: `AUDITED_FAIL`
- historical calendar status: `UNRESOLVED`
- artifact SHA-256: `482991df85c7143077ef3713c81f3c5ae14ae12311f6c03e3579f27f8048e34e`

Pattern diagnostic:
- missing dates: 15
- largest missing block: 2026-07-03, 239 minutes
- repeated late-session missing timestamps, especially 23:59
- daily jumps around 23:58/23:59 → 01:00
- weekend jumps Friday → Monday

Interpretation: the supplied current calendar does not match the observed July data pattern. This does NOT prove that the candles are missing from the historical market session; it demonstrates that the calendar used for the audit is not historically resolved.

## 5. What must NOT be done

- Do not fill missing candles.
- Do not interpolate or shift timestamps.
- Do not silently delete missing periods.
- Do not change SP2L geometry to accommodate data artifacts.
- Do not infer a historical broker calendar solely from the July data pattern.
- Do not mark July `AUDITED_PASS` until the historical session applicability question is independently resolved.
- Do not mix MT5/OtetGroup-MT5/XAUUSD.ecn/M1 with the repository Twelve Data XAU/USD/UTC dataset without explicit provenance separation.
- Do not treat `AUDITED_PASS` under an unverified historical calendar as historical validation proof.

## 6. Immediate next work

### Gate 1 — Historical session calendar resolution

Determine whether an authoritative or independently documented historical session schedule for XAUUSD.ecn / OtetGroup-MT5 exists for July 2026.

Evidence hierarchy:
1. broker/server-native historical session metadata or documented historical schedule;
2. broker documentation with explicit effective dates;
3. independently reproducible historical evidence tied to the same symbol/server;
4. data-pattern evidence only as supporting evidence, never as sole canonical source.

If historical applicability cannot be proven, keep July historical calendar status `UNRESOLVED` and do not publish it into validation/stability.

### Gate 2 — Re-audit only after calendar evidence is resolved

Run the exact same raw-data audit with the versioned historical calendar. No data repair is allowed.

Required output:
- exact expected active timestamps
- exact returned timestamps
- missing/unexpected counts
- unique/chronological status
- invalid jumps
- raw artifact SHA-256
- calendar ID and evidence provenance

### Gate 3 — Expand coverage

Repeat the same controlled process for August and September 2026, then assess June/May/April only after historical calendar applicability is separately addressed.

### Gate 4 — Freeze data provenance

Only `AUDITED_PASS` artifacts with a resolved/verified applicable calendar may enter published stability/validation datasets.

## 7. Strategy research status

The previously established non-overlap stability sample remains descriptive only:
- 190 wins
- 117 losses
- 5 ambiguous
- 307 decisive
- pooled decisive WR: 61.89%
- pooled total R: +73R
- pooled PF: approximately 1.62

These results do not canonicalize any rule and do not override unresolved source meaning, geometry, execution/fill semantics, AB=CD/F14, or historical data applicability.

## 8. Geometry and execution status

Still unresolved / blocked from canonical freeze:
- P-Gap formula
- AB=CD anchors/tolerance / F14
- execution and fill semantics
- lifecycle semantics where source evidence is incomplete

No strategy rule has been modified because of the July data audit.

## 9. Recovery procedure for the next session

1. Pull the branch and verify the checkpoint commit.
2. Read this snapshot first.
3. Read `SP2L_MT5_HISTORICAL_SESSION_RESOLUTION_2026-09-17.md`.
4. Verify the July audit artifact and SHA-256.
5. Resolve historical session applicability before changing the audit calendar.
6. Re-audit without modifying raw data.
7. Continue August/September coverage only under the same provenance and gating rules.
8. Do not proceed to statistical validation with unresolved data/session integrity.

## 10. Current status

Overall phase: **SOURCE RESOLUTION / DATA PROVENANCE**

Historical July session calendar: **UNRESOLVED**

July audit under current calendar: **AUDITED_FAIL**

Strategy canonicalization: **BLOCKED**

Production: **NOT AUTHORIZED**

This checkpoint is intended to prevent loss of context between sessions and to preserve the exact workflow and decision gates.
