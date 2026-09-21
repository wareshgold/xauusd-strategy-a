# SP2L Strategy A — Author-Site Primary Source Update: F13 / F12
## 2026-09-21

Status: RESEARCH-ONLY / SOURCE-UPDATE / NON-CANONICAL

## New source artifact

Author-controlled source:
**Mohammad Ali Poursamadi — SP2L Strategy (Spike–2Leg)**

Source:
https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

The page explicitly states that SP2L has a secondary entry and describes it as:
- a secondary entry may be added at **50% of the distance from Entry to Stop-Loss**;
- the second-leg trigger is described directionally as the corrective candle reaching the low of the previous candle in an uptrend, and the high of the previous candle in a downtrend;
- the Stop-Loss is described as being behind the candle from which the spike originated;
- the default TP is described as 1:1 risk-to-reward.

## Evidence classification

Authority: PRIMARY / AUTHOR-CONTROLLED WRITTEN MATERIAL.

This is stronger than secondary TradingFinder material and is admissible under the existing source-retrieval checklist, which explicitly permits author-controlled written material.

## F13 update

New source evidence uniquely supports the **50% Entry-to-SL secondary-entry relationship**.

Therefore:
- F13 50% price relationship: SOURCE-CONFIRMED at the concept/price-relationship level.
- F13 exact 2X execution lifecycle: still UNRESOLVED.
- F13 conditions for enabling 2X: still UNRESOLVED.
- F13 pending-vs-market semantics: still UNRESOLVED.
- F13 fill/re-entry semantics: still UNRESOLVED.
- F13 TP1/TP2 relationship: still UNRESOLVED.
- F13 shared invalidation semantics: still UNRESOLVED.

No canonical 2X execution rule is promoted by this document.

## F12 update

The author page independently states the directional trigger reference:
- bullish correction reaches previous candle Low;
- bearish correction reaches previous candle High.

This reinforces the existing source-confirmed directional reference.

It does **not** uniquely determine:
- touch vs breach vs close;
- exact candle indexing convention;
- confirmation requirements;
- precedence among one/two/three-candle variants;
- trigger vs activation vs fill semantics.

Therefore F12 remains PARTIAL / UNRESOLVED for executable canonicalization.

## F10 update

The author page repeats the structural statement that SL is placed behind the candle from which the spike originated.

It still does not uniquely specify:
- wick/body/open/close field;
- buffer;
- invalidation event semantics.

F10 remains PARTIAL / UNRESOLVED.

## Source boundary

This artifact does not promote:
- P-Gap formula/index/threshold/order-space;
- AB=CD A/B/C/D anchors or tolerance;
- bearish symmetry;
- entry field;
- pending-order timeout/replacement semantics;
- production BUY/SELL logic.

## Gate effect

- Source Resolution: PARTIAL, with F13 50%-relationship newly source-confirmed.
- Frozen Geometry: BLOCKED.
- Synthetic Fixture Gate: PASS.
- Untouched Validation: LOCKED.
- Robustness/Stability: LOCKED.
- Fresh Holdout: BLOCKED.
- Production: DISABLED.
- Forward Test: UNTOUCHED.

## Reproducibility note

The web source is an author-controlled page and was retrieved during the 2026-09-21 source audit. Search indexing currently exposes the cited statements; direct page retrieval returned a transient 404 in the web fetch layer. The source URL and exact quoted/paraphrased claims are therefore recorded for later archival verification.

## Required next action

Before any canonical F13 promotion, archive a durable copy/screenshot/PDF of the author-controlled page and reconcile it against the original training video. The exact lifecycle semantics must remain unresolved until that evidence discriminates them.
