# SP2L Forward/Backtest Parity Audit — 2026-09-26

## Scope

Static source audit of the shared detector, the XAUUSD research forward runner, and the MT5 historical backtest. This is an engineering/forensic audit only; it does not define canonical Strategy A rules.

## Findings

| Area | Status | Evidence |
|---|---|---|
| Detector implementation | PASS | Both paths use `scripts/sp2l_author_replica_detector.py`. |
| Detector window | PASS | Shared detector uses `[-5],[-4],[-3],[-2]`; final bar is current/forming. |
| Research parameters | PASS | pGap=1.0, spike multiplier=1.5, max SL=10.0, TP=1R. |
| Signal levels | PASS | Entry/SL/TP originate from the shared detector. |
| Forward session filter | MISMATCH / UNRESOLVED | Historical backtest explicitly filters to its research session; forward runner does not apply that same eligibility filter. |
| Forward execution | RESEARCH-ONLY DIFFERENCE | Forward runner places a pending-limit research order at the theoretical entry; historical outcome logic evaluates future M1 touch of the theoretical entry. These are not yet proven equivalent execution semantics. |
| Timestamp semantics | BLOCKED | Forward events retain wall-clock `ts_utc` plus raw MT5 trigger epoch; historical timestamp mapping remains unresolved. |
| Fill semantics | BLOCKED | No source-confirmed canonical fill rule. Current historical touch logic is research-only. |
| SL-anchor semantics | BLOCKED | Current `SPIKE_CANDLE_EXTREME_RESEARCH` is explicitly non-canonical. |
| Geometry promotion | BLOCKED | Shared detector remains research-only. |

## Important documentation inconsistency

The forward-runner module docstring still contains an older description of MARKET execution after the completed trigger, while the active configuration and implementation use `PENDING_LIMIT_RESEARCH`. This is documentation drift, not evidence that execution semantics are resolved.

No trading behavior is changed by this audit.

## Consequence

The detector itself is structurally centralized, which reduces silent geometry drift between the two research paths. The remaining reconciliation blockers are primarily **session eligibility, timestamp interpretation, and execution/fill semantics**, not an identified detector-code fork.

## Required next evidence

On the next open-market capture, retain for each observed candidate:

1. raw MT5 trigger epoch;
2. independent wall-clock UTC capture;
3. forward candidate event;
4. session-eligibility context;
5. order request/result;
6. pending-order state;
7. fill/deal lifecycle.

Reconciliation remains exact/raw-first. No timezone shift or numeric tolerance is to be invented to force a match.
