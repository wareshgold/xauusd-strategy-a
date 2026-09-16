# SP2L F09/F10 Forensic Closeout — 2026-09-16

## Scope

This document closes the current source-primary forensic pass for Entry (F09) and Stop/Invalidation (F10). It records the strongest conclusions that can be made without inventing executable geometry.

## F09 — Entry anchor

### Source-supported facts

- The source describes a correction/Limit-entry sequence in the 38:38–39:26 window.
- The visual triangulation for 38:40–39:50 shows the demonstrated bullish Buy Limit reference evolving with the relevant completed higher-low while the invalidation remains deeper.
- The source distinguishes the later Leg-2 continuation objective from the entry phase.

### What this discriminates

`Entry != Leg-2 start` is a valid research distinction and must remain explicit.

A dynamic/relevant completed higher-low is strongly supported for the demonstrated bullish example.

### What it does not discriminate

The evidence does not establish a universal executable function for the Entry anchor across all Spike variants. It does not uniquely define wick/body/pivot semantics, exact candle selection, or whether the same anchor applies to bearish variants.

### Decision

`F09 = PARTIAL / CANONICAL UNRESOLVED`

The research engine may model the demonstrated bullish behavior as an evidence-backed candidate, but must not promote it to universal production geometry.

## F10 — Stop / invalidation

### Source-supported facts

- The source establishes a structural invalidation condition distinct from Entry.
- Returning to the referenced structural level invalidates the scenario.
- The visual example places the invalidation/SL reference deeper than the pending Buy Limit.
- The project geometry matrix explicitly separates structural invalidation from risk-budget position sizing.

### What this discriminates

A risk-derived distance must not be used to invent the source stop anchor. Entry and invalidation are separate variables.

### What it does not discriminate

The source evidence currently does not uniquely specify the exact OHLC point, wick/body convention, or any numeric buffer/offset.

### Decision

`F10 = PARTIAL / CANONICAL UNRESOLVED`

Represent `invalidation_anchor` explicitly as unresolved source geometry until a worked source example uniquely identifies the OHLC semantics.

## Combined F09/F10 conclusion

The forensic pass has reached a useful stopping boundary: further optimization cannot legitimately resolve these fields. The remaining ambiguity is source-definition ambiguity, not engineering ambiguity.

Therefore the fastest source-aligned path toward testing is **not** to guess the missing rules. It is to finish the minimum evidence set for F11–F14 while keeping F09/F10 unresolved, unless new primary visual/value evidence becomes available.

## Testing gate implication

Historical strategy testing remains locked because the executable geometry is not frozen. A partial research harness may be developed for source-discrimination and synthetic fixtures only; it must not be presented as canonical Strategy A performance.

## Non-negotiable exclusions

- No fixed stop distance.
- No ATR stop.
- No risk-derived stop anchor.
- No wick/body preference without source evidence.
- No universal `Entry = latest HL` rule.
- No production BUY/SELL logic.
