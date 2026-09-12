# G358 — Entry / SL / TP Synthetic Discrimination

**Date:** 2026-09-12  
**Gate:** SYNTHETIC FIXTURES  
**Issue:** #91  
**Status:** RESEARCH ONLY — all interpretations remain `canonical=false`

## Purpose

G357 established that the official public page adds authoritative claims that are more concise than the original lesson. G358 creates minimal synthetic cases that keep those claims separate instead of forcing one implementation.

## Fixture matrix

| ID | Dimension | Synthetic distinction | Canonical? |
|---|---|---|---|
| ES-01 | Trigger | corrective candle touches previous low/high | false |
| ES-02 | Entry | pending-limit is placed before touch | false |
| ES-03 | Entry | pending-limit is placed at a structural correction point | false |
| ES-04 | Fill | trigger event and actual fill are separate events | false |
| ES-05 | Fill | fill occurs before the nominal geometric correction point | false |
| ES-06 | SL | structural invalidation level | false |
| ES-07 | SL | spike-origin candle boundary | false |
| ES-08 | SL | origin-candle boundary plus explicit offset | false |
| ES-09 | Secondary | no secondary entry | false |
| ES-10 | Secondary | optional 50% entry-to-SL add-on | false |
| ES-11 | TP | default public-page 1:1 outcome | false |
| ES-12 | TP | lesson TP1/TP2 + R1/R2 / AB=CD outcome | false |

## Source-discipline rules

1. A trigger condition is not automatically an entry price.
2. A pending-limit price is not automatically the geometric C point.
3. A fill event is not automatically an anchor definition.
4. Structural invalidation and spike-origin SL are represented separately until source evidence defines their exact relationship.
5. The 50% secondary entry is represented as an optional source-supported candidate, not a mandatory production rule.
6. Public-page 1:1 TP and lesson TP1/TP2/R1/R2/AB=CD are represented as competing/scope-dependent outcomes, not silently averaged or replaced.
7. No fixture may be selected as canonical by backtest performance.

## Adversarial minimal pairs

### Pair A — Trigger vs entry

Same candles; one model places a pending limit before the corrective touch, another treats the touch itself as the executable entry. The fixture exists to prevent the phrase “wait for the corrective candle to reach the previous candle low/high” from silently becoming a market-entry rule.

### Pair B — Invalidation vs origin candle

Same spike; one model invalidates on the previously identified structural level, another uses the spike-origin candle boundary. The source currently supports both concepts at different levels, but does not provide enough executable geometry to collapse them.

### Pair C — Primary vs secondary entry

Same setup; one model has only the primary entry, another adds the official-page 50% entry-to-SL secondary order. The secondary order must remain optional/research-only until its scope is source-resolved.

### Pair D — 1:1 vs AB=CD target

Same setup; one model exits at public-page default 1:1, another uses the lesson's TP1/TP2/R1/R2 and AB=CD/Leg2≈Leg1 concept. This is a semantic conflict/scope question, not a parameter-optimization question.

## Gate decision

**G358 = PASS — SYNTHETIC COVERAGE COMPLETE.**

The fixture space distinguishes the newly exposed source dimensions without choosing among them. FROZEN_GEOMETRY remains blocked until authoritative evidence supplies the missing executable semantics.
