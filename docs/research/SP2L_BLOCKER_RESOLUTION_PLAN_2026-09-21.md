# SP2L Blocker Resolution Plan — 2026-09-21

This is a research-control artifact, not a canonical strategy specification.

## Order
**P0:** F08 Swing → F10 Stop
**P1:** F09 Entry → F14 AB=CD → F11/F12 execution → F13 2X lifecycle
**P2:** F15 bearish independent evidence

## Rule
A blocker can move toward canonical only after source evidence discriminates the candidate field/semantics. Backtest performance cannot choose among unresolved source hypotheses.

## Required evidence
- **F08:** source-demonstrated pivot/swing selection, wick/body semantics, counterexamples.
- **F10:** exact source stop field, buffer semantics if any, touch/breach/close invalidation.
- **F09:** exact entry field, trigger precedence, pending-limit semantics.
- **F14:** A/B/C/D anchors and leg measurement; tolerance only if source-supported, otherwise explicitly unresolved.
- **F11/F12:** lifecycle and activation/fill distinction; no silent fill assumption.
- **F13:** retain only the source-confirmed Entry→SL midpoint relation until lifecycle/risk semantics are resolved.
- **F15:** independent bearish source demonstration; mirror consistency alone is insufficient.

## Gate
**Research-ready:** yes.
**Canonical-ready:** no.
**Frozen Geometry:** BLOCKED.
**Forward Test:** untouched.
**Production:** disabled.


## P0 counterexample checkpoint
Counterexample discrimination is complete for the current 14 F08/F10 cases. Only semantic narrowing was accepted; executable geometry remains unresolved.


## Execution checkpoint
F11/F12/F13 have explicit discrimination coverage. Touch is not fill; activation is not broker fill; no timeout or risk aggregation convention has been invented.
