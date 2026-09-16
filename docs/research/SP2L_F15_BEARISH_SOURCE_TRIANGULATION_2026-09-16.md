# SP2L F15 — Bearish Source Triangulation — 2026-09-16

## Purpose

F15 verifies that bearish geometry can be represented as the directional mirror of the bullish research fixture without silently promoting bearish rules to canonical status.

## Current fixture result

The deterministic OHLC mirror preserves directional structure:

- bullish high/low ordering maps to bearish high/low ordering;
- open/close direction is mirrored;
- the fixture remains symmetric at the representation level.

This proves fixture determinism only.

## Source boundary

Existing source triangulation confirms the bullish higher-low construction and explicitly notes that full mirrored bearish confirmation remains a blocker. Therefore F15 cannot be promoted to a source-confirmed universal bearish algorithm solely from the synthetic mirror.

## Status

- Bearish fixture determinism: `PASS`
- Bearish source geometry: `UNRESOLVED`
- Full mirrored confirmation: `REQUIRED`
- No bearish canonical OHLC rule promoted.

## Gate impact

- Source Resolution: `PARTIAL PASS`
- Synthetic Fixtures: `PASS`
- Frozen Geometry: `BLOCKED`
- Historical validation: `LOCKED`
- Production: `OFF`
