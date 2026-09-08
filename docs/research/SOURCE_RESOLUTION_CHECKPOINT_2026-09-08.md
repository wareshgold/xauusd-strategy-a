# SP2L Source Resolution Checkpoint

Date: 2026-09-08
Branch: `research/source-aligned-sp2l-semantics-v1`

## Source inspected

Supplied video excerpt associated with the SP2L source video:
`https://youtu.be/7HEC5mO3d3U`

The locally supplied excerpt was inspected frame-by-frame across the available teaching section and later execution examples.

## Direct visual evidence

### Early teaching slide / diagram

The opening teaching material visibly contains:

- `SP2L Strategy`
- `Spike - 2Leg`
- handwritten `AB = CD`
- handwritten `1M` and `5M`
- printed `Valid BO = P-Gap`

These observations are treated as source evidence, not as inferred trading terminology.

### Approximate teaching sequence in the supplied excerpt

The excerpt spends roughly the first 35 seconds on the teaching slide/diagram. From approximately 27–35 seconds the presenter adds hand-drawn wave/leg annotations over the same diagram.

The hand-drawn sequence clearly communicates a multi-wave / two-leg construction, but the available pixels do **not** unambiguously identify numerical OHLC coordinates or uniquely label A, B, C, and D.

## Resolution outcome

### G6 — AB = CD

**RESOLVED / SOURCE-CONFIRMED.**

The relationship is explicitly written in the teaching material. The implementation may therefore preserve the equality relationship once A/B/C anchors are source-confirmed.

### P-Gap semantic relationship

**RESOLVED / SOURCE-CONFIRMED SEMANTICALLY.**

The teaching material explicitly states `Valid BO = P-Gap`.

This does not yet provide enough coordinate-level evidence to derive an OHLC formula for P-Gap. A generic three-candle imbalance remains non-canonical.

### G4 — exact A/B anchors

**NOT RESOLVED.**

The supplied teaching drawing does not provide enough unambiguous coordinate information to distinguish the candidate A/B endpoint families. No candidate is promoted.

### G5 — exact C anchor

**NOT RESOLVED.**

The supplied drawing establishes that a correction exists before the second leg, but does not unambiguously establish whether C is the correction extreme, a structural swing point, another visual anchor, or another source-defined point.

Pending-order fill price remains explicitly excluded as an automatic substitute for C.

### Spike grammar

**NOT FROZEN.**

The excerpt and source outline support the semantic concept of Spike, but the exact deterministic candle/sequence grammar is not sufficiently resolved by this excerpt alone.

## Execution examples

The later MetaTrader/order-history portion of the excerpt contains concrete entries and highlighted chart regions. These are useful execution evidence, but they are not automatically treated as geometric definitions of A/B/C/D or P-Gap.

Observed execution examples must not be reverse-engineered into canonical rules unless the source explicitly establishes the relationship.

## Gate decision

The supplied video materially strengthens source resolution but does **not** justify freezing G4, G5, or the P-Gap OHLC formula.

Therefore:

- SOURCE RESOLUTION: **progressed, not complete**
- G4: **blocked**
- G5: **blocked**
- G6: **resolved**
- P-Gap formula: **blocked**
- Synthetic fixture suite: **remain valid and research-only**
- Canonical implementation: **blocked on unresolved geometry**
- DEV: **not opened for canonical SP2L**
- VAL: **locked**
- Fresh Holdout: **untouched / locked**
- Production: **unchanged**

## Research principle

Absence of sufficient visual evidence is itself a result. This checkpoint intentionally records unresolved geometry rather than converting a plausible visual interpretation into a deterministic rule.