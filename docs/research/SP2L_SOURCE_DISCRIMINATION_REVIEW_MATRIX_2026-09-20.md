# SP2L Source Discrimination Review Matrix — 2026-09-20

## Purpose

Feature-by-feature review of the four tracked source-resolution blockers
**F10 / F11 / F12 / F14**, based exclusively on the source discrimination
audits already archived in `docs/research/`.

This matrix records what the source confirms, what it does not confirm, the
blocking item, and the evidence required to close each blocker.

It does **not**:
- infer missing geometry;
- create formulas;
- promote any candidate to canonical;
- change any code.

STATUS is restricted to the existing discrimination vocabulary:
**SOURCE-CONFIRMED · SOURCE-SUPPORTED · PARTIAL / UNRESOLVED · UNRESOLVED**.

Sources reviewed (all 2026-09-19 resolution audits):
- F10 — `SP2L_F10_INVALIDATION_SL_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`
- F11 — `SP2L_F11_PENDING_ORDER_LIFECYCLE_RESOLUTION_AUDIT_2026-09-19.md`
- F12 — `SP2L_F12_TRIGGER_ACCEPTANCE_PRECEDENCE_RESOLUTION_AUDIT_2026-09-19.md`
- F14 — `SP2L_F14_ABCD_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`
- Status/pack: `SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md`, `SP2L_SOURCE_DISCRIMINATION_PACK_F10_F11_F12_F14_2026-09-19.md`, `SP2L_F10_F11_F12_F14_SOURCE_PASS_INDEX_2026-09-19.md`

---

## Review matrix

| Feature | Current evidence | Current status | What is confirmed | What is not confirmed | Blocking item | Required evidence to close |
|---|---|---|---|---|---|---|
| **F10 — Invalidation / SL anchor** | Source transcript + Batch34/35 visuals: SL placed behind the candle from which the spike originated; separate Buy Limit vs SL levels; return toward referenced level invalidates setup | **PARTIAL / UNRESOLVED** | SL is tied to spike-origin candle (SOURCE-CONFIRMED); entry and SL are separate levels (SOURCE-CONFIRMED); return through structure invalidates setup (SOURCE-SUPPORTED) | Exact bullish SL price field; exact bearish SL price field; wick vs body; buffer/offset; touch vs penetration vs close; bid/ask & spread/slippage semantics | No source statement of the exact executable price field / invalidation event for the SL anchor | A primary statement or frame that uniquely defines the OHLC field behind the spike-origin candle (and its bearish mirror), plus buffer/touch/close semantics |
| **F11 — Pending-order lifecycle** | Transcript ~39:48: when a subsequent candle forms, the existing order may be deleted and a new order placed based on changed distance to stop; Batch34 records a delete annotation | **PARTIAL / UNRESOLVED** | Pending Buy Limit can exist (SOURCE-CONFIRMED); existing order may be deleted (SOURCE-CONFIRMED); replacement/new order may follow (SOURCE-CONFIRMED) | Exact mandatory deletion predicate; numeric candle/time timeout; exact replacement condition; replacement-price construction; multi-candidate precedence; fill/activation semantics | No unique observable event that makes deletion/re-placement mandatory; no deterministic state machine | A primary statement/frames uniquely defining when deletion is mandatory (candle-count, time, new-candidate, or stop-distance), the replacement-price rule, and precedence among candidates |
| **F12 — Trigger acceptance / precedence** | Directional trigger concept: bullish corrective candle reaches previous-candle low; bearish reaches previous-candle high; entry after Second-Leg trigger in spike direction; source also describes 1/2/3-candle and bar/key-bar variants | **PARTIAL / UNRESOLVED** | Second-Leg trigger part of SP2L (SOURCE-CONFIRMED); bullish prev-candle-low reference (SOURCE-CONFIRMED); bearish prev-candle-high reference (SOURCE-CONFIRMED); entry follows trigger in spike direction (SOURCE-CONFIRMED); 1/2/3-candle and bar/key-bar variants source-described (SOURCE-CONFIRMED) | Exact candle-index classifier; exact touch/wick/close activation; variant precedence; universal pending-order vs later-confirmation choice; broker bid/ask/fill semantics | No unique trigger-acceptance classifier or precedence among the 1/2/3-candle / bar / key-bar variants; P-Gap predicate (prerequisite) also unresolved | A primary statement/frames uniquely fixing the trigger index, activation event (touch/wick/close), and a precedence or selection rule among variants |
| **F14 — AB=CD anchors** | Primary transcript names SPIKE-2LEG and links two-leg concept to AB=CD; "second leg expected to equal first leg"; Batch34 records direct AB=CD visual evidence with multiple local structural points but no A/B/C/D labels | **PARTIAL / UNRESOLVED** | AB=CD is explicitly part of SP2L (SOURCE-CONFIRMED); Leg-2 ≈ Leg-1 magnitude relationship (SOURCE-CONFIRMED) | All four A/B/C/D endpoint identities; endpoint price semantics (wick/body/OHLC); observed-D vs projected-D; local swing/pivot definition; how competing points resolve; any numerical tolerance | No deterministic mapping of the four endpoints and no measurement/tolerance rule | A primary statement/frames uniquely identifying A, B, C, D (and any pivot definition), the endpoint price field, whether D is projected or observed, and the tolerance rule |

---

## Cross-cutting dependency

P-Gap remains the highest-severity unresolved geometry item overall. F12's
conceptual chain depends on a "valid P-Gap/breakout" prerequisite whose exact
OHLC construction is **UNRESOLVED**. No F-level blocker can be promoted to
canonical executable geometry while P-Gap's formula/candle-boundary semantics
remain open.

## Gate rollup (unchanged)

| Gate | Status |
|---|---|
| Source Resolution | **PARTIAL** |
| Frozen Geometry | **BLOCKED** |
| Production / Live | BLOCKED / DISABLED |

All four blockers remain **PARTIAL / UNRESOLVED**. No evidence in the archived
audits uniquely closes any of them; each row above states the exact evidence
that would.

## Related

- [Source Discrimination Status](docs/research/SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md)
- [Source Discrimination Pack F10/F11/F12/F14](docs/research/SP2L_SOURCE_DISCRIMINATION_PACK_F10_F11_F12_F14_2026-09-19.md)
- [Gate Status Dashboard](docs/research/SP2L_RESEARCH_GATE_STATUS_2026-09-20.md)