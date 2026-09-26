# SP2L Strategy A — Official System Snapshot
## 2026-09-26 — Weekend Forensic Checkpoint

**Repository:** wareshgold/xauusd-strategy-a  
**Branch:** research/sp2l-f13-forensic-repro-2026-09-26  
**Purpose:** official research/forensic checkpoint before the next live-market capture.

> This snapshot is research-only. It does not promote Strategy A geometry to canonical status and does not authorize production BUY/SELL decisions.

## 1. Current system state

### Source / geometry
- SP2L remains a source-reconstruction project: source meaning outranks backtest performance.
- Shared detector parity between historical backtest and forward runner is currently **PASS**.
- P-Gap formula, pivot assumptions, AB=CD anchors/tolerance, fill semantics, and production execution semantics remain **unresolved/non-canonical** unless explicitly source-confirmed.
- Geometry promotion remains **BLOCKED**.

### Forensic timestamp state
The latest Saturday timestamp probe is:
- `artifacts/forensic/runtime/SP2L_TIMESTAMP_PROBE_20260926T064507Z.json`
- 30/30 polls completed.
- 10 M1 bars returned on every poll.
- MT5 API reported success on every poll.
- Newest M1 bar stayed at `2026-09-25T23:57:00Z`.
- Tick stayed at `2026-09-25T23:57:59Z`.
- `tick_minus_bar = 59s` on every sample.

Interpretation:
- MT5 API availability on a closed market: **PASS**.
- Internal bar/tick ordering consistency: **PASS**.
- Live-market freshness: **UNRESOLVED** until an actual market-open capture.
- Timestamp/timezone semantics during the open market: **UNRESOLVED**.
- No timezone shift or timestamp normalization is authorized from the weekend evidence.

### Forward-test state
Forward runner is research-only and currently uses:
- XAUUSD.ecn / M1.
- P-Gap 1.0.
- Spike multiplier 1.5.
- Max SL distance 10.
- TP = 1R.
- Research pending-limit execution mode.
- Research SL anchor: spike-candle extreme.
- Polling interval approximately 2 seconds.

Known parity differences versus historical replay:
1. Historical backtest applies a research London-open → New-York-close session filter.
2. Forward runner currently does not apply that same eligibility filter.
3. Historical replay uses theoretical pending-limit fill/outcome diagnostics.
4. Forward execution depends on live MT5/broker acceptance.
5. Forward lifecycle telemetry is not yet sufficient to prove continuous polling across every historical candidate window.
6. Raw MT5 timestamp semantics during an open market are unresolved.

Therefore forward/backtest disagreement cannot yet be interpreted as a strategy-quality failure or a geometry failure.

## 2. What has gone wrong / what remains unresolved

### A. Historical performance was unstable
Earlier author-replica stability work reached roughly 60%+ win-rate across much of the tested parameter grid, with a baseline around 66.9% in one four-week research run. Other non-overlap weekly samples varied materially.

Those numbers are **diagnostic research results, not proof of a canonical edge**. The important issue is not that a >60% result existed; it is that the result has not yet been shown to be stable under frozen, source-confirmed geometry, untouched validation, execution-parity checks, and fresh holdout conditions.

### B. Backtest and forward universe are not yet identical
The historical replay has a session eligibility rule that the forward runner does not currently share. This can create apparent missing/extra signals without any detector difference.

### C. Timestamp semantics are unresolved
Weekend probes show consistent internal MT5 bar/tick ordering, but they cannot establish live freshness or the correct interpretation of terminal timestamps while XAUUSD is actively trading.

### D. Forward telemetry is incomplete for forensic reconciliation
Some forward runs have START/STOP evidence, but continuous polling cannot yet be proven for every candidate window. Raw forward event logs also need to be committed in a stable, auditable location before candidate-by-candidate reconciliation can be completed.

