# SP2L Full Session Snapshot — 2026-09-17

## 0. Purpose

This is the official continuation snapshot for the XAUUSD Strategy A / SP2L (Spike → 2 Leg) research project.

It is written from the latest official checkpoint available in the repository, `SP2L_SESSION_SNAPSHOT_2026-09-16.md` (blob SHA `9c98e4f4fddb0a2040e177ec0378f33c5f855e35`), plus the verified research/engineering work completed after that checkpoint.

This snapshot is a handoff record. It does not promote unresolved research into canonical Strategy A rules.

---

## 1. Project identity and governing objective

Repository: `wareshgold/xauusd-strategy-a`

Objective: build a source-aligned, deterministic, statistically validated XAUUSD Strategy A system based on SP2L (Spike → 2 Leg).

Primary objective: prove a reproducible statistical edge before live trading.

Governance sequence:

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

Non-negotiable governance:

- source meaning outranks backtest performance;
- only source-confirmed rules may become canonical;
- unresolved geometry remains explicitly unresolved;
- no invented P-Gap formula;
- no invented AB=CD anchors/tolerance;
- no invented fill semantics;
- no invented execution rules;
- AI may assist research, engineering, validation, documentation, and analytics but does not autonomously define canonical geometry or production BUY/SELL decisions;
- production BUY/SELL generation remains OFF.

---

## 2. Official baseline used for this snapshot

The latest official checkpoint on the repository before this snapshot is:

`docs/checkpoints/SP2L_SESSION_SNAPSHOT_2026-09-16.md`

Official checkpoint blob SHA:
`9c98e4f4fddb0a2040e177ec0378f33c5f855e35`

That checkpoint recorded:

- deterministic synthetic geometry fixture implementation;
- F8–F15 fixture coverage;
- source-resolution partial pass;
- Frozen Geometry blocked;
- Untouched Validation / Robustness / Fresh Holdout locked;
- Production OFF;
- explicit prohibition on parameter optimization, profitability-based geometry selection, and invented geometry/execution semantics.

The Batch-3 checkpoint additionally recorded that P-Gap semantics, Entry-vs-Leg-2 separation, structural-invalidation-vs-risk distinction, pending-limit qualitative behavior, trigger-family concept, 2X concept, AB=CD magnitude relationship, and bearish symmetry had evidence boundaries while exact formulas/classifiers/anchors/tolerances remained unresolved.

---

## 3. Work completed after the official 2026-09-16 checkpoint

### 3.1 Timestamp basis resolution

A deterministic MT5 timestamp contract was frozen for the research environment:

- terminal/company: Otet Group MT5 / Otet Group Ltd.;
- server: `OtetGroup-MT5`;
- symbol: `XAUUSD.ecn`;
- timeframe: M1;
- canonical research time basis: UTC;
- MT5 returned `r["time"]` is treated as Unix epoch for bar open;
- conversion is `datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)`;
- no manual broker/server/local offset is applied to returned timestamps.

Current diagnostics also established raw epoch continuity and historical query-boundary behavior in the connected environment. These diagnostics are environment evidence and do not override official API semantics.

Explicitly forbidden remains any `-3h`, `+3h`, broker correction, workstation correction, or DST correction applied to canonical returned bar timestamps.

### 3.2 Session-calendar boundary

A separate MT5 session-calendar contract was established as a frozen boundary, not as a resolved historical calendar.

Source-confirmed model:

- per-symbol quote/trade schedules;
- session windows are exposed by MQL5 session APIs;
- session-time semantics are broker/server-time based;
- cross-midnight sessions must preserve their day relationship.

Current status:

`CALENDAR DATA UNRESOLVED`

Therefore:

- a missing M1 bar is not automatically a session closure;
- a price/time jump is not automatically a session boundary;
- current-day truncation is not historical calendar evidence;
- four-week CSV gaps cannot by themselves define a historical session schedule;
- no broker/server offset may be invented to fit an expected session.

Unexplained gaps remain classified as:

`UNRESOLVED_GAP`

### 3.3 Session evidence intake and validator

Added/frozen research infrastructure includes:

- `scripts/mt5_mql5_session_schedule_diagnostic.mq5`
- `scripts/validate_session_schedule_snapshot.py`
- `docs/research/MT5_SESSION_CALENDAR_EVIDENCE_INTAKE_V1.md`
- `docs/research/SESSION_CALENDAR_RESOLUTION_GATE_V1.md`
- `docs/research/SESSION_CALENDAR_SNAPSHOT_SCHEMA_V1.md`

