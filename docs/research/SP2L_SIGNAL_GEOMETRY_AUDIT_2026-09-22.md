# SP2L Strategy A — Signal Geometry Audit
## 2026-09-22

Status: **RESEARCH-ONLY / CANONICAL GEOMETRY UNCHANGED**

### Scope

This audit reconciles the current author-replica `signal()` implementation with the condition diagnostics and the source-resolution state already established for Strategy A.

It does **not** promote the implementation to canonical Strategy A and does **not** authorize a new P-Gap formula, A/B/C/D anchor definition, fill-price rule, AB=CD tolerance, or execution rule.

### 1. Current executable research geometry

The current research replica evaluates four candles at positions:

- A = `c[i-4]`
- Spike = `c[i-3]`
- Correction = `c[i-2]`
- Trigger = `c[i-1]`

BUY predicate currently requires:

1. trigger low < correction low
2. correction close > spike close
3. correction open > spike open
4. spike open > A open
5. correction bullish
6. spike bullish
7. A bullish
8. correction low > A high + `P_GAP`
9. spike body > multiplier × correction body
10. spike body > multiplier × A body
11. spike body > multiplier × trigger body

SELL is the mirrored research predicate, including both spike close < A close and spike open < A open.

This is a description of the current research implementation, **not a source-confirmed canonical geometry statement**.

### 2. Reconciliation result

The first reconciliation run used a diagnostic SELL predicate that omitted the exact `signal()` SELL open-vs-A condition. BTC therefore showed:

- BUY: diagnostic 33 / exact 33 / both 33
- SELL: diagnostic 34 / exact 33 / both 33
- one diagnostic-only SELL at 2026-09-14 00:59 UTC

The diagnostic has now been corrected to include the missing SELL condition. The reconciliation tool has also been changed so that any future disagreement is treated as an engineering mismatch rather than an expected SELL exception.

EURUSD reconciliation was already exact at zero signals.

### 3. P-Gap observation

The week 2026-09-14 through 2026-09-18 showed materially different sensitivity by symbol:

- EURUSD.ecn: positive diagnostic P-Gap values eliminated all full-condition matches.
- BTCUSD.ecn: full matches changed only slightly as diagnostic P-Gap moved from 0 to 2.
- USTEC.c.ecn: full matches declined progressively as P-Gap increased, while remaining non-zero.

These observations demonstrate implementation/data sensitivity, but **do not identify the teacher's P-Gap formula**. In particular, `P_GAP=1.0` remains a research parameter/proxy and is not source-resolved by these results.

### 4. Source-alignment status

Already source-discriminated at the project level:

- SP2L is Spike → 2 Leg.
- A valid breakout is associated with P-Gap.
- P-Gap is distinct from a generic/common gap.
- AB=CD / second-leg magnitude relationship is source-confirmed.

Still unresolved for canonical executable geometry:

- exact A/B anchors;
- exact C anchor;
- exact P-Gap price-coordinate formula;
- spike grammar at candle/price-coordinate level;
- AB=CD anchors and tolerance;
- pending-limit fill semantics (fill price must not be assumed to equal C);
- exact execution semantics.

Therefore the current research `signal()` must remain a **research replica**, not the canonical Strategy A signal definition.

### 5. Decision

**No canonical geometry change is authorized from this audit.**

The evidence supports an engineering conclusion only:

> The current condition diagnostic can be made condition-exact with the research `signal()`, but condition-exactness does not establish that the research predicate is identical to the teacher's original geometry.

### 6. Next gate

Before changing P-Gap or A/B/C/D geometry, resolve the remaining source geometry from the archived visual evidence. After source resolution, freeze deterministic geometry, then run untouched validation and robustness/holdout testing.

Forward-test process and production execution are unchanged.
