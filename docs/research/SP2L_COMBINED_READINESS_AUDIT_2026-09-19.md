# SP2L Combined Readiness Audit — 2026-09-19

## Scope

This checkpoint combines three non-invasive audits that can be completed while the Fresh Holdout has no eligible post-boundary bars:

1. Parameter Stability evidence review.
2. Production execution-infrastructure readiness review.
3. Source/Frozen Geometry gate review.

No canonical parameter, source rule, geometry rule, fill semantic, or live-trading authorization is changed by this audit.

## A — Parameter Stability

### Archived evidence reviewed

The pre-registered protocol and existing 81-combination assessment were reviewed.

Current evidence:

- 81/81 tested combinations have positive Total R.
- 80/81 are above the descriptive 60% decisive-WR reference.
- Matrix median decisive WR: 65.972%.
- Baseline decisive WR: 66.883%.
- Baseline: 103 wins / 51 losses / 4 ambiguous; 154 decisive.
- Baseline Total R: +52R.
- Baseline PF: 2.020.
- Baseline weekly decisive WR: 72.973%, 70.270%, 52.941%, 69.565%.
- TP is the most sensitive tested dimension in the archived main-effect summary.
- S5 multiple-testing guard is PASS.
- S6 uncertainty remains descriptive/limited.

### Gate

**PARAMETER STABILITY: INCONCLUSIVE — NO PASS / NO FAIL**

Reason: the observed temporal sample is mixed, with one materially weaker week, and the available historical sample is still development/research data rather than untouched validation.

No parameter is promoted because of matrix performance.

## B — Production Execution Infrastructure

### Verified from committed code and checkpoints

The authoritative gateway is:

`scripts/live_mt5_gateway.py`

The gateway:

- accepts an externally produced APPROVED signal;
- does not calculate Strategy A geometry;
- defaults `LIVE_TRADING_ENABLE=false`;
- enforces `MAX_OPEN_POSITIONS`;
- uses ask for BUY and bid for SELL;
- supports dry-run execution without calling `mt5.order_send` when live trading is disabled;
- records signal/trade/market-snapshot journal events;
- rejects duplicate signal IDs and archives the consumed signal;
- exposes Nexora public branding rather than the internal SP2L strategy name.

Committed offline safety coverage includes:

- non-APPROVED signal rejection;
- SELL dry-run using bid;
- MAX_OPEN_POSITIONS guard;
- Nexora branding regression coverage.

The existing runtime checkpoint records PASS for the previously executed synthetic dry-run path, journal, Excel export, and broker reconciliation with zero MT5 deals.

### Remaining local-only verification

The following require the user's local MT5/Telegram runtime and are not claimed as newly executed by this audit:

- restart/persistence runtime test;
- credentialed Telegram delivery test;
- live broker-history reconciliation after any future real execution.

These are infrastructure verification items, not reasons to enable live trading now.

### Gate

**EXECUTION INFRASTRUCTURE: READY FOR CONTROLLED DRY-RUN / NOT AUTHORIZED FOR PRODUCTION STRATEGY AUTO-SIGNALS**

The gateway can remain present and guarded without authorizing Strategy A production decisions.

## C — Source / Frozen Geometry Gate

The source-first boundary remains authoritative.

This audit confirms that the production gateway does not define or silently promote:

- P-Gap source geometry;
- AB=CD anchors or tolerance;
- fill semantics;
- Leg 1 = Leg 2 equality;
- unresolved pending-order lifecycle rules.

The robustness/stability evidence is not used to resolve any of those source ambiguities.

The Fresh Holdout runner likewise records that source geometry and fill semantics are unchanged and does not define unresolved AB=CD or Leg1=Leg2 from holdout observations.

### Gate

**FROZEN GEOMETRY: BLOCKED**

This remains the controlling strategy-definition gate.

## D — Fresh Holdout Interaction

Frozen boundary:

**2026-09-19 00:00:00 UTC**

Latest local availability check:

- requested through 2026-09-19 07:37:38 UTC;
- XAUUSD.ecn M1;
- 0 returned bars;
- no reported MT5 acquisition error;
- status HOLDOUT_DATA_UNAVAILABLE.

No pre-boundary data is substituted.

The Fresh Holdout remains pending rather than failed.

## Combined disposition

| Gate | Status |
|---|---|
| Source / Frozen Geometry | **BLOCKED** |
| Robustness evidence | **POSITIVE** |
| Parameter Stability | **INCONCLUSIVE — NO PASS / NO FAIL** |
| Fresh Holdout | **WAITING FOR ELIGIBLE DATA** |
| Execution infrastructure | **READY / GUARDED** |
| Strategy production authorization | **BLOCKED** |
| Live execution | **DISABLED** |

## Next valid actions

When eligible post-boundary XAUUSD.ecn M1 data exists, run the existing frozen runner without modification.

Until then:

- do not tune parameters;
- do not substitute pre-boundary data;
- do not redefine source geometry from performance;
- do not generate production Strategy A BUY/SELL decisions;
- keep `LIVE_TRADING_ENABLE=false`.

This checkpoint is a readiness audit, not a production approval.