The validator is deliberately structural. A valid current snapshot does not establish historical schedule validity, DST history, holidays, broker schedule changes, or missing-bar semantics.

### 3.4 Telegram ↔ MT5 time boundary

A frozen comparison boundary was established:

- MT5 research timestamp: UTC / Unix epoch;
- Telegram signal display: `Asia/Tehran`;
- comparison key: absolute instant / Unix epoch;
- raw Telegram timestamp must be preserved;
- MT5 data must never be shifted to align with Telegram display;
- if Telegram absolute instant cannot be established, the match remains unresolved.

### 3.5 Synthetic fixtures and geometry audit

The F8–F15 synthetic fixture layer remains research infrastructure, not canonical geometry.

Current evidence boundaries:

- F8: represented; source discrimination still required;
- F9: Entry vs Start-of-Leg-2 separation represented and retained as a source-confirmed boundary;
- F10: structural invalidation vs risk stop represented; exact semantics unresolved;
- F11: pending-limit state transition represented; replacement threshold intentionally absent;
- F12: 1/2/3-candle family represented; exact taxonomy unresolved;
- F13: competing 2X interpretations represented; canonical formula unresolved;
- F14: competing AB=CD anchors represented; tolerance and canonical anchors unresolved;
- F15: bearish mirror represented; source discrimination still required.

### 3.6 Existing backtest evidence

Existing baseline backtest results remain experimental/pre-freeze evidence.

They cannot be used to choose between unresolved geometry variants.

Metric accounting must distinguish:

- candidates;
- closed trades;
- open trades;
- ambiguous outcomes;
- tiny-risk/extreme-R observations;
- TP1/TP2/SL outcomes;
- consecutive losses;
- session-level behavior.

No backtest result in this snapshot is a canonical Strategy A performance claim.

---

## 4. Current source-resolution matrix

| Dimension | Current status | Canonical? |
|---|---|---|
| C01 P-Gap | `SOURCE_DISCRIMINATED` semantically; exact numeric formula unresolved | NO |
| C02 SL | working fixed test rule exists (50/60/70/80 pips; RR 1:2) | NO |
| C03 AB=CD / Leg-2 equality | `BLOCKED`; anchors/tolerance unresolved | NO |
| C04 TP1 / TP2 / 2X | `SOURCE_DISCRIMINATED` concept/boundary; exact execution formula unresolved | NO |
| C05 M15 / MA50 | working fixed test rule | NO |
| C06 Pending-order behavior | `SOURCE_DISCRIMINATED` qualitatively; exact refresh semantics unresolved | NO |
| C07 Trigger classifier | `BLOCKED`; exact classifier unresolved | NO |
| C08 Correction / invalidation | `BLOCKED`; exact geometry/semantics unresolved | NO |

Important: `SOURCE_DISCRIMINATED` does not mean a complete frozen numeric implementation exists. Exact unresolved geometry remains blocked.

---

## 5. Frozen / unresolved Strategy A geometry boundaries

The following remain explicitly unresolved unless and until direct source evidence discriminates them:

- exact P-Gap formula;
- HL/LH counting/classification;
- spike width/threshold;
- dirty-market / anti-channel definition and numeric threshold;
- overlap semantics;
- first important Low/High definition;
- exact trigger classifier;
- exact correction and invalidation boundary;
- Entry semantics;
- SL semantics beyond source-supported conceptual separation;
- TP1 / TP2 exact semantics;
- 2X formula;
- AB=CD anchors;
- AB=CD tolerance;
- Leg-1 min/max constraints;
- RR selection as canonical geometry;
- round-number definition;
- session windows;
- session-open gap handling;
- pending-limit refresh/replacement threshold;
- fill semantics;
- broker execution constraints as strategy rules.

No item above may be filled by inference from profitability.

---

## 6. Current MT5 acquisition evidence boundary

Canonical acquisition environment:

- `Otet Group MT5 Terminal`
- `OtetGroup-MT5`
- `XAUUSD.ecn`
- M1

Recent four-week artifact:

`artifacts/xauusd-ecn-m1-recent-4week-2026-08-21_2026-09-17.csv`

Its audit reported returned bars fewer than the full wall-clock M1 interval and several gaps/jumps. Those gaps are **not** session closures until independently resolved by historical session evidence.

The acquisition diagnostics also show current-day truncation at the time of acquisition. This is not historical calendar evidence.

---

## 7. Execution-layer status

MT5 trailing stop remains strictly optional position-management infrastructure and is separate from Strategy A geometry.

Policy:

- trailing: optional/planned capability;
- research baseline: no trailing;
- production: OFF;
- no trailing distance/activation/step has been canonically frozen;
- no broker stop/freeze formula has been invented;
- no live position modification is authorized by this snapshot.

