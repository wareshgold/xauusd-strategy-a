# SP2L Entry vs Leg2 Anchor Discrimination V6 — 2026-09-09

## Scope

This pass triangulates the 45:40–46:45 and 53:10–55:25 source examples to determine whether the pending-limit Entry is identical to the start of Leg 2, the first relevant Low/High, or a later latest-swing reference.

## Evidence

### 45:55–46:36 — explicit first-pullback example

The authoritative transcript states that the teacher trades Spike in this manner and that even three-candle opportunities can occur where the next candle returns to **"this Low"** and, from the **first pullback**, price returns upward toward Leg 2. The teacher then says the objective is reaching Leg 2.

Source conclusion: the entry trigger is explicitly associated with the first pullback to a named structural Low/High, rather than a generic market-close trigger.

### 53:16–53:43 — Limit trigger and start of Leg 2

The transcript states: a one/two/three-candle structure is formed and the Limit entry trigger can be placed at the demonstrated level. Immediately afterward the teacher explains that a larger pullback can return to the **start of Leg 2**, preserving the broader leg structure.

Important distinction: the statement about returning to the start of Leg 2 is made while explaining a broader-market pullback and does not, by itself, prove that the original Limit entry price equals the start of Leg 2.

### 55:02–55:25 — explicit SL / Entry / Leg2 ordering

The teacher cleans the chart and describes a clean structural sequence, then explicitly labels separate levels as SL, Enter, and Leg 2. The direct frame at approximately 55:20 shows three vertically ordered horizontal references in a bearish example: upper SL, internal Entry, and lower continuation/Leg2 region.

Source conclusion: Entry and Leg 2 are visually distinct objects in this example. Therefore the hypothesis `Entry = Leg2 target/start` must not be frozen.

## Candidate discrimination

| Candidate | Evidence | Status |
|---|---|---|
| Entry = first/relevant prior Low/High | Strong: 38:38 and 46:15–46:36 explicitly describe correction/return to Low and first pullback | **Strong candidate** |
| Entry = latest Higher-Low/Lower-High | Visual support in 38:40–39:50, but wording across examples is not universal | **Candidate, unresolved** |
| Entry = Start of Leg 2 | 53:43 links a pullback to start of Leg 2, but 55:02–55:25 visually separates Entry and Leg 2 | **Not established; weakened** |
| Entry = fixed i-1 extreme | No source confirmation; examples do not establish universal candle index | **Rejected as canonical** |
| Entry = Fibonacci percentage | No source confirmation | **Rejected as canonical** |

## A/B/C/D implication

The source supports the semantic relationship `Leg2Magnitude approximately equals Leg1Magnitude` and names AB=CD, but the 45–55 minute examples do not establish candle-level A/B/C/D anchors. The start of Leg 2 therefore remains a structural concept distinct from the executable Entry until source geometry explicitly maps them.

## Research decision

1. Keep `Entry = relevant prior Low/High during first correction` as the leading source interpretation.
2. Keep `Entry = latest Higher-Low/Lower-High` as a competing candidate because the earlier visual sequence moves the pending line with evolving structure.
3. Do **not** equate Entry with `start of Leg 2`.
4. Do not freeze exact wick/body/tick boundary or candle index.
5. Keep structural SL independent from Entry.
6. Keep TP1/TP2/2X as separate management concepts.

## Gate impact

FROZEN GEOMETRY remains blocked. This pass reduces the candidate space but does not justify historical optimization or production implementation.

## Next highest-value source test

Find an original source frame where the Limit line, the Low/High marker, and the explicit beginning of Leg 2 are visible simultaneously at candle resolution. That single frame can discriminate the remaining Entry candidates more reliably than any historical backtest.
