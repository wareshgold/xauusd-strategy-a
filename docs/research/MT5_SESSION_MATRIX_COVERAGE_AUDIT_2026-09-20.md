# MT5 Session Matrix Coverage Audit — 2026-09-20

## Status

- Session Matrix pipeline: IN_PROGRESS
- Timestamp alignment: UNRESOLVED
- Trading usage: BLOCKED

## Scope

This checkpoint records the coverage audit layer for MT5 raw session observations.

## Rules

- Use only MT5 returned timestamps.
- Do not convert timestamps to UTC without verified mapping.
- Do not infer broker sessions from missing bars.
- Do not modify Strategy A geometry or execution rules.

## Audit Outputs

Planned outputs:

- raw timestamp distribution
- weekday coverage
- hour bucket coverage using terminal time
- missing interval inventory
- confidence classification

## Gate

CURRENT_STATE: PARTIAL

The session matrix can describe observed availability but cannot establish a canonical trading session until timestamp mapping evidence is resolved.
