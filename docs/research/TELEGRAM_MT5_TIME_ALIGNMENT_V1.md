# Telegram ↔ MT5 Time Alignment v1

**Status:** FROZEN COMPARISON BOUNDARY

## Canonical representations

- MT5 bar open: Unix epoch / UTC.
- Telegram signal display: `Asia/Tehran`.
- Comparison key: absolute instant (Unix epoch), never displayed clock time alone.

## Rules

1. Preserve the raw Telegram source timestamp whenever available.
2. Establish its absolute instant from source metadata before matching.
3. Render the established instant in `Asia/Tehran` for project-facing signal records.
4. Convert MT5 raw epochs to UTC only for human-readable output; never alter the raw epoch.
5. Never add/subtract broker, server, workstation, Stockholm, or Tehran offsets from MT5 bar timestamps to force a match.
6. If the Telegram source cannot establish an absolute instant unambiguously, the match remains `UNRESOLVED`.
7. Signal-to-bar matching tolerance is intentionally unresolved here; this document does not invent one.

## Scope boundary

This document resolves representation only. It does not define signal parsing, trigger semantics, execution/fill semantics, SP2L geometry, or session calendar rules.
