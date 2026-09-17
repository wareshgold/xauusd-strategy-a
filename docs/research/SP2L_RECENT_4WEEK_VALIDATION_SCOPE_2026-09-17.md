# SP2L Recent 4-Week Validation Scope — 2026-09-17

## Question
Can the most recent four weeks be tested now?

## Decision
Yes, as a **descriptive research / stability sample**, provided the exact data provenance and session treatment are preserved. It must not be treated as canonical validation or production authorization.

## Proposed period
Use the latest four completed calendar weeks available before 2026-09-17, with an explicit UTC boundary and no look-ahead. The exact start/end timestamps must be recorded in the acquisition artifact.

## Data requirements
- Provider/terminal: Otet Group MT5 Terminal
- Server: OtetGroup-MT5
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Raw source: MT5 acquisition
- UTC normalization without changing instants
- Session calendar must be evidence-backed
- No shifting, interpolation, fabrication, or silent deletion
- Exact first/last UTC timestamps, row count, continuity audit, and SHA-256 required

## Important distinction
The current terminal session observation establishes a weekday session boundary of 01:00–00:00 UTC for the observed current schedule. It does **not** by itself prove that the same schedule applied throughout the historical four-week period.

Therefore the four-week sample should be split into:
1. periods for which session applicability is source-resolved;
2. periods where it remains unresolved.

Only the first category can enter a published AUDITED_PASS dataset.

## Strategy status
This test must reuse the already frozen research configuration and must not alter P-Gap, spike multiplier, SL, TP, AB=CD, fill semantics, or lifecycle rules.

The resulting statistics are descriptive. They do not establish a canonical edge by themselves and do not authorize BUY/SELL production decisions.

## Current source evidence
Otet's September 2026 financial-holidays page states that schedule times are MT5 server time and identifies XAUUSD holiday changes, including a September 7 early close at 21:30. The broker states its general labor hours are 00:00 Monday through 24:00 Friday EET, with additional non-working periods for holidays and possible schedule adjustments from liquidity providers.

These sources support handling explicit holiday exceptions, but do not establish the complete historical symbol-specific session schedule for every minute of the recent four-week period.

## Gate
STATUS: `RESEARCH_SCOPE_APPROVED`

This scope may proceed to acquisition/audit. A result must remain `UNRESOLVED` wherever historical session applicability cannot be demonstrated from source evidence.
