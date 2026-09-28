# SP2L Strategy A — Source Boundary / Frozen Geometry Gap Register

Date: 2026-09-28
Branch: research/sp2l-clean-forward-xau-eurusd-usdjpy-20260928
Status: RESEARCH / NOT CANONICAL

## Purpose

This register separates source-confirmed meaning from implementation-era predicates and unresolved geometry. Backtest performance does not promote any item to canonical status.

## Source-confirmed boundaries

| ID | Evidence | Status | Canonical implication |
|---|---|---|---|
| F12 | BUY retraces to previous candle Low; SELL retraces to previous candle High | Source-aligned | Directional trigger location is source-aligned; touch/penetration/close semantics remain unresolved |
| F13 | Secondary 2X entry is 50% of Entry–SL distance | Source-confirmed | 2X construction is eligible for canonical specification once Entry/SL semantics are frozen |
| F10 | SL behind candle where Spike started | Source-confirmed concept | Exact anchor semantics (wick/body/open/close/buffer) remain unresolved |
| C01 | P.GAP is distinct from Common GAP; valid BO is P-Gap | Source-discriminated | P-Gap concept is valid; numeric threshold/formula remains unresolved |
| C02 | Historical source says SL 50–80 pips and RR 1:2 | Source evidence | Numeric meaning/pip convention and exact execution semantics require source resolution before canonicalization |
| C03 | No Leg1=Leg2 confirmation | Source-confirmed | Do not add Leg1=Leg2 equality/confirmation |
| C04 | Pending template includes SL / Entry / TP1 / TP2 + “2x” | Source evidence | Template structure is retained; exact fill/execution semantics remain unresolved |
| C05 | 15m MA50 | Source evidence | Retained as source evidence; exact role/filter semantics require resolution |
| C06 | Delete unfilled Buy Limit within 1–2 candles | Candidate/source evidence | Timing rule remains unresolved until exact source wording is verified |

## Current parity findings — diagnostic only

The 2026-08-26 through 2026-09-25 XAU parity run used one common MT5 dataset and found 167 common signals, 1 Old-only, and 46 Current-only. Diagnostic integrity mismatches were zero.

The 46 Current-only windows fail one or more historical Old predicates. The observed failure families include P-Gap, trigger inequalities, spike-body magnitude comparisons, spike/A open relationships, and A candle direction. These counts describe implementation divergence only; they do not establish that any of those predicates are source rules.

The common-signal counterfactual matrix also shows that changing SL anchor and outcome semantics materially changes research results. This is diagnostic evidence only and does not resolve source semantics.

## Frozen-geometry blockers

1. Exact P-Gap formula and numeric threshold.
2. Exact meaning of F12 trigger: touch vs penetration vs close.
3. Exact F10 SL anchor: wick/body/open/close and any buffer.
4. Exact pending-order fill semantics and bar ordering.
5. Exact AB=CD anchors/tolerance, if AB=CD is required by the source.
6. Exact spike magnitude definition and numeric threshold, including whether the historical 1.5 multiplier is source-confirmed.
7. Exact candle-role relationships that appear in the old candidate but lack source confirmation.
8. Exact interpretation of C02 50–80 pips and RR 1:2 under the applicable instrument convention.

## Explicit non-promotions

The following must NOT be promoted to canonical rules from this register or from the parity/backtest results:

- old candidate geometry;
- shared-detector geometry;
- P-Gap = 1.0 price units;
- spike multiplier = 1.5;
- SL = 10.0 price units;
- any 20/30/40/50 pip sensitivity result;
- old API outcome semantics;
- pending-fill semantics;
- Old SL anchor = A candle low/high;
- Current SL anchor = Spike candle low/high.

## Next source-resolution inputs

The next research action is source retrieval/resolution for the blockers above. Until resolved, Frozen Geometry remains BLOCKED and the active forward configuration remains untouched.
