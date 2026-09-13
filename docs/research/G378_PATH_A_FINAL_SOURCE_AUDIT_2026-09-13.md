# G378 — Path A Final Authoritative-Source Audit

Date: 2026-09-13  
Gate: SOURCE RESOLUTION  
Scope: final targeted acquisition before closing the current geometry cycle

## Objective

Complete Path A using only authoritative SP2L source material and determine whether the remaining executable geometry can be frozen without invention.

## Primary-source corpus checked

1. Official SP2L page by Mohammad Ali Poursamadi (English and Persian versions).
2. Official SP2L YouTube video `7HEC5mO3d3U`, represented in the preserved local source video and transcript.
3. Preserved source transcript `POORSAMADI_SP2L_SOURCE.txt` / project copy of the transcript.
4. Explicitly annotated source frames extracted from the SP2L video.
5. Earlier source-resolution records G353–G377.
6. Official Poursamadi course index was checked for potentially relevant additional modules. The public index exposes course/module titles (including Gaps, Protective Stops, and advanced Spike Trading), but does not expose the protected lesson artifacts or executable SP2L annotations needed to promote missing geometry.

Third-party indicator pages were also checked as research leads only. Their formulas were **not** treated as authoritative evidence and were not promoted.

## New direct visual evidence from the preserved SP2L video

### Entry / pending-limit sequence

The source sequence around 38:38–39:48 is stronger than a generic textual description:

- the speaker states that when the next candle begins the correction, correction means price comes below the first low;
- he explicitly says the order can be placed manually or as a pre-set limit;
- he then demonstrates a Buy Limit on the chart;
- he explains that the order can be placed within the first three candles rather than waiting for another candle;
- he distinguishes the pending order from later activation and states that the distance to SL is known before activation;
- if price returns to the invalidation area, the scenario is cancelled.

This resolves the **mechanism**: correction-based pending-limit entry is canonical semantic evidence. It does **not** resolve a universal numerical limit-price formula or exchange/broker fill semantics.

### Leg / AB=CD sequence

The source around 36:59–37:22 explicitly shows `AB=CD` and `Valid BO = P-Gap`.

The source around 1:02:41–1:04:32 explicitly distinguishes:

- a first leg and a second leg;
- a nested 2Leg contained inside a larger leg;
- a deeper correction producing another larger-scale leg;
- an order being moved until activation;
- the first leg being described as “from here to here” on the chart.

The visual chart is sufficient to confirm that the teacher selects structural locations on the chart, but the source does not provide universal machine-readable rules identifying those locations as a particular OHLC field or a universal A/B selector.

Therefore **AB=CD remains source-confirmed semantically, but A/B/C/D executable anchors remain unresolved**.

### Stop-loss sequence

The official SP2L page explicitly states that SL is placed behind the candle from which the Spike originated. The video also demonstrates structural invalidation. Neither source fixes whether “behind” means the wick extreme, body boundary, open/close boundary, or an offset beyond one of those levels.

Therefore the structural reference is frozen but the numerical boundary remains unresolved.

### Target sequence

The video explicitly discusses TP1/TP2 and R-style reward outcomes and gives 2X/3X examples. The official page separately states a default 1:1 TP. The source corpus does not state a deterministic priority/mapping between these target descriptions.

Therefore no fixed 1R, 2R, 3R, or AB=CD target formula is promoted.

### P-Gap

The video and gap lesson establish P-Gap as Pressure Gap and distinguish it from other gap classes. The source repeatedly emphasizes context/location. No authoritative artifact defines the exact P-Gap candle endpoints, wick/body treatment, overlap condition, or minimum size.

The generic gap formula demonstrated elsewhere in the gap lesson is therefore not promoted to P-Gap.

### Secondary 50% entry

The official SP2L page explicitly describes a secondary entry at 50% of the entry-to-SL distance. The video also discusses additional position management. The source corpus does not clearly establish that the 50% add-on is mandatory core setup logic for every canonical signal.

It remains a source-confirmed optional/additional mechanism, not a mandatory canonical signal component.

## Path A conclusion

**No new authoritative artifact resolves the remaining executable geometry.**

The final status is therefore:

**SOURCE RESOLUTION = COMPLETE FOR THE CURRENT PRIMARY CORPUS**  
**FROZEN GEOMETRY = BLOCKED**

This is a source-completeness decision, not a claim that the strategy is impossible to formalize. It means the missing definitions are not recoverable from the currently available authoritative artifacts without introducing researcher-defined geometry.

## Canonical promotion guard

The following remain explicitly prohibited:

- generic three-candle gap formula → P-Gap;
- third-party indicator geometry → canonical Strategy A;
- chart-pixel measurement → OHLC rule;
- invented A/B/C/D anchors;
- parent/nested scale selection by backtest performance;
- fill price = C by assumption;
- invented SL offsets/tolerances;
- fixed 2R/3R target;
- MA60/M1/M5/session/candle-count hard filters without source evidence.

## Gate consequence

Do not enter canonical DEV/VAL or production from the current corpus.

The only permissible next research layer is the explicitly non-canonical hypothesis layer, where competing executable interpretations may be tested and compared while preserving `canonical=false` and source provenance.

If a new primary artifact becomes available later (for example an annotated lesson/video not present in the current corpus), SOURCE RESOLUTION may be reopened and this decision revisited.
