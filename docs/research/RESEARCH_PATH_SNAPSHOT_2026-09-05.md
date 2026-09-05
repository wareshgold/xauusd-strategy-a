# XAUUSD Strategy A — Research Path Snapshot

Date: 2026-09-05
Branch: `research/strategy-a-poorsamadi-geometry`

## Objective

Build a statistically validated, deterministic XAUUSD price-action system by progressively reconciling Strategy A with the Poorsamadi SP2L source material and validating every candidate rule on chronological out-of-sample data.

The goal is **not** to turn the videos directly into trading rules. The videos are semantic/source evidence; executable rules must be explicitly defined and then validated.

## Source Layers

We now have three complementary Poorsamadi source layers:

1. **SP2L main lesson** — core price-action lifecycle and SPIKE-2LEG concepts.
2. **Gap Effects lesson** — pressure-gap vs exhaustion-gap interpretation and contextual use of gaps.
3. **Time Analysis lesson** — time windows/time points, broker/chart time, session/opening behavior, and temporal context.

Raw source files are preserved under `docs/strategy/source/`.

## Integrated Conceptual Model

The working research model is:

`TIME / SESSION CONTEXT`
→ `LOCATION / LEVEL`
→ `RANGE / CONTEXT`
→ `BREAKOUT`
→ `FOLLOW-THROUGH / PRESSURE`
→ `SPIKE FAMILY`
→ `STRUCTURAL LOW/HIGH`
→ `CORRECTION`
→ `PENDING LIMIT / ENTRY`
→ `FIXED STRUCTURAL STOP`
→ `LEG2 ≈ LEG1`
→ `TP1`
→ optional `2X / extended management`

Gap behavior is treated as a contextual classifier within the strong-move/spike family until its exact executable geometry is fully specified.

Time is treated as a context/state variable, not automatically as a hard entry filter. The research must determine whether time improves entry selection, setup quality, management, or only describes regime behavior.

## What Is Source-Established vs TBD

### Source-established at conceptual level

- Breakout is based on price closing beyond a relevant prior level.
- Follow-through/strong continuation matters after the breakout.
- SP2L means SPIKE-2LEG: after a spike and correction, the second leg is expected to approximate the first leg.
- Pending/limit entry can be placed around the structural correction level before the setup fully completes, provided the known structure and risk remain acceptable.
- Stop is tied to structural invalidation.
- Location and market context matter; SP2L is not intended to be applied blindly everywhere.
- Pressure gaps and exhaustion gaps have different contextual roles.
- Time of day/session and market opening behavior matter.
- Broker/chart time must be distinguished from arbitrary UTC assumptions.

### Still TBD / must be researched

- Exact spike geometry and numeric thresholds.
- Exact P-GAP geometry, size, body/wick measurement and overlap tolerance.
- Exact exhaustion-gap algorithm and reversal/exit trigger.
- Exact time windows in the canonical XAUUSD data timezone.
- Exact session/opening rules and seasonal/DST handling.
- Exact entry placement and tolerance.
- Exact structural stop/touch-vs-close invalidation semantics.
- Exact Leg1 measurement and Leg2 tolerance.
- Exact 2X trigger and management rules.

## Current Research Discipline

- Do not modify production Strategy A from exploratory evidence alone.
- Use DEV for hypothesis discovery/fitting, VAL for chronological OOS validation, and fresh holdout only after replication survives.
- Do not optimize thresholds on VAL or fresh holdout.
- Preserve raw source transcripts unchanged.
- Separate source facts, source examples, implementation assumptions, and research hypotheses.
- Handle same-candle ambiguity conservatively.
- No hindsight leakage.
- Any promoted rule must survive chronological validation and fresh holdout.

## Existing Research Findings That Remain Relevant

The recent nested post-entry path study found that the first post-entry MAE state (`T1`) contains robust information about final outcome, while later cumulative states did not show robust incremental information. However, the extreme T1 state was found to be overwhelmingly a same-bar stop state and therefore was **not** accepted as an actionable post-entry management rule. The next productive direction is to investigate **pre-entry predictors** of adverse early-path states.

This is important because the integrated SP2L + Gap + Time research may provide exactly the kind of pre-entry context needed to distinguish cleaner opportunities before entry rather than attempting to repair bad entries afterward.

## Immediate Next Research Track

### Time Window Research V1

1. Verify the timezone and timestamp semantics of the canonical XAUUSD historical data.
2. Translate the Time Analysis source's windows/time points into deterministic timestamp partitions without assuming they are canonical yet.
3. Join those partitions to the canonical Strategy A baseline.
4. Measure N, win rate, total/mean R, PF, drawdown, max consecutive losses, and average R by time window.
5. Split BUY/SELL and, where useful, volatility/regime strata.
6. Test interactions between time context and SP2L structural quality/gap evidence.
7. Replicate surviving hypotheses on VAL before any fresh-holdout test.
8. Only then consider a candidate rule.

## Architectural Direction

Long-term deterministic pipeline remains:

`Reliable XAUUSD Market Data`
→ `Deterministic Strategy Engine`
→ `Risk / Signal Engine`
→ `Webhook/API`
→ `Cloudflare Worker`
→ `Telegram Channel/Bot`

AI may later explain signals, summarize research, and support analytics, but must not arbitrarily generate BUY/SELL decisions.

## Checkpoint

This snapshot marks the point where the research program moves from studying SP2L geometry alone toward **integrating three semantic dimensions — SP2L structure, gap behavior, and time context — while keeping executable rule promotion strictly evidence-driven**.

No production strategy rule is promoted by this snapshot.