Execution engineering must not leak unverified broker parameters into the Strategy A research baseline.

---

## 8. Statistical-validation status

The project has **not** reached an authoritative untouched-validation result.

Therefore:

- no canonical win rate is established;
- no canonical expectancy is established;
- no canonical profit factor is established;
- no canonical max drawdown is established;
- no production edge claim is established.

Any previously observed positive experimental backtest statistic remains conditional on non-frozen geometry and is not a production validation result.

Required eventual validation metrics include, at minimum:

- trade count;
- win rate;
- average R;
- expectancy;
- profit factor;
- max drawdown;
- winners/losers;
- TP1/TP2/SL outcomes;
- consecutive losses;
- session/regime breakdown;
- ambiguity and exclusion accounting.

---

## 9. Exact path from here

### Phase A — Source Resolution

1. Capture the actual MQL5 current quote/trade schedule output for `XAUUSD.ecn`.
2. Preserve raw terminal output verbatim.
3. Validate its structure with the deterministic snapshot validator.
4. Obtain historical boundary observations sufficient to distinguish regular weekly behavior, cross-midnight behavior, DST/seasonal changes, holidays/special sessions, and broker schedule changes.
5. Build reproducible expected-M1 availability evidence without labeling unexplained gaps as closures.
6. Cross-audit the acquired dataset against that evidence.

### Phase B — Synthetic Fixtures

7. Keep F8–F15 fixtures source-boundary based.
8. Add assertions that prevent fixture construction from silently becoming canonical geometry.
9. Maintain separate competing interpretations where source evidence does not discriminate.

### Phase C — Frozen Geometry

10. Only after source evidence discriminates the remaining geometry, freeze a versioned Strategy A geometry contract.
11. Record every numeric parameter and its source evidence.
12. Freeze timestamp, session, fill, trigger, invalidation, AB=CD, P-Gap, and execution semantics only where source-supported.

### Phase D — Development

13. Implement only the frozen contract.
14. Enforce no-lookahead and deterministic event ordering.
15. Keep risk/position management separate from signal geometry.

### Phase E — Untouched Validation

16. Lock the validation dataset before running the final frozen candidate.
17. Run the exact same deterministic implementation without parameter fitting.
18. Produce complete candidate/outcome/ambiguity accounting.

### Phase F — Robustness / Stability

19. Test predeclared robustness dimensions only.
20. Examine stability across time windows, session regimes, market conditions, and admissible execution assumptions.
21. Do not optimize on the robustness set.

### Phase G — Fresh Holdout

22. Freeze the complete system before touching the fresh holdout.
23. Evaluate once under the frozen protocol.
24. Preserve the holdout result as an independent evidence record.

### Phase H — Production

25. Production remains OFF until all preceding gates pass.
26. Live execution and BUY/SELL authorization are outside the current state.

---

## 10. Immediate next gate

The immediate blocker is **historical session-calendar evidence**, not another backtest optimization.

The next evidence-bearing action is to capture the real terminal-side session schedule and then perform the historical boundary-resolution work. Until that evidence exists, dataset gaps remain `UNRESOLVED_GAP` and no calendar-derived filtering is canonical.

In parallel, the deterministic fixture/test infrastructure can continue to be hardened without changing source meaning.

---

## 11. Stop conditions / prohibited shortcuts

Stop rather than infer when:

- source wording does not discriminate two geometries;
- session history cannot be established;
- fill semantics are missing;
- broker execution constraints are incomplete;
- validation requires changing a frozen parameter;
- a result depends on an undocumented assumption;
- a profitability improvement is the only reason to prefer one interpretation.

Explicitly prohibited:

- optimizing unresolved geometry against the backtest;
- converting dataset gaps into session rules without evidence;
- shifting MT5 timestamps to fit Telegram/session expectations;
- inventing AB=CD anchors or tolerance;
- inventing P-Gap formula;
- inventing fill semantics;
- inventing production execution rules;
- generating production BUY/SELL decisions.

---

## 12. Official continuation state

`SOURCE RESOLUTION = PARTIAL / ACTIVE`

`SYNTHETIC FIXTURES = PASS / ACTIVE HARDENING`

`FROZEN GEOMETRY = BLOCKED`

`DEV = LOCKED FOR CANONICAL STRATEGY`

`UNTOUCHED VALIDATION = LOCKED`

`ROBUSTNESS/STABILITY = LOCKED`

`FRESH HOLDOUT = LOCKED`

`PRODUCTION = OFF`

This snapshot is the new official handoff point for continuation.
