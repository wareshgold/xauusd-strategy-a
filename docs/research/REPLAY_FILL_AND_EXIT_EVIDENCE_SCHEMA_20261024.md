# Research-only replay fill and exit evidence contract

**Status: proposal for research instrumentation; not canonical trading rules.**  
**Scope:** Strategy B vs RR2/TRAIL4 offline replay evidence. This document records what a replay must preserve so that later audits can distinguish known, false, and unknown facts. It does not define signal geometry, entry-fill semantics, order behavior, or production execution rules.

## Non-negotiable boundaries

- Offline/research-only. No MT5 connection, order calls, forward-runner changes, or live-state edits.
- Never infer `FILLED` merely because a later candle touched SL or TP.
- Never infer `NOT_FILLED` from missing evidence. Missing evidence is `UNKNOWN`.
- A candle touching a proposed entry is an observation, not by itself proof of a broker fill. Any rule that turns candle observations into fill decisions must be separately source-confirmed or explicitly labeled a replay assumption and approved before use.
- Preserve original input bytes and SHA-256. Emit new uniquely named artifacts; do not rewrite existing evidence.
- Keep source-derived facts, replay assumptions, and unknowns separate in every row.

## Evidence record (proposed schema)

Each signal/trade candidate should carry the following fields where available. Nullable fields stay null when evidence is absent; do not synthesize values.

| Field | Type / allowed values | Meaning |
|---|---|---|
| `schema_version` | string | Version of this evidence contract. |
| `run_id` | string | Stable identifier for this replay run. |
| `candidate_id` | string | Stable ID for one signal candidate; unique within a run. |
| `signal` | object | `source_commit`, `config_sha256`, `dataset_sha256`, `symbol`, `timeframe`, `direction`, `candle_index`, `candle_time`, `entry_reference`, `sl_reference`, `tp_reference`. Keep source-provided values and derived values distinguishable. |
| `execution_model` | object | `label` (for example `source_observed`, `ohlc_proxy`, `synthetic_fixture`), `assumptions[]`, `source_evidence_refs[]`. This label does not claim parity. |
| `entry_assessment.status` | `FILLED`, `NOT_FILLED`, `UNKNOWN`, `NOT_APPLICABLE` | Epistemic status only. Use `FILLED` or `NOT_FILLED` only when the declared evidence/rule supports it. Otherwise `UNKNOWN`. `NOT_APPLICABLE` is reserved for rows that are not entry candidates. |
| `entry_assessment.evidence[]` | array of objects | Each item records `kind`, `source_ref`, `event_time`, `observed_price`, and `notes` where available. A candle touch may be recorded as evidence of a touch, not as proof of a fill. |
| `entry_assessment.rule_id` | string or null | Identifier for the separately approved fill rule/assumption used. Null when no rule is approved/applied. |
| `entry_assessment.fill_time` | timestamp or null | Actual or assumed fill time, with evidence type stated. |
| `entry_assessment.fill_price` | number or null | Actual or assumed fill price, with evidence type stated. |
| `exit_assessment.status` | `CLOSED`, `OPEN_AT_END`, `AMBIGUOUS`, `UNKNOWN`, `NOT_APPLICABLE` | Exit-evidence status. Do not call an outcome closed if entry status is unknown. |
| `exit_assessment.reason` | string or null | Evidence-backed reason, such as SL/TP/trailing/other/unknown; do not infer from an outcome label alone. |
| `exit_assessment.candle_index` / `candle_time` | integer/timestamp or null | Reference to the exact exit observation. |
| `exit_assessment.evidence[]` | array of objects | Source event/tick/order record or candle reference, with its evidence granularity stated. |
| `accounting` | object | `risk_reference`, `realized_r`, `gross_pnl`, `costs`, `net_pnl`, each nullable unless derivable from documented inputs. Include formula/version and assumptions. |
| `overlap_assessment` | object | `status`: `DETERMINABLE` or `NOT_DETERMINABLE`; `basis`; trade IDs and time/index references used. Compute overlap only for rows whose entry and exit intervals are sufficiently evidenced under the declared model. |
| `warnings[]` | array of strings | Explicit missing evidence, assumptions, timestamp limitations, or ambiguous OHLC ordering. |

### Evidence provenance

For each evidence item, preserve at least the source artifact hash and a stable row/event reference. If an exact source row or event cannot be referenced, record that limitation. UTC display alone does not prove that the original timestamp was UTC; retain the original timestamp and the declared mapping/basis separately.

Recommended provenance fields on the run manifest: replay code commit, schema version, config hash, dataset hash, exact window boundaries and boundary convention, source timezone/mapping status, symbol metadata (point/digits), and the command/environment used.

## Deterministic synthetic fixture matrix

These are contract tests for the future research replay, not claims about real fills or canonical SP2L behavior.

| Fixture ID | Setup | Required assertion |
|---|---|---|
| `FILL-01-entry-never-touched` | Candidate entry reference is never touched in subsequent synthetic candles; a later candle touches the proposed SL or TP price. No order/fill event exists. | Entry status must not become `FILLED` from the later SL/TP touch. With no approved fill rule/evidence, it remains `UNKNOWN`; no realized trade P&L is asserted. |
| `FILL-02-entry-touched-semantics-unknown` | A candle range crosses the candidate entry reference, but there is no tick/order record and no approved touch/penetration/close rule. | Record the observed touch; entry status remains `UNKNOWN`. Do not silently equate touch with fill. |
| `EXIT-03-both-levels-same-bar` | For an already-evidenced synthetic fill, one OHLC candle spans both SL and TP; no finer-grained data exists. | Exit status is `AMBIGUOUS`; no favorable path is selected. |
| `OVERLAP-04-referenced-intervals` | Two synthetic trades have evidenced entry and exit references; their intervals overlap. A control case omits one exit reference. | Overlap may be `DETERMINABLE` for the complete pair; the case with a missing interval boundary is `NOT_DETERMINABLE`. Never infer no overlap from absent exits. |
| `R-05-conditional-tpR2-accounting` | Pure arithmetic fixture only: one assumed full TP winner at +2R and one assumed full SL loser at −1R, with zero costs explicitly assumed. | Conditional sum is +1R; conditional PF is 2.0/1.0 = 2.0. Label the result conditional arithmetic, not execution-aware P&L. |

## Acceptance gates before implementation

1. Tests must prove the epistemic distinction between `UNKNOWN` and `NOT_FILLED`.
2. Tests must prove a later SL/TP touch cannot create fill evidence.
3. Tests must preserve `AMBIGUOUS` when both exit levels occur within one OHLC candle and no finer data resolves order.
4. Overlap computation must require evidenced interval boundaries and state its basis.
5. Accounting fixtures must declare their assumed TP_R and costs; they must not silently reuse the current source JSON's reported `totalR` or profit factor.
6. Tests must be deterministic and use synthetic data only. They must not import or invoke MT5, broker APIs, forward runners, or strategy signal generation.
7. Passing tests establishes contract implementation consistency only; it does not validate source fidelity, fill semantics, timestamp mapping, or profitability.

## Explicitly unresolved

This contract does not decide whether entry requires touch, penetration, close, or an execution event; how gaps/slippage/price side affect fills; whether a pending order expires; how AB=CD/P-Gap geometry is calculated; or any Strategy A canonical rule. Those remain unresolved until supported by source evidence and separately approved.
