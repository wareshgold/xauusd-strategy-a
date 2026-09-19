# SP2L F13 — 2X Lifecycle Source Resolution Audit — 2026-09-19

## Purpose
Source-first audit of the SP2L 2X concept and its executable lifecycle. No backtest, parameter search, implementation convenience, or chart convention is used to resolve ambiguity.

## Evidence reviewed
- `docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `docs/research/SP2L_BATCH34_PRIMARY_SEQUENCE_GEOMETRY_FORENSIC_2026-09-17.md`
- `docs/research/SP2L_BATCH35_OFFICIAL_SOURCE_PGAP_2X_RESOLUTION_2026-09-17.md`
- `docs/research/SP2L_F13_F14_SOURCE_DISCRIMINATION_2026-09-16.md`
- `docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md`

## Source-confirmed findings

1. 2X is a distinct second-position concept in the teaching material.
2. The source describes 2X as an optional secondary position in at least one teaching context.
3. Author-associated source text explicitly describes the secondary entry at 50% of the distance from the entry point to the stop-loss.
4. The source explains that the later secondary entry can improve average entry/risk characteristics and can have a different R outcome because it is farther along the move toward the target.
5. Primary artifacts visibly distinguish the 2X level from the initial Buy/Entry level and SL reference.

## Still unresolved

- Whether every SP2L setup must use 2X or whether it is always optional.
- Exact reference point for the 50% measurement when the initial entry is pending, filled, partially filled, or refreshed.
- Exact price construction and rounding/tick handling.
- Position sizing of the secondary order.
- Whether 2X is a pending order, immediate entry, or confirmation-dependent action in every context.
- What happens if the first entry never fills.
- What happens if the order is refreshed before 2X activation.
- Fill/touch/wick/close semantics and Bid/Ask execution semantics.
- Whether the 2X level changes after entry/SL refresh.
- Exit/lifecycle interaction with TP1/TP2 and Round Level.
- Whether the label “2X” denotes size, position number, entry level, or a combined teaching notation in every diagram.

## Non-inferences

Do not canonicalize:
- `2X = Entry + 0.5*(SL-Entry)` as a universal executable equation without resolving direction/reference semantics.
- Any fixed lot multiplier such as 2x size.
- Any mandatory 2X rule.
- Any fill semantics.
- Any TP/exit behavior inferred from a chart drawing.
- Any broker-specific rounding or execution behavior.

## Gate impact

**F13: PARTIAL / UNRESOLVED.**

The 50%-of-entry-to-SL relation is source-confirmed at concept level, but complete lifecycle semantics are not source-complete.

**Frozen Geometry remains BLOCKED.**

No backtest or robustness run is justified by this audit.

## Highest-value next evidence

A source artifact that explicitly maps the 2X line to a price equation, reference state, sizing, and lifecycle (including what occurs when the initial entry is unfilled or refreshed) would close the remaining F13 blockers.