### E. Execution semantics remain research-only
Pending-limit fill, missed execution, same-candle outcomes, broker stop constraints, and lifecycle behavior must not be promoted to canonical strategy rules based on observed performance.

## 3. Official gates

| Gate | Status |
|---|---|
| Shared detector parity | PASS |
| MT5 API response on closed market | PASS |
| Internal tick/bar ordering | PASS |
| Live-market freshness | BLOCKED |
| Open-market timestamp semantics | BLOCKED |
| Forward continuous polling proof | NOT PROVEN |
| Session eligibility parity | UNRESOLVED |
| Fill/execution semantics | UNRESOLVED |
| Canonical geometry | BLOCKED |
| Production strategy status | NOT READY |

## 4. Work plan — next two days

### Sunday 2026-09-27 — offline only
1. Freeze this checkpoint; do not alter detector geometry.
2. Build the deterministic forward/backtest reconciliation harness.
3. Define one auditable candidate schema:
   trigger time → detector match → session eligibility → entry/SL/TP → forward visibility → order state → fill/miss → lifecycle.
4. Audit all available forward artifacts for:
   - candidate presence/absence,
   - trigger timestamp,
   - theoretical entry/SL/TP,
   - session eligibility,
   - forward visibility,
   - execution result,
   - START/STOP coverage.
5. Separate every discrepancy into:
   - MATCH
   - SESSION_MISMATCH
   - TIMESTAMP_UNRESOLVED
   - DETECTOR_MISMATCH
   - EXECUTION_MISMATCH
   - DATA_GAP
6. Prepare Monday's live-market capture procedure without changing the detector.

### Monday 2026-09-28 — first market-open forensic run
1. Run the existing timestamp probe while XAUUSD is actively trading.
2. Establish live:
   - wall-clock vs newest M1 bar,
   - wall-clock vs tick,
   - tick vs bar,
   - raw timestamp behavior.
3. Run forward telemetry continuously.
4. Capture every candidate and its lifecycle.
5. Re-run the same historical interval with the same detector and compare candidate-by-candidate.
6. Do not change P-Gap, spike multiplier, SL anchor, fill semantics, or timestamp normalization merely to improve matching.
7. If timestamp/session mismatch is found, document it first; only then decide whether a research-only adapter is justified.
8. Produce the first real forward/backtest reconciliation report.

## 5. Strategy-status decision path for this week

The goal is to determine the **status of the evidence**, not to force a positive result.

### Possible outcomes
- **Evidence supports further validation:** geometry is source-confirmed/frozen, forward/backtest universe is reconciled, execution semantics are explicitly defined, and fresh holdout remains positive/stable.
- **Research edge but not production-ready:** performance exists, but source/geometry/execution/timestamp parity is still unresolved.
- **No reproducible edge under frozen rules:** forward/backtest/holdout evidence does not reproduce the earlier performance.
- **Data/implementation issue:** discrepancies are explained by timestamp, session, lifecycle, or execution infrastructure rather than strategy geometry.

A historical >60% win-rate is preserved as an observed research result; it is not discarded, but it is also not treated as proof until the reproducibility gates above are passed.

## 6. Non-negotiable constraints

- No backtest result may redefine source meaning.
- No AI-generated geometry becomes canonical without source confirmation.
- No guessed timezone correction.
- No guessed P-Gap formula.
- No guessed pivot rule.
- No guessed AB=CD anchor/tolerance.
- No guessed fill semantics.
- No production BUY/SELL generation from this forensic work.
- Fresh holdout must remain untouched until the research rules are frozen.

## 7. Target deliverables

By the end of this work cycle, the repository should contain:
1. This official system snapshot.
2. Deterministic reconciliation harness/specification.
3. Monday live-market timestamp evidence.
4. Forward-vs-backtest candidate reconciliation.
5. A clear evidence-status report covering XAUUSD forward test and backtest.
6. Only after the above: a decision on whether the strategy can advance to the next validation gate.
