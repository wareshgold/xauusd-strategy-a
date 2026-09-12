# G349 — Official Poursamadi Web-Source Bridge Audit

Date: 2026-09-12  
Strategy: SP2L / Strategy A  
Parent: G348  
Issue: #77

## Source provenance

New external source candidates discovered after G348:

- Official Persian page: `https://poursamadi.com/sp2l-strategy/`
- Official English page: `https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/`

Both pages identify SP2L as a method introduced/taught by Mohammad Ali Poursamadi and describe the same core sequence of spike, correction/second leg, and entry level. The web source is therefore treated as a potentially authoritative extension of the source package, not as a community interpretation.

## Newly observed claims

The official web material adds several claims that were not represented as executable rules in the preserved lesson package:

1. A valid spike is described as requiring a P-Gap. The page does not define the exact P-Gap endpoints, price fields, candle count, minimum size, or overlap rule.
2. The second-leg trigger is described directionally: after an upward spike, the corrective candle reaches the prior candle's low; after a downward spike, it reaches the prior candle's high.
3. A secondary/add-on entry is described at 50% of the distance from the entry point to the stop-loss.
4. The stop-loss is described as being behind the candle from which the spike originated.
5. Default take-profit is described as 1:1 risk-to-reward.
6. Higher-volume sessions, including New York, are described as more favorable, but this is presented as contextual guidance rather than a deterministic session gate.

## Bridge against existing source evidence

### Entry / correction

The new web wording potentially strengthens a deterministic trigger candidate for the second-leg event, but it does not by itself prove that this trigger is identical to the pending-limit order placement semantics shown in the original lesson. The original lesson explicitly teaches pending-limit placement during correction. Therefore:

`SECOND_LEG_TRIGGER = newly source-supported candidate`

`PENDING_LIMIT_ENTRY = already source-confirmed`

The relationship between the trigger event and the actual pending-limit price remains a separate executable question.

### Stop-loss / origin

The web page explicitly ties the stop-loss to the candle from which the spike originated. This strengthens the existing source evidence that the deep/spike origin is structurally important. It still does not specify whether the stop uses the candle high/low wick, body boundary, close, or an offset. Wick/body semantics therefore remain unresolved.

### Take-profit

The official web page's default 1:1 statement is new evidence, but it does not automatically override the original lesson's broader discussion of R1/R2, 2X/3X reward selection, and AB=CD / Leg2≈Leg1. The correct source-first interpretation is that multiple source contexts now exist and their scope/relationship must be reconciled. No single executable TP rule is frozen at G349.

### P-Gap

The web page strengthens the proposition that P-Gap is a validity condition for the spike, but still does not supply an executable P-Gap formula. The project must continue to reject an invented generic three-candle imbalance rule unless explicit source evidence is found.

### Secondary entry

The 50% add-on rule is a newly source-confirmed textual claim from the official page. It is a candidate for deterministic implementation only after its exact meaning (50% of which entry-to-stop distance, sizing interaction, and relationship to the primary pending order) is bridged to the original lesson and covered by fixtures.

## Contradiction / scope matrix

| Dimension | Original preserved lesson | Official web source | G349 status |
| --- | --- | --- | --- |
| Spike + correction + continuation | Explicit | Explicit | Consistent |
| P-Gap required for valid spike | Explicitly associated | Explicitly required | Consistent at semantic level |
| P-Gap formula | Unresolved | Unresolved | Blocked |
| Pending-limit during correction | Explicit | Entry described more generally | Preserve pending-limit rule; bridge trigger separately |
| Spike/deep origin matters | Strongly supported | Explicit via SL origin candle | Strengthened, but OHLC field unresolved |
| Wick/body convention | Unresolved | Unresolved | Blocked |
| Second-leg trigger | Worked example / semantic | Explicit directional trigger | Newly source-supported candidate |
| Secondary 50% entry | Not executable in preserved audit | Explicit | Newly source-supported; bridge required |
| TP1/TP2 / R1/R2 | R1/R2 and 2X/3X discussed | Default TP 1:1 | Scope conflict; unresolved executable TP policy |
| AB=CD / Leg2≈Leg1 | Explicit / strong | Not supplied on page | Preserve source-confirmed geometry concept |
| Exact A/B/C/D | Unresolved | Not supplied | Blocked |
| Session preference | Contextual source material | New York described favorably | No deterministic session gate |

## What G349 does NOT establish

The web page does not resolve:

- exact A/B OHLC anchors;
- exact C price field;
- wick/body convention;
- deterministic parent/nested scale selection;
- executable D formula;
- AB=CD tolerance;
- exact relationship between pending-limit price and second-leg trigger;
- TP1/TP2 mapping to AB=CD or R1/R2;
- P-Gap construction formula.

## Required next research

Before geometry freeze, the project must obtain and preserve the full authoritative web/video material underlying these new claims, preferably including the visual examples or downloadable source document if the official site exposes them. The next synthetic fixture set should specifically discriminate:

1. corrective-candle trigger versus pending-limit placement;
2. origin-candle stop using wick versus body/close;
3. 50% secondary entry semantics;
4. default 1:1 TP versus source lesson R1/R2/AB=CD contexts;
5. whether the web page is a simplified public summary or a complete canonical rule set.

No historical optimization is authorized to choose among these interpretations.

## Gate decision

**G349 = PASS — NEW OFFICIAL SOURCE MATERIAL IDENTIFIED; SOURCE BRIDGE OPEN, GEOMETRY STILL UNRESOLVED.**

```text
SOURCE_RESOLUTION_DISCOVERY = REOPENED_FOR_NEW_OFFICIAL_SOURCE
FROZEN_GEOMETRY = BLOCKED
DEV = BLOCKED
VAL = PROTECTED
FRESH_HOLDOUT = LOCKED
PRODUCTION = BLOCKED
```
