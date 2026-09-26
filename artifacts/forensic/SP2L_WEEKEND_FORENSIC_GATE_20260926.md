# SP2L Weekend Forensic Gate — 2026-09-26

## Scope

This is a research/forensic checkpoint only. It does not promote geometry to canonical, change the detector, alter timestamp semantics, or define production execution rules.

Current branch:

- `research/sp2l-f13-forensic-repro-2026-09-26`
- latest captured probe commit: `ad53b77`

## Current evidence

### Timestamp probe

Artifact:

`artifacts/forensic/runtime/SP2L_TIMESTAMP_PROBE_20260926T064507Z.json`

Observed:

- 30/30 polls completed.
- 10 M1 bars returned on every poll.
- MT5 last error was `[1, "Success"]` on every rates request.
- Newest M1 bar stayed at `2026-09-25T23:57:00Z`.
- Tick stayed at `2026-09-25T23:57:59Z`.
- `tick_minus_bar = 59.0s` on all 30 samples.
- Tick bid/ask stayed at `4286.05 / 4286.27`.
- Wall-clock minus newest bar increased from about 24427.84s to 24485.89s.

Interpretation:

- MT5 API availability: PASS for this closed-market capture.
- Internal bar/tick ordering consistency: PASS.
- Live-market freshness: UNRESOLVED.
- Timestamp timezone semantics: UNRESOLVED.
- This capture cannot establish a stale-data defect because it was performed while XAUUSD was closed on Saturday.

No timestamp normalization or detector change is justified by this evidence.

## Existing detector/backtest/forward parity

The research backtest and forward runner use the shared module:

`scripts/sp2l_author_replica_detector.py`

The shared detector currently defines the research-only geometry and signal levels. This is useful for preventing silent geometry drift between the two paths.

Important execution/session differences remain intentionally unresolved:

1. Historical backtest applies the research London-open -> New-York-close session filter.
2. Forward runner does not apply that historical session filter.
3. Historical replay uses theoretical pending-limit fill/outcome diagnostics.
4. Forward runner uses a research pending-limit demo order mode.
5. Forward lifecycle and broker acceptance depend on live MT5 state.
6. Raw MT5 candle timestamps are not yet empirically resolved during an open market.

These differences must not be collapsed into one canonical rule.

## Weekend work completed / gate status

| Gate | Status | Meaning |
|---|---|---|
| Shared detector parity | PASS | Backtest and forward import the same research detector |
| MT5 API response on closed market | PASS | Rates/tick requests succeed |
| Internal tick/bar ordering | PASS | Stable 59s relationship observed |
| Live-market freshness | BLOCKED | Requires an open-market capture |
| Timestamp timezone semantics | BLOCKED | Requires an open-market capture |
| Forward continuous polling proof | NOT PROVEN | Existing lifecycle telemetry has START/STOP but not continuous-poll proof for all historical intervals |
| Session eligibility parity | UNRESOLVED | Backtest has research session filter; forward does not |
| Fill/execution semantics | UNRESOLVED | Research-only and not canonical |
| Geometry promotion | BLOCKED | Source confirmation still outranks performance |

## Next decisive market-open test

When XAUUSD opens, run the existing timestamp probe unchanged:

`python scripts/run_sp2l_timestamp_probe.py`

The capture should establish whether:

- newest M1 bars advance with wall time;
- tick timestamps advance with wall time;
- tick/bar ordering remains coherent;
- the apparent multi-hour wall-clock gap disappears or has a reproducible explanation.

Only after that gate is resolved should timestamp reconciliation be used in the forward-vs-backtest audit.

## Next offline work

Before market open, the safe work is limited to deterministic offline analysis:

1. Freeze the current forensic evidence and do not reinterpret Saturday captures as live freshness evidence.
2. Audit forward/backtest eligibility differences, especially the research session filter.
3. Audit event-time semantics and signal visibility timing without changing the detector.
4. Build a reconciliation matrix for candidate presence/absence, trigger timestamp, theoretical entry, SL, TP, and execution status.
5. Keep geometry, fill semantics, and execution semantics explicitly research-only until source resolution.

## Prohibited changes at this gate

Do not:

- shift MT5 timestamps by a guessed timezone offset;
- change P-Gap;
- change pivot/candle indexing;
- change AB=CD geometry;
- change SL anchor;
- change fill semantics to improve agreement;
- add/remove a session filter from the canonical strategy;
- promote the current backtest or forward results to canonical performance.

