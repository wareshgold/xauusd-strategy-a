# SP2L Author-Site Source Retrieval Evidence — 2026-09-21

## Source

Author: Mohammad Ali Poursamadi  
Title: **SP2L Strategy (Spike–2Leg) by Mohammad Ali Poursamadi**  
URL: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

Authority class: **PRIMARY / AUTHOR-CONTROLLED**

Retrieval evidence: web search result `turn2search0`, crawled approximately 4 months before 2026-09-21.

Direct page retrieval during this audit returned HTTP 404, so this repository artifact records the retrieved source text and provenance rather than claiming a byte-identical page archive.

## Retrieved source statements

The author-controlled page states that:
- after the spike, the corrective candle reaches the previous candle's low in an uptrend and the previous candle's high in a downtrend;
- a secondary entry can be added at **50% of the distance from Entry to Stop-Loss**;
- the Stop-Loss is placed behind the candle from which the spike originated;
- default Take-Profit is 1:1 risk-to-reward.

These statements are reproduced here as a provenance record from the retrieved search result; the repository does not treat this document as a substitute for the original page artifact.

## Source-resolution effect

### F13 — 2X / secondary entry

The 50% Entry-to-SL relationship is now **SOURCE-CONFIRMED at the relationship level** by author-controlled written material.

Still unresolved:
- exact 2X order type;
- whether 2X is always enabled or conditional;
- exact activation/fill semantics;
- whether the 50% level is measured from the original Entry or a refreshed Entry;
- TP1/TP2 relationship;
- shared SL/invalidation semantics;
- replacement/update precedence.

Therefore F13 executable geometry remains **PARTIAL / UNRESOLVED**.

### F12 — trigger reference

The author-controlled page confirms:
- bullish: corrective candle reaches previous-candle Low;
- bearish: corrective candle reaches previous-candle High.

Still unresolved:
- touch vs breach vs close;
- exact indexing convention;
- confirmation requirement;
- precedence among trigger variants;
- trigger vs activation vs fill.

Therefore F12 remains **PARTIAL / UNRESOLVED**.

### F10 — stop anchor

The author-controlled page confirms the structural concept that SL is behind the spike-origin candle.

Still unresolved:
- wick/body/open/close field;
- buffer;
- invalidation event semantics.

Therefore F10 remains **PARTIAL / UNRESOLVED**.

## Canonical boundary

This evidence does NOT authorize promotion of:
- a P-Gap formula or indexing;
- AB=CD A/B/C/D anchors or tolerance;
- universal bullish/bearish symmetry;
- entry field/update precedence;
- pending-order timeout/replacement;
- production BUY/SELL decisions.

## Gate status

- Source Resolution: PARTIAL
- F13 50% relationship: SOURCE-CONFIRMED
- F13 executable lifecycle: UNRESOLVED
- F12 executable semantics: UNRESOLVED
- F10 executable semantics: UNRESOLVED
- Frozen Geometry: BLOCKED
- Synthetic Fixture Gate: PASS
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: BLOCKED
- Production: DISABLED
- Forward Test: UNTOUCHED
