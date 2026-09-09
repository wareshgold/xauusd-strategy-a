# SP2L G35 — Synthetic Execution Contract

Date: 2026-09-09

## Purpose

G35 establishes a strategy-neutral execution harness for synthetic OHLC fixtures. It exists so execution mechanics can be tested independently of unresolved Strategy A geometry.

## Determinism boundary

OHLC bars do not uniquely reveal the intrabar path when multiple executable levels are touched. Therefore the runner has three explicit policies:

- `UNRESOLVED`: a touched pending LIMIT produces an ambiguity event and no fabricated fill/outcome.
- `OHLC_PATH`: explicit synthetic path Open → High → Low → Close.
- `OLHC_PATH`: explicit synthetic path Open → Low → High → Close.

The two path policies are research fixtures, not claims about the real XAUUSD feed.

## Lifecycle

Pending LIMIT → Fill → optional Stop/Target exit.

Expiry is deterministic by bar age when configured. The post-fill path begins at the fill level, preventing a pre-fill price excursion from being incorrectly counted as a post-fill exit.

## Same-bar conflicts

A fixture may legitimately produce different outcomes under different explicit intrabar policies. This is intentional: it demonstrates why production backtests must have a documented feed/execution convention rather than silently choosing an OHLC ordering.

## Scope restrictions

This module does not detect Strategy A setups and does not choose P-Gap, Entry, SL, Trigger, AB=CD, Leg2, TP1, or any other unresolved geometry. It cannot advance FROZEN GEOMETRY or downstream validation gates by itself.

## Test status

Fixture coverage includes unresolved touch, fill→target, fill→stop, path-dependent same-bar outcome, and deterministic expiry.
