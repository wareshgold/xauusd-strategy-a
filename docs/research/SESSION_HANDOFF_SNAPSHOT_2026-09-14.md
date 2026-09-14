# SP2L Session Handoff Snapshot — 2026-09-14

## Purpose

This snapshot preserves the state of the current working session so the next ChatGPT conversation can resume without reconstructing the research history from scratch.

It is a research/governance handoff artifact. It does not canonicalize Strategy A geometry, authorize production trading, or replace manual approval by Ali.

## Project

Repository: `wareshgold/xauusd-strategy-a`

Objective: build a source-aligned, deterministic, statistically validated XAUUSD Strategy A system based on SP2L (Spike → 2 Leg), proving a reproducible statistical edge before live trading.

Core gate order:

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

## Current session focus

The session concentrated on preserving continuity, inspecting the user-supplied authoritative SP2L source video directly, adjudicating F8–F15, and refusing to convert visual ambiguity into invented executable rules.

The important working principle reaffirmed in this session is:

`Source meaning > backtest performance.`

If the source does not uniquely discriminate a rule, the correct state is unresolved/blocked—not parameter optimization and not profitability-driven selection.

## Direct source video artifact

User-supplied MP4:
`strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

- Duration: `01:09:15.721723`
- Video: H.264, `640x360`, `30 fps`
- Audio: AAC, `44.1 kHz`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

The video was directly frame-inspected rather than relying only on web/index descriptions.

## Direct visual evidence examined

### 36:58–37:22 — P-Gap / AB=CD

The teaching diagram visibly contains the explicit labels `Valid BO = P-Gap` and `AB=CD` beside the directional construction.

Established:
- P-Gap is explicitly associated with a valid breakout.
- AB=CD is explicitly presented as a source relationship.

Not established:
- exact P-Gap candle indices;
- exact P-Gap OHLC boundaries;
- exact A/B/C/D anchors;
- equality tolerance.

Disposition: semantic association source-discriminated; executable geometry remains unresolved.

### 38:35–39:55 — bullish Entry / SL / Buy Limit

The teaching sequence shows several low references, changing horizontal levels, an explicit `Buy Limit` / `BuyLimit` annotation, and a distinct lower level labelled `SL`.

Established:
- Pending Limit execution is directly supported.
- Entry and SL are separate levels.
- The construction is a correction-order model rather than a market-close-reclaim replacement.

Not established:
- universal `Entry = latest HL` rule;
- exact Entry OHLC anchor;
- wick/body semantics;
- exact structural invalidation OHLC boundary;
- deterministic pending-order retain/replace threshold.

### 1:02:40–1:03:32 — bearish structure

A bearish directional sequence with lower-high/lower-low structure and correction is directly visible.

Established:
- bearish directional structure exists in the source.

Not established:
- complete deterministic mirrored executable geometry;
- exact bearish A/B endpoint geometry.

### 1:04:00–1:04:40 — bearish order / continuation

A bearish chart sequence shows an order/reference marker around a corrective lower-high region followed by continuation lower.

Established:
- bearish order-before-continuation concept is directly observed.

Not established:
- exact bearish Entry price;
- exact bearish invalidation/SL OHLC boundary;
- exact bearish P-Gap formula;
- exact bearish AB=CD endpoints/tolerance.

## F8–F15 adjudication after direct-video inspection

| Fixture | Current result | Canonical geometry unlocked? |
|---|---|---|
| F8 — Entry correction level | `SOURCE-DOES-NOT-DISCRIMINATE` | No |
| F9 — Entry vs Leg-2 start | Separation retained; exact anchor unresolved | No |
| F10 — Invalidation vs risk stop | Structural separation confirmed; OHLC unresolved | No |
| F11 — Pending refresh | Structure-dependent update supported; threshold unresolved | No |
| F12 — Trigger family | 1/2/3-candle family confirmed; exact classifier unresolved | No |
| F13 — 2X / TP1 / TP2 | Unresolved | No |
| F14 — AB=CD | Leg2 magnitude approximately Leg1 supported; anchors/tolerance unresolved | No |
| F15 — Bearish mirror | Bearish order/continuation observed; deterministic mirror blocked | No |

## Source-resolution conclusions carried forward

### Confirmed / strongly supported

- SP2L means Spike → 2 Leg.
- Spike is directional price movement.
- Breakout/follow-through matter.
- P-Gap is a source concept associated with valid breakout.
- Pending Limit execution is source-supported.
- Entry is distinct from Leg-2 start.
- Entry is distinct from structural invalidation/SL.
- Structural invalidation is distinct from risk-budget sizing.
- Leg 2 is a separate continuation objective.
- `Leg2Magnitude ≈ Leg1Magnitude` is the safe AB=CD interpretation.
- 1-, 2-, and 3-candle trigger family is source-supported.
- Bullish and bearish order/continuation examples are directly visible in the source video.

### Still blocked / unresolved

1. Exact P-Gap OHLC/candle-index formula and variant invariants.
2. Exact universal Entry price anchor / relevant Low-High algorithm.
3. Exact spike-origin structural invalidation OHLC boundary and wick/body semantics.
4. Deterministic pending-limit retain/replace condition.
5. Exact 1/2/3-candle trigger classifier.
6. Exact 2X / TP1 / TP2 executable formulas.
7. Exact AB=CD A/B/C/D anchors and equality tolerance.
8. Deterministic bearish mirror across all executable dimensions.

## Governance decisions preserved

- No P-Gap formula is invented.
- No A/B/C/D anchors or AB=CD tolerance is invented.
- No Entry/SL buffer or wick/body convention is invented.
- No pending-order replacement threshold is invented.
- No fill semantics are invented.
- No market-close-reclaim rule is substituted for Pending Limit.
- No historical profitability is used to choose source meaning.
- No unresolved geometry is promoted to canonical.
- Canonical promotion requires explicit manual approval by Ali.
- AI may research, engineer infrastructure, document, validate, and analyze, but may not autonomously canonicalize Strategy A geometry or generate production BUY/SELL decisions.

## Replay / Backtest foundation status

Deterministic infrastructure is separate from Strategy A geometry and remains valid as strategy-agnostic research infrastructure.

Replay/Backtest Audit is formally `AUDIT-CLOSED` for infrastructure/governance only.

The audit closure explicitly does NOT mean:
- Strategy A geometry is canonical;
- the strategy is profitable;
- validation is ready;
- Fresh Holdout is ready;
- production is ready.

Known unresolved semantics remain outside the frozen infrastructure boundary.

## Important GitHub artifacts

### Active foundation PR

PR #126 — `feat: isolated deterministic engine foundation`

- Open, not merged.
- Foundation-only.
- Branch: `dev/deterministic-engine-foundation-clean-2026-09-14`
- Latest known foundation branch commit before later research work: `2ba192865a29cc6722ccc28097ffc4ec2af5e715`
- Foundation CI and Scope Guard were green at the audited foundation checkpoint.
- Do not merge automatically.

### Active source checkpoint PR

PR #147 — `research: establish finite SP2L source-resolution stop condition`

- Open, not merged.
- Branch: `research/sp2l-source-resolution-stop-condition-2026-09-14`
- Commit: `b52fc6bc98c349bdaf6049b1d1284f5decd9b2`
- Purpose: finite stop condition for the current source-resolution pass.
- All eight executable geometry blockers remain protected by the stop condition.
- Do not merge automatically.

### Active direct-video evidence PR

PR #149 — `research: record direct SP2L source-video frame extraction`

- Open, not merged.
- Branch: `research/sp2l-video-source-extraction-2026-09-14`
- Current branch head after this session's evidence commits: `f9e947a8350f1e4e716096a9002696e847b68fad`
- Direct video extraction and F8–F15 adjudication are recorded here.
- No engine changes.
- No canonical promotion.
- No backtest-driven geometry selection.

The branch also contains the direct evidence records and the session handoff snapshot.

## Authoritative blocker

Issue #146 — `Research blocker: authoritative source evidence needed for remaining SP2L executable geometry`

Current state: `EVIDENCE WAITING`.

The issue remains the authoritative blocker. A new source-resolution pass should only begin when genuinely new Tier-1/Tier-2 evidence can uniquely discriminate a remaining executable dimension.

## Historical / governance records

- Replay/Backtest Audit evidence matrix: `AUDIT-CLOSED`.
- Replay/Backtest closure record: `AUDIT-CLOSED`.
- Official snapshot: `snapshot/replay-backtest-audit-2026-09-14` at commit `70682823bd6915a8302d31680a453611240d67be`; do not modify/delete.
- Issue #127 records source authority, canonicalization governance, replay audit scope, and branch-retention governance.
- PR #148 governance audit was closed without merge.
- Superseded research PRs were closed without merge to preserve provenance; no unsupported deletion should be inferred.

## Current gate state

```text
Foundation / Infrastructure   🟢 GREEN
Replay Audit                  🟢 CLOSED
Source-video evidence         🟢 CAPTURED
F8–F15 adjudication           🟢 DOCUMENTED
Issue #146                    🟡 EVIDENCE WAITING

Source Resolution             🟡 EVIDENCE BOUNDARY
Synthetic Fixtures            🟢 DEFINED / ADJUDICATED
Frozen Geometry               🔴 BLOCKED
DEV                           🔒 LOCKED
Untouched Validation          🔒 LOCKED
Robustness / Stability        🔒 LOCKED
Fresh Holdout                 🔒 LOCKED
Production                    🔒 LOCKED
```

## Exact next step for the next chat

Resume from this snapshot—not from an invented new geometry hypothesis.

Priority:

1. Continue direct source-video extraction only where it can genuinely discriminate a blocker, with exact timestamp/frame provenance.
2. First focus on the detailed `38:35–39:55` bullish teaching sequence for F8/F10/F11 if additional frames can reveal an actual unambiguous executable anchor or order-refresh rule.
3. Then inspect `36:58–37:22` for any additional P-Gap/AB=CD evidence that can uniquely expose candle indexing or anchors.
4. Use `1:02:40–1:04:40` for bearish mirror evidence.
5. If no unique executable rule emerges, record `SOURCE-DOES-NOT-DISCRIMINATE` or `BLOCKED` and stop source-resolution churn.
6. Do not modify the Strategy A engine until geometry is source-resolved and manually approved.
7. Do not enter historical DEV/Validation/Fresh Holdout merely because the research has become cleaner.

## Handoff rule

The next chat should treat this file, the current geometry ledger, Issue #146, and the active PRs as the continuity baseline. The direct source-video SHA is the provenance anchor for the visual evidence reviewed in this session.
