# SP2L Source-to-Gap Traceability Map — 2026-09-20

## Purpose

For each of the four tracked source-resolution blockers (F10, F11, F12, F14),
record which archived source items were checked, what each does and does **not**
resolve, and why the blocker remains open. Produced after a full re-audit of
all `docs/research/SP2L_BATCH*.md`, the primary-source transcript, video-evidence
batches, micro-forensics, and the 2026-09-19/2026-09-20 documentation set.

**Standing rule:** a blocker closes only when a primary source uniquely
determines the executable meaning. Secondary sources, implementation formulas,
and documentation restatements are not primary evidence.

This map is documentation only. No geometry is inferred, no formula is created,
nothing is promoted to canonical.

## Traceability map

### F10 — Invalidation / Stop-loss anchor

| Source item | Authority | What it resolves | What it leaves open |
|---|---|---|---|
| Primary transcript & Batch34/35 visuals: SL behind spike-origin candle | PRIMARY | SL structural anchor concept (SOURCE-CONFIRMED); entry vs SL separated | Exact price field; invalidation event |
| Batch12 TradingFinder: SL "usually the lowest point before the sharp move" / "highest point before the sharp drop" | SECONDARY | Nothing unique — "usually" is non-deterministic; not primary | Same as above; **cannot close** |
| Batch38 author code: `BUY SL = low[-4]`, `SELL SL = high[-4]` | IMPLEMENTATION | Confirms origin-candle direction concept | Exact OHLC field, buffer, invalidation semantics per the batch's own "source confirmation still required" verdict; **cannot close** |

**Remaining gap:** no primary statement/frame uniquely defines the exact
executable SL price field (wick/body/close/open) or the invalidation event.

### F11 — Pending-order lifecycle

| Source item | Authority | What it resolves | What it leaves open |
|---|---|---|---|
| Transcript (~39:48) + Batch18/27/28/34: "existing order may be deleted and a new order placed … changed distance to the stop" | PRIMARY | Delete/replace behavior demonstrated; pending Buy Limit exists (SOURCE-CONFIRMED) | "May," not "must" — no mandatory predicate; no timeout/expiry; no replacement-price rule; no candidate precedence |
| Batch38 pending-state model in author bot | IMPLEMENTATION | Engineering state present | Canonical lifecycle still source-gated; **cannot close** |

**Remaining gap:** no primary source uniquely defines *when* deletion is
mandatory, a numeric candle/time expiry, the replacement-price construction, or
precedence among candidates.

### F12 — Trigger acceptance / precedence

| Source item | Authority | What it resolves | What it leaves open |
|---|---|---|---|
| Transcript & Batch11/16/18: bullish corrective candle reaches previous-candle low; bearish reaches previous-candle high; entry after Second-Leg trigger | PRIMARY | Directional trigger reference (SOURCE-CONFIRMED) | No candle index; no touch/wick/close activation; no precedence |
| Source-described 1/2/3-candle and Bar/Key-Bar variants | PRIMARY | Variants exist (SOURCE-CONFIRMED) | No universal classifier; no precedence rule |
| Batch38 author code: BUY `low[-1] < low[-2]`, SELL `high[-1] > high[-2]` | IMPLEMENTATION | Cross-confirms directional prior-candle concept | Is an indexing candidate, not a source rule; **cannot close** |

**Remaining gap:** no primary source uniquely defines the trigger candle index,
the activation event, or precedence among the described variants. (P-Gap
validity is a stated prerequisite whose OHLC construction is itself unresolved.)

### F14 — AB=CD anchors

| Source item | Authority | What it resolves | What it leaves open |
|---|---|---|---|
| Primary transcript: SPIKE-2LEG linked to AB=CD; "second leg expected to equal first" | PRIMARY | AB=CD concept (SOURCE-CONFIRMED); Leg2≈Leg1 magnitude (SOURCE-CONFIRMED) | No A/B/C/D endpoints; no measurement convention; no tolerance |
| Batch17 video frames 2220–2240; Batch21/22/34 visuals | PRIMARY | Direct visual confirmation of AB=CD teaching | No endpoint labels; no price field; no observed-vs-projected D |
| Batch10/12 TradingFinder: "spike = AB, continuation = CD, A near stop" | SECONDARY | Concept repeat only | Non-deterministic; **cannot close** |

**Remaining gap:** no primary source labels A/B/C/D, states which price fields
define endpoints, or gives any equality tolerance.

## Audit conclusion

A complete re-audit of the archived evidence found **no new unique primary-source
evidence** beyond what the four 2026-09-19 resolution audits already tracked.

- F10: **PARTIAL / UNRESOLVED**
- F11: **PARTIAL / UNRESOLVED**
- F12: **PARTIAL / UNRESOLVED**
- F14: **PARTIAL / UNRESOLVED**

Each blocker remains open. The only path to closure is a genuinely
discriminating primary-source artifact (labelled source frame, worked numerical
example, or direct author wording uniquely specifying the missing rule).
Secondary sources, implementation formulas, and documentation restatements do
not qualify.

## Gate rollup (unchanged)

| Gate | Status |
|---|---|
| Source Resolution | PARTIAL |
| Frozen Geometry | BLOCKED |
| Validation | PARTIAL (scope blocked) |
| Robustness / Stability | PARTIAL (descriptive only) |
| Fresh Holdout | BLOCKED |
| Production / Live | BLOCKED / DISABLED |

## Related

- [F10/F11/F12/F14 Evidence Gap Matrix](docs/research/SP2L_F10_F11_F12_F14_EVIDENCE_GAP_MATRIX_2026-09-20.md)
- [Source Discrimination Review Matrix](docs/research/SP2L_SOURCE_DISCRIMINATION_REVIEW_MATRIX_2026-09-20.md)
- [Batch12 Source Evidence F8/F10](docs/research/SP2L_BATCH12_SOURCE_EVIDENCE_F8_F10_2026-09-16.md)
- [Batch38 Author Implementation Crosswalk](docs/research/SP2L_BATCH38_AUTHOR_IMPLEMENTATION_CROSSWALK_2026-09-17.md)