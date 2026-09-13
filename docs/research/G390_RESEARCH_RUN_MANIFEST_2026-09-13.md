# G390 — Research Run Manifest

Date: 2026-09-13

## Purpose

Every future research execution must identify its exact dataset, provider, timeframe, timezone, split policy and strategy version. This prevents results from becoming detached from their input provenance.

## Contract

A run manifest contains:

- unique run ID;
- dataset version;
- provider and symbol;
- timeframe and timezone;
- chronological, non-random split policy;
- strategy version;
- explicit `canonicalExecution: false` until Frozen Geometry and all promotion gates are passed.

## Current state

The contract is infrastructure-only. It does not execute Strategy A or claim an edge.

Frozen Geometry remains BLOCKED because source-confirmed executable geometry for P-Gap, A/B/C/D, entry/fill, SL and TP is still unresolved.
