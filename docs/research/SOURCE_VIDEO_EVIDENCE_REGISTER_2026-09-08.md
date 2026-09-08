# SP2L Source Video Evidence Register

Date: 2026-09-08
Source: `https://youtu.be/7HEC5mO3d3U`
Branch: `research/source-aligned-sp2l-semantics-v1`

## Purpose

Record only source observations that can safely constrain the deterministic SP2L implementation. This register does not promote unresolved geometry into production.

## Direct visual observations recorded from the supplied video

### 1. SP2L naming

The teaching material explicitly presents the strategy as **SP2L / Spike - 2Leg**.

Status: SOURCE-CONFIRMED.

### 2. AB = CD

The teaching material explicitly displays **AB = CD**.

This is direct source evidence for the magnitude relationship used by the two-leg construction: the CD leg is equal in magnitude to AB for the demonstrated construction.

Status: SOURCE-CONFIRMED.

Implementation consequence: the canonical projection must measure AB from source-confirmed A/B anchors and project the same magnitude from source-confirmed C. It must not rely on a legacy `first.open -> last.close` shortcut unless that shortcut is separately source-confirmed.

### 3. Valid BO = P-Gap

The teaching material explicitly displays the relationship **Valid BO = P-Gap**.

Status: SOURCE-CONFIRMED as a semantic relationship.

Implementation consequence: a generic price-gap/imbalance detector cannot be promoted to P-GAP merely because its OHLC predicate is true. The canonical implementation must use a source-confirmed P-GAP definition and preserve the distinction between P-GAP and other gap categories.

## Still unresolved from the available visual evidence

### G4 — exact A/B geometry

The source establishes the two-leg equality relationship, but the exact chart anchors used for A and B still require coordinate-level identification before they are frozen in code.

Candidate families remain subject to source visual confirmation; no ATR, tick, percentage, or heuristic tolerance is authorized.

### G5 — exact C geometry

The source establishes that the second leg follows the correction, but the exact geometric C anchor remains unresolved. Correction extreme, structural point, and other visual candidates must not be collapsed without source evidence.

A pending-order fill price is not automatically C.

## Entry semantics

The source material demonstrates pending-limit order placement during the correction. Therefore the canonical SP2L semantic layer represents entry as a pending limit and does not use the legacy close-reclaim trigger as canonical source behavior.

## Gap taxonomy guardrail

The source distinguishes P-GAP from other gap concepts. Therefore `PGAPResearch.ts` remains a research observation and is not a canonical P-GAP implementation.

## Gate status

- Source resolution: in progress, materially strengthened by supplied video.
- Synthetic fixture discrimination: complete.
- G4: NOT FROZEN.
- G5: NOT FROZEN.
- G6: SOURCE-CONFIRMED by AB = CD.
- Canonical implementation: blocked on G4/G5.
- DEV/VAL/robustness: not started for canonical SP2L.
- Fresh Holdout: locked.
- Production: unchanged.
