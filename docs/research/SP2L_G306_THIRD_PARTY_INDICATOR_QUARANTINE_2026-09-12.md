# SP2L G306 — Third-Party Indicator Geometry Quarantine

**Date:** 2026-09-12  
**Status:** `NON_AUTHORITATIVE_LEADS_QUARANTINED`

## Findings

Third-party TradingFinder material describes executable SP2L-like geometry including three-candle spike patterns, breakout entry, origin-based SL, 1:1 TP, and AB=CD language.

These materials are useful as research leads, but they are not authoritative source material from the creator and contain details that are not established by the official source ledger.

Examples of third-party-only details that must not become canonical without creator-source confirmation:

- exact three-candle detector;
- 65% body/range threshold;
- fixed Spike Size threshold;
- M1/M5 restriction;
- exact breakout candle boundary;
- exact AB/CD implementation;
- exact TP formula.

## Decision

Third-party implementations may be used only to generate candidate hypotheses for later source testing.

They cannot resolve an unresolved source geometry question and cannot override contradictions between official textual material and primary-video evidence.

`THIRD_PARTY_GEOMETRY = QUARANTINED`

`CANONICAL_RULE_PROMOTION = PROHIBITED`
