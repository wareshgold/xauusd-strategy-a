# SP2L Source-Resolution Batch — SL / Pending Refresh — 2026-09-14

## Scope

This document advances the next two source-resolution dimensions after P-Gap and Entry: structural invalidation / stop boundary and pending-order refresh.

It is a research evidence artifact only. It does not define canonical executable geometry.

## Governance

Source meaning outranks implementation convenience, backtest performance, and optimization.

No rule is promoted to `CANONICAL` here. Manual approval by Ali remains mandatory.

No engine changes are authorized by this pass.

---

## A. Structural Invalidation / SL

### Source-discriminated semantics

The source consistently separates:

`Entry ≠ Structural Invalidation ≠ Risk-Budget Position Sizing`

The demonstrated ordering is structurally consistent with:

`SL / invalidation → Entry → Leg 2`

The source also supports Spike-origin / base-structure semantics for invalidation. Therefore a stop must not be selected from a risk percentage, ATR distance, fixed pip distance, or arbitrary offset from Entry.

### Executable geometry still unresolved

The available evidence does not uniquely determine:

1. universal Spike-origin candle index;
2. exact OHLC field used for the boundary;
3. wick versus body semantics;
4. exact stop boundary versus any source-defined buffer;
5. spread/execution adjustment;
6. universal bullish/bearish application.

The phrase `behind the candle` is source-relevant semantics, not a deterministic formula.

### Adjudication

`SOURCE-DISCRIMINATED` at semantic level.

`SOURCE-DOES-NOT-DISCRIMINATE` at executable OHLC level.

### Negative controls

Do not canonicalize:

- `stop = Entry ± N`;
- ATR/fixed-pip stops;
- risk-derived stop prices;
- wick-only/body-only rules inferred from pixels;
- arbitrary buffers;
- generic swing algorithms substituted for Spike-origin geometry;
- assumed bearish sign-flip symmetry.

### Fixture consequence

F10 remains required as a discrimination fixture, but its correct status is unresolved at executable OHLC level unless a new authoritative source explicitly selects one candidate.

---

## B. Pending-Order Refresh

### Source-discriminated semantics

The source confirms correction entry through a pending Limit and permits order management to respond when new structure develops before fill. Evidence demonstrates that an earlier pending order may be deleted and a new order placed when the structure/distance changes.

The source also discriminates against replacing the pending-limit model with market-close/reclaim entry.

### Executable refresh rule still unresolved

The evidence does not uniquely select among:

- retaining the original order;
- replacing on every new relevant structural swing;
- replacing only under a qualitative/material-distance condition.

No numerical pip/tick/ATR/percentage threshold is source-confirmed.

### Adjudication

`SOURCE-DOES-NOT-DISCRIMINATE` at deterministic retain/replace level.

Market-entry replacement is rejected as a substitution for the source-confirmed pending-Limit model.

### Negative controls

Do not invent:

- fixed replacement thresholds;
- ATR/percentage thresholds;
- mandatory replacement on every swing;
- fixed candle-count refresh rules;
- market-entry-on-close replacement;
- universal bearish mirror.

---

## Combined gate impact

| Dimension | Semantic status | Executable status |
|---|---|---|
| P-Gap | RESOLVED as Pressure Gap category | BLOCKED / source does not discriminate formula |
| Entry | Pending Limit; distinct from Leg-2 start and invalidation | BLOCKED / exact anchor unresolved |
| SL / invalidation | Spike-origin/base structural concept | BLOCKED / exact OHLC unresolved |
| Pending refresh | Refresh behavior source-supported | BLOCKED / retain-replace condition unresolved |

### Research gate

- SOURCE RESOLUTION: **IN PROGRESS**
- SYNTHETIC FIXTURES: **DEFINED / ADJUDICATION CONTINUES**
- FROZEN GEOMETRY: **BLOCKED**
- DEV: **LOCKED for Strategy A geometry**
- UNTOUCHED VALIDATION: **LOCKED**
- ROBUSTNESS/STABILITY: **LOCKED**
- FRESH HOLDOUT: **LOCKED**
- PRODUCTION: **LOCKED**

## Next priority

Continue with:

1. F12 trigger classifier;
2. F13 2X / TP1 / TP2;
3. F14 AB=CD anchors/tolerance;
4. F15 bearish mirror.

Each dimension must end as exactly one of:

`SOURCE-DISCRIMINATED`, `SOURCE-DOES-NOT-DISCRIMINATE`, `BLOCKED`, `REJECTED` with source-based reason.

If source evidence cannot uniquely determine executable geometry, the result remains unresolved. No backtest result may break the tie.
