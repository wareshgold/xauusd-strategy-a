# SP2L Multi-Module Execution Resolution

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION  
**Status:** `BASE EXECUTION NARROWED — OPTIONAL 2X REMAINS SEPARATE`

## 1. Base target

The primary transcript explicitly distinguishes TP1 and TP2. At 42:26 the instructor says he generally uses TP1; at 42:37 he states TP2 is relatively large for this strategy because the stop is relatively large and therefore the TP should be 1 in that context.

The official SP2L page independently states default TP = 1:1 risk/reward.

**Decision:** base SP2L target is source-supported as **1R / 1:1**, subject to exact fill/SL semantics.

## 2. 2X / secondary position is a separate management module

The transcript describes an optional second position / 2X entry. It explicitly gives a different risk/reward contribution for the second position and explains that combining the first and second positions can increase aggregate return.

The official page also describes a secondary entry at 50% of the entry-to-SL distance.

**Decision:** do not fold 2X into the canonical base entry/target formula. Treat it as a separate, versioned execution-management module until its exact source geometry is frozen.

## 3. Important negative finding

The real execution table contains multiple positions with different entry/SL distances and at least one position with no displayed TP. Those examples are management demonstrations, not sufficient evidence for a universal single-position exit formula.

Therefore historical execution ratios must not be used to reverse-engineer a target rule.

## 4. Current source-aligned execution chain

The narrowest source-supported chain is:

`Spike → correction → pending Limit → structural SL → base TP1 = 1R`

with an optional separate module:

`2X / secondary position → separate sizing/entry management → aggregate outcome`

The second module must not alter the base signal decision.

## 5. Remaining unresolved execution details

- exact pending Limit price anchor;
- exact structural SL anchor at candle level;
- exact intrabar fill ordering;
- exact 2X trigger/price formula;
- exact rules for deleting/replacing a pending order;
- whether any target variant is canonical beyond base TP1.

## 6. Gate decision

**Base TP 1:1:** `SOURCE-CONFIRMED / STRONG`  
**2X exists:** `SOURCE-CONFIRMED`  
**2X exact geometry:** `UNRESOLVED`  
**2X required for base Strategy A signal:** `NO / NOT SOURCE-CONFIRMED`  
**Production change:** `NONE`

## Primary-source references

- `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt` (SHA `47f867385338738a23b2d06dc48e67b852127243`)
- Official SP2L page: `https://poursamadi.com/sp2l-strategy/`
