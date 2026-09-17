# SP2L Batch 34 — Source Matrix Addendum — 2026-09-17

## Scope

Delta to the F8–F16 source-resolution matrix from the fine-grained forensic inspection of the primary SP2L training sequence at approximately 36:30–44:30.

| Fixture | Batch 34 delta | Canonical rule | Freeze impact |
|---|---|---|---|
| F8 | Multiple local lower points are visibly marked before the Buy Limit step; structural relevance strengthened, selection algorithm still absent | No | BLOCKED |
| F9 | Buy Limit is explicitly labelled; separate SL reference is shown; exact price construction and activation/fill remain absent | No | BLOCKED |
| F10 | Entry/order level and SL are visibly separated in the teaching diagram; exact SL boundary/invalidation absent | No | BLOCKED |
| F11 | Pending-level persistence and explicit `delete` are visible; deletion predicate and replacement/refresh causality absent | No | BLOCKED |
| F12 | `Valid BO = P-Gap` is explicit and BO→Buy Limit ordering is visible; exact touch/wick/close/next-bar taxonomy absent | No | BLOCKED |
| F13 | `2X` is explicitly demonstrated and visually placed as a distinct deeper level; numeric formula/sizing absent | No | BLOCKED |
| F14 | `AB=CD` is explicitly written in the teaching sequence; A/B/C/D anchors and tolerance absent | No | BLOCKED |
| F15 | No new deterministic bearish mirror evidence in this predominantly bullish sequence | No | BLOCKED |
| F16 | `Round level` plus 250/500/1000 point examples are visibly taught; exact interval/rounding algorithm absent | No | BLOCKED |

## Strongest source-supported chain

`AB=CD concept → Valid BO = P-Gap → structural/local points → Buy Limit → separate SL reference → delete/order management → 2X concept → Round Level examples`

This chain is **concept/source-supported but not executable-rule-complete**.

## Explicit non-inferences

No canonical P-Gap formula, swing-selection algorithm, entry price construction, fill trigger, SL formula, delete/replace rule, 2X=50% formula, AB=CD tolerance, or universal Round Level interval is promoted.

## Gate

**Source Resolution: PARTIAL PASS**

**Frozen Geometry: BLOCKED**

**Untouched Validation: LOCKED**

**Robustness/Stability: LOCKED**

**Fresh Holdout: LOCKED**

**Production: OFF**

**125R: UNTOUCHED**
