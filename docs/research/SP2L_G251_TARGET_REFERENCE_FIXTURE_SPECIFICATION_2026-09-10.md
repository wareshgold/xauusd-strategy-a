# SP2L G251 — Target Reference Fixture Specification

**Date:** 2026-09-10  
**Gate:** SYNTHETIC FIXTURES  
**Status:** `PASS_RESEARCH_SPEC_ONLY__EXECUTION_MAPPING_BLOCKED`

## Purpose

Encode the G250 source-confirmed bullish TP reference geometry as deterministic research fixtures while preserving unresolved terminal TP selection and bearish mirror geometry.

## Source-confirmed reference

For the inspected bullish schematic:

- Risk = absolute Entry-to-SL distance;
- TP1 reference = Entry + 1 × Risk;
- TP2 reference = Entry + 2 × Risk.

The fixture suite does not decide whether a live/terminal TP must equal TP1 or TP2.

## Fixture coverage

- exact bullish 1R TP1;
- exact bullish 2R TP2;
- terminal TP equal to TP1;
- terminal TP equal to TP2;
- terminal TP between references;
- no terminal TP;
- bearish target mirror remains UNKNOWN until independently source-confirmed;
- absolute risk calculation independent of direction.

## Forbidden inference

The fixtures do not establish:

- terminal TP selection;
- round-level rules;
- partial exits/scaling;
- AB=CD anchor mapping;
- target tolerance;
- tick rounding;
- intrabar/close execution semantics.

## Files

- `research/fixtures/sp2l_target_reference_fixtures_g251.py`
- `research/fixtures/test_sp2l_target_reference_fixtures_g251.py`

The research CI workflow was extended to execute the new fixture test together with the existing P-Gap fixture suites.

## Gate

SYNTHETIC FIXTURES: `PASS_RESEARCH_SPEC_ONLY`  
FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`  
DEV: `BLOCKED`  
UNTOUCHED VALIDATION: `PROTECTED`  
FRESH HOLDOUT: `PROTECTED`  
PRODUCTION: `BLOCKED`
