# SP2L G255 — AB=CD Visual Cross-Reference

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `ABCD_RELATION_CONFIRMED__ANCHORS_UNRESOLVED`

## Source pass

Frame-by-frame review of the source sequence around 36:20–37:25 confirms that the teacher explicitly writes and repeats `AB=CD` over the SP2L schematic. The annotation is directed toward the price-move construction, and later frames add distance-style notes while the same schematic remains visible.

This strengthens the existing conclusion that AB=CD is a source-defined relationship, not a backtest-derived hypothesis.

## What the frames do not uniquely establish

The source sequence does not label four chart coordinates as A, B, C and D. It therefore does not uniquely establish:

- A = spike origin;
- B = spike endpoint;
- C = correction endpoint or Entry;
- D = terminal TP;
- wick versus body versus close anchors;
- whether equality is exact or approximate;
- any tolerance;
- any rounding convention;
- whether AB=CD defines a target, a diagnostic relationship, or both.

The handwritten distance notes are evidence that measured distances are discussed, but they are not sufficient to assign those measurements to a unique A/B/C/D coordinate mapping.

## Decision

Freeze only the semantic relationship `AB = CD`. Keep all executable anchor mappings and tolerance rules unresolved. Do not implement an AB=CD target projection yet.

### Gates

- SOURCE RESOLUTION: `PASS_PARTIAL`
- AB=CD semantic: `FROZEN`
- AB=CD executable anchors: `BLOCKED`
- FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`
- DEV: `BLOCKED`
- VALIDATION: `PROTECTED`
- PRODUCTION: `BLOCKED`
