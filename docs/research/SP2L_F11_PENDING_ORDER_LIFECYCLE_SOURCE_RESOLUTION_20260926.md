# SP2L F11 Pending Order Lifecycle Source Resolution

Date: 2026-09-26
Status: SOURCE-PARTIAL / EXECUTABLE LIFECYCLE UNRESOLVED

## Primary evidence

The author transcript provides unusually direct lifecycle evidence around 38:38–41:18.

### 1. Pending Limit creation — SOURCE-CONFIRMED

At 38:38 the bullish correction begins when price moves below the first low; the author states that the order can be placed manually or as a predefined Limit. At 38:53–39:26 he demonstrates a Buy Limit placed within the early three-candle structure and states that the distance to SL is known before activation.

### 2. Pending order may be deleted/replaced — SOURCE-CONFIRMED

At 39:48 the author states that when another candle forms, the existing order can be deleted and a new order can be placed according to the changed distance to the stop.

This establishes **refresh/replacement as a source-supported lifecycle operation**.

### 3. Replacement is conditional, but threshold is NOT deterministic

At 40:07 the author explicitly says he sometimes does not replace the order when the changed distance is not large; instead he moves the existing order upward. If the distance is large, he places a new order with a new volume. At 40:16 he explains that the distance is generally not large enough to damage his money management.

Therefore source evidence supports:

- keep/move existing order when the structural change is small enough;
- replace order when the change is sufficiently large;
- new volume may accompany a materially changed stop distance.

The source does **not** provide a numerical threshold, pip threshold, percentage threshold, candle-count threshold, or deterministic sizing equation for this decision.

### 4. Activation/fill — SOURCE-CONFIRMED at conceptual level

At 41:18 the author states that when the next candle starts, the order is activated and there is a Buy with an SL. This supports the conceptual transition Pending Limit -> active position.

Exact broker-side fill semantics, intrabar ordering, touch/penetration semantics, spread treatment, and same-bar SL handling remain unresolved.

### 5. Invalidation/cancellation — PARTIAL

At 39:26 the author states that if price returns to the referenced invalidation area, the scenario is nullified. This establishes setup invalidation, but the transcript does not explicitly specify whether the pending order is cancelled immediately by a software rule, manually deleted, or simply considered no longer valid before activation.

Do not convert this statement into an automatic broker cancellation rule without additional source evidence.

## Source discrimination fixtures

F11-001: pending order created before activation.
Expected source property: represent Pending Limit state separately from active position.

F11-002: next candle changes stop distance slightly.
Expected source property: keep/move existing order is allowed; no numerical threshold may be invented.

F11-003: next candle changes stop distance materially.
Expected source property: replacement with new order is source-supported; new volume may accompany it.

F11-004: replacement threshold boundary.
Expected source property: fixture remains unresolved because no numeric threshold is sourced.

F11-005: price reaches invalidation before fill.
Expected source property: scenario is invalidated; exact cancellation mechanism remains unresolved.

F11-006: pending order becomes active on subsequent candle.
Expected source property: state transition to active position is source-supported; exact fill semantics remain unresolved.

F11-007: intrabar touch versus penetration.
Expected source property: unresolved broker/fill semantics.

F11-008: bearish mirror.
Expected source property: conceptual mirror is plausible, but independent source freezing is not established here.

## Canonical boundary

The following may be marked SOURCE-CONFIRMED:

- Pending Limit is a valid/source-demonstrated execution mechanism.
- Pending order can be refreshed/replaced as structure develops.
- Replacement is related to changed stop distance.
- Small versus materially changed distance can lead to different handling.
- Material replacement may involve new volume.
- Pending -> active position is a real lifecycle transition.

The following remain UNRESOLVED:

- exact entry-price anchor;
- exact invalidation/SL anchor;
- numerical replacement threshold;
- exact position-sizing formula after replacement;
- deterministic cancellation rule at invalidation;
- exact fill/touch/penetration semantics;
- spread/broker execution treatment;
- deterministic bearish lifecycle mirror.

## Gate

F11 = SOURCE-PARTIAL / EXECUTABLE LIFECYCLE UNRESOLVED.

Frozen Geometry remains BLOCKED. Untouched Validation, Fresh Holdout, and Production remain locked/off.

No canonical execution algorithm is promoted from this checkpoint.

## Reopen condition

Reopen F11 only for new primary evidence that supplies a deterministic replacement threshold, cancellation instruction, sizing equation, or explicit fill semantics.
