# Phase 14 — Pre-Entry Setup Sequencing Audit

## Status

`PLAN_ONLY`

`NO_OPT`

`NO_THRESHOLD_SEARCH`

`NO_NEW_RULE`

`NO_FRESH`

`PRODUCTION_UNCHANGED`

## Objective

After Phase 12 rejected the promotion of individual reclaim/geometry features as trading rules, and Phase 13 rejected the post-entry recovery event, the next research axis returns to the canonical **pre-entry setup** without changing the detector chain.

The question is narrowly defined:

> Does the **temporal sequencing/coherence of the already-existing canonical setup components** carry reproducible information about outcome across chronological DEV/VAL windows?

This is an audit of existing setup structure, not a new entry rule.

## Why this axis is legitimate

The canonical implementation already has ordered causal components:

`Breakout → Follow-Through → Spike → Correction → Trigger/Entry`

The research has already examined several geometric magnitudes. It has not separately audited the elapsed-bar relationships between the canonical components as a single pre-entry process.

No detector semantics are changed. No new market concept is introduced.

## Canonical source semantics

The audit must use the actual detector outputs already used by the baseline reconstruction:

- breakout index from `BreakoutDetector`;
- follow-through index from `FollowThroughDetector`;
- spike start/end from `SpikeDetector`;
- correction extreme index from `CorrectionDetector`;
- trigger/entry index from `EntryTrigger`.

`EntryTrigger` is explicitly the first post-correction candle whose close reclaims the correction extreme. fileciteturn89file0L2-L2

`CorrectionDetector` defines the correction extreme as the first post-spike candle that breaches the spike start price in the opposite direction. fileciteturn91file0L2-L2

`SpikeDetector` already defines the candidate around breakout + follow-through and exposes start/end indices plus structure/overlap measures. fileciteturn90file0L2-L2

## Exact features

Only elapsed-bar quantities derived from those canonical indices may be added:

1. `breakoutToFollowThroughBars = followThroughIndex - breakoutIndex`
2. `followThroughToSpikeEndBars = spikeEndIndex - followThroughIndex`
3. `spikeToCorrectionExtremeBars = correctionExtremeIndex - spikeEndIndex`
4. `correctionExtremeToEntryBars = entryIndex - correctionExtremeIndex`
5. `totalSetupBars = entryIndex - breakoutIndex`

No thresholds are searched.

`correctionExtremeToEntryBars` is retained as an audit variable even though the canonical DELAY1 subset has historically fixed this relationship; the full canonical baseline is the population and any zero-variance result is reported rather than converted into a rule.

## Integrity requirements

For each timeframe:

- use the canonical baseline report directly;
- include every non-AMBIGUOUS, finite-R pre-holdout baseline trade with valid canonical indices;
- do not filter through DELAY1;
- do not reconstruct a different candidate universe;
- require exact entry timestamp/direction parity if replay is needed;
- report missing/unreconstructable indices explicitly;
- DEV cutoff remains `entryIndex < 6000`;
- PRE cutoff remains `entryIndex < 10000`;
- Fresh remains completely untouched.

Expected canonical 5m pre-holdout population remains 210 if the baseline is unchanged.

## Analysis layers

### Layer 1 — Continuous association

For each feature:

- Spearman correlation against canonical `rMultiple`;
- Spearman correlation against no-exceptional outcomes;
- median win-minus-loss feature delta;
- ALL / DEV / VAL separately.

This is descriptive evidence only.

### Layer 2 — Chronological replication

Use the already-established fixed chronological blocks:

- DEV_1: indices 0–1999
- DEV_2: 2000–3999
- DEV_3: 4000–5999
- VAL_1: 6000–7999
- VAL_2: 8000–9999

Do not create, merge, split, or optimize windows.

The question is whether the **sign and rough magnitude** of an association remains directionally consistent across windows.

### Layer 3 — Direction/session replication

Use the existing canonical direction/session cells only:

- BUY + LONDON
- BUY + NEW_YORK
- SELL + LONDON
- SELL + NEW_YORK

`OUT_OF_SESSION` remains descriptive and is not a candidate trading segment.

No cell is promoted because of a high observed result.

## Guardrails

- No threshold mining.
- No quantile-based entry filter.
- No best-hour selection.
- No feature combination optimization.
- No composite score.
- No new detector condition.
- No exit simulation.
- No horizon selection.
- No Fresh access.
- No production changes.

If a feature shows an attractive association, it remains descriptive until an independently specified rule can be justified and replicated.

## Stop conditions

Abort before interpretation if:

1. baseline population changes;
2. canonical component indices cannot be reproduced;
3. any future information is required;
4. a feature becomes tautological or zero-variance;
5. results require selecting a threshold/window after seeing outcomes.

## Decision criteria

### PASS — descriptive replication only
A feature may be classified as `REPRODUCIBLE_DESCRIPTIVE_ASSOCIATION` only if its association is directionally consistent across the fixed chronological windows and does not depend materially on exceptional winners.

### REJECT
If sign flips materially across DEV/VAL or windows, classify it as unstable/inconclusive and do not research thresholds.

### PROMOTION
Phase 14 itself cannot promote a trading rule. Any future rule requires a separate ex-ante hypothesis and validation plan.

## Expected output

Compact stdout:

```text
PHASE_14_SETUP_SEQUENCE N=... DEV=... VAL=... FRESH=LOCKED
INTEGRITY ...
FEATURE ... ALL ... DEV ... VAL ...
=== WINDOWS ===
...
=== SEGMENTS ===
...
STATUS=DESCRIPTIVE_ONLY NO_OPT NO_THRESHOLD_SEARCH NO_NEW_RULE NO_FRESH PRODUCTION_UNCHANGED
```

Full machine-readable reports remain under:

`data/reports/strategy-a-phase14-preentry-setup-sequencing/`

## Decision ownership

This phase is an evidence-gathering step. The assistant will decide whether any finding is robust enough to justify a **new, separately specified hypothesis**. No result is automatically converted into a trading rule.
