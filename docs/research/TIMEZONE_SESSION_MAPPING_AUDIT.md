# Timezone / Session Mapping Audit

**Date:** 2026-09-06
**Branch:** `research/ny-sell-preentry-temporal-replication`
**Status:** VERIFIED — frozen for future research

---

## 1. Dataset Timezone

**TIMEZONE = UTC**

### Evidence

| Source | Evidence |
|--------|----------|
| `scripts/download-xauusd.mjs` | `const timezone = process.env.XAUUSD_TIMEZONE ?? 'UTC'` — Twelve Data API receives `timezone=UTC` |
| `data/historical/xauusd-5min.json` | Metadata field: `"timezone": "UTC"` |
| `data/historical/xauusd-1min.json` | Metadata field: `"timezone": "UTC"` |
| Twelve Data API | Returns timestamps in the requested timezone; UTC was requested |

### Dataset span

- First candle: `2026-07-12 05:30:00` UTC
- Last candle: `2026-09-02 07:25:00` UTC
- Total: 15,000 candles (5min)

---

## 2. Candle Timestamp Semantics

Historical candle timestamps represent **candle OPEN time**.

The Twelve Data API `datetime` field is the candle open timestamp. The download script passes it directly:

```javascript
timestamp: v.datetime
```

No transformation is applied.

---

## 3. Session Classification Implementation

### Code location

`src/domain/strategy-a/Context.ts` — `buildSessionContext()` function.

### Mechanism

```typescript
function minutesOfDay(timestamp: string): number {
  const d = new Date(timestamp);
  return d.getUTCHours() * 60 + d.getUTCMinutes();
}
```

Uses `getUTCHours()` — **explicitly UTC-based**. No IANA timezone lookup.

### Session configuration

`scripts/run-baseline-backtest.ts`:

```typescript
tradingSessions: [
  { name: 'LONDON', startMinutes: 7 * 60, endMinutes: 16 * 60 },    // 420–960
  { name: 'NEW_YORK', startMinutes: 16 * 60, endMinutes: 22 * 60 }, // 960–1320
],
```

### First-match behavior

`buildSessionContext` uses `Array.find()`, which returns the **first** matching session. The session array order determines precedence when windows overlap.

For the current configuration:
1. LONDON (07:00–16:00 UTC) — checked first
2. NEW_YORK (16:00–22:00 UTC) — checked second

Because LONDON's end (16:00) equals NEW_YORK's start (16:00), there is no overlap. The `find()` first-match behavior has no effect on the boundary — both sessions produce clean, non-overlapping windows.

---

## 4. Effective Session Mapping

| Session | Start (inclusive) | End (exclusive) | UTC hours |
|---------|------------------|-----------------|-----------|
| LONDON | 07:00 UTC | 16:00 UTC | 07–15 |
| NEW_YORK | 16:00 UTC | 22:00 UTC | 16–21 |
| OUTSIDE | — | — | 00–06, 22–23 |

### Reconstruction rule

```
if (utcHour >= 7 && utcHour < 16) → LONDON
if (utcHour >= 16 && utcHour < 22) → NEW_YORK
else → OUTSIDE
```

### Verification

348/348 resolved baseline trades reconstructed with **0 mismatches** using the rule above.

---

## 5. Trigger Timestamp Semantics

Session labels are assigned to the **trigger candle's open timestamp** in the baseline backtest:

```typescript
const session = buildSessionContext(trigger.timestamp, CONTEXT);
```

`trigger.timestamp` = candle's `timestamp` field from the historical dataset = candle OPEN time in UTC.

---

## 6. DST Handling

**No DST handling is implemented.** Session boundaries are fixed UTC integer offsets.

### Current dataset DST status

| Transition | Date | In dataset? |
|-----------|------|-------------|
| US DST start | March 8, 2026 | No (dataset starts July 12) |
| UK DST start | March 29, 2026 | No |
| UK DST end | October 25, 2026 | No (dataset ends September 2) |
| US DST end | November 1, 2026 | No |

**DST_IN_CURRENT_DATA = NONE**

The entire dataset (July 12 – September 2, 2026) falls within the Northern Hemisphere summer DST period. Both New York (EDT, UTC-4) and London (BST, UTC+1) are on summer time for the full duration.

### Future risk

If the dataset is extended to span March or October/November, DST transitions would shift real-world session boundaries. The fixed UTC offsets would no longer align with actual market sessions. A separate DST audit would be required before any time-window research on extended data.

---

## 7. Poorsamadi Time Window Mapping

The Poorsamadi source material uses broker/chart time, approximately aligned with Istanbul time (UTC+3 in summer, UTC+2 in winter).

**For the current summer dataset:** Poorsamadi clock time → UTC = subtract 3 hours.

Example: Poorsamadi `16:30–18:00` → UTC `13:30–15:00`.

**POORSAMADI_TIMEZONE = REQUIRES_SOURCE_VERIFICATION**

This UTC+3 assumption is based on the source transcript's statements about broker time alignment. It has not been independently verified against the repository's data pipeline. The Poorsamadi timezone must be confirmed from source evidence before any time-window interaction research proceeds.

---

## 8. Repository Files Inspected

| File | Relevance |
|------|-----------|
| `src/domain/strategy-a/Context.ts` | Session classification logic (`buildSessionContext`, `minutesOfDay`) |
| `scripts/run-baseline-backtest.ts` | Session configuration (tradingSessions array), baseline decision function |
| `scripts/download-xauusd.mjs` | Data source, timezone parameter, timestamp handling |
| `data/historical/xauusd-5min.json` | Dataset metadata (timezone field), timestamp format |
| `scripts/analyze-ny-sell-expanded-anatomy.mjs` | Hardcoded `isNySell` filter (16:00–22:00 UTC) |
| `scripts/analyze-ny-sell-correction-path-geometry-v3.mjs` | Hardcoded `isNySell` filter (16:00–22:00 UTC) |
| `scripts/analyze-ny-sell-trigger-process-features.mjs` | Hardcoded `isNySell` filter (16:00–22:00 UTC) |
| `scripts/analyze-feature-generalization-across-segments.mjs` | Uses baseline session labels directly |
| `docs/strategy/STRATEGY_A_POORSAMADI_TIME_ANALYSIS_RESEARCH_V1_2026-09-05.md` | Poorsamadi time window source analysis |

---

## 9. Implications for Future Research

### Time-window interaction research

With verified UTC session boundaries, Poorsamadi time windows can be mapped to UTC and joined to baseline trades by trigger timestamp. The mapping is deterministic and auditable.

### What can be tested

- Whether Poorsamadi time windows (mapped to UTC) show stable performance variation across DEV/VAL
- Whether existing geometry features interact with time-window classification
- Whether time-window classification adds information beyond session classification

### What cannot be tested yet

- DST-dependent session behavior (dataset has no DST transitions)
- Poorsamadi time-point effects (requires source timezone verification)
- Cross-DST seasonal patterns (requires extended dataset)

---

## 10. Discrepancy History

The previous code in `run-baseline-backtest.ts` contained:

```typescript
{ name: 'NEW_YORK', startMinutes: 13 * 60, endMinutes: 22 * 60 }
```

This was misleading because LONDON (07:00–16:00) always captured 13:00–15:59 via `find()` first-match precedence. The effective NEW_YORK start was always 16:00 UTC.

This has been corrected to `16 * 60` for code clarity. The behavioral change is zero — the effective session classification is identical before and after the fix.

---

## 11. Frozen Reference

This document freezes the verified timezone/session semantics for the current dataset. Any future changes to session boundaries, timezone handling, or dataset scope require a new audit.
