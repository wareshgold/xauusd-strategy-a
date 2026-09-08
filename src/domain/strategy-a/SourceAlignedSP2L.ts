/**
 * Source-aligned SP2L semantic layer.
 *
 * This module intentionally separates source-established meaning from
 * unresolved geometry. It does NOT guess the P-GAP formula or the A/B/C
 * anchors. Those must be supplied only after source visual confirmation.
 *
 * Source facts represented here:
 * - valid breakout context is associated with P-GAP;
 * - SP2L is Spike -> 2 Leg;
 * - Leg 2 follows a correction and targets the Leg 1 magnitude;
 * - the source explicitly demonstrates AB = CD;
 * - entry may be a pre-placed pending limit order;
 * - fill price is not silently substituted for geometric C.
 */

export type SP2LSide = 'BUY' | 'SELL';

export interface SourceConfirmedGap {
  readonly kind: 'P_GAP';
  readonly startIndex: number;
  readonly endIndex: number;
}

export interface SourceConfirmedLeg1 {
  readonly startIndex: number;
  readonly endIndex: number;
  readonly startPrice: number;
  readonly endPrice: number;
}

export interface SourceConfirmedCorrection {
  readonly index: number;
  readonly price: number;
}

export interface PendingLimitEntry {
  readonly price: number;
  readonly placedBeforeFill: true;
}

export interface SourceAlignedSP2LSetup {
  readonly side: SP2LSide;
  readonly gap: SourceConfirmedGap;
  readonly leg1: SourceConfirmedLeg1;
  readonly correction: SourceConfirmedCorrection;
  readonly pendingLimit: PendingLimitEntry;
}

export interface ABEqualCDProjection {
  readonly leg1Magnitude: number;
  readonly leg2Magnitude: number;
  readonly target: number;
}

/**
 * Measure AB from source-confirmed A/B prices and project CD from the
 * source-confirmed correction point C.
 *
 * No tolerance is invented here. The caller must later validate the chosen
 * geometry against the source and any explicitly sourced tolerance.
 */
export function projectABEqualCD(setup: SourceAlignedSP2LSetup): ABEqualCDProjection {
  const leg1Magnitude = Math.abs(setup.leg1.endPrice - setup.leg1.startPrice);
  if (!Number.isFinite(leg1Magnitude) || leg1Magnitude <= 0) {
    throw new Error('SOURCE_ALIGNED_SP2L_INVALID_LEG1');
  }

  const target = setup.side === 'BUY'
    ? setup.correction.price + leg1Magnitude
    : setup.correction.price - leg1Magnitude;

  return {
    leg1Magnitude,
    leg2Magnitude: leg1Magnitude,
    target,
  };
}

/**
 * Hard guard for the old research heuristic: a generic three-candle gap is
 * not sufficient evidence to call something P-GAP.
 */
export function requireSourceConfirmedPGAP(
  gap: SourceConfirmedGap | null,
): SourceConfirmedGap {
  if (!gap || gap.kind !== 'P_GAP') {
    throw new Error('SOURCE_P_GAP_CONFIRMATION_REQUIRED');
  }
  return gap;
}

/**
 * Entry semantics are deliberately pending-limit based. A market-close
 * reclaim is not accepted as the canonical SP2L entry by this layer.
 */
export function createPendingLimitEntry(price: number): PendingLimitEntry {
  if (!Number.isFinite(price)) throw new Error('INVALID_PENDING_LIMIT_PRICE');
  return { price, placedBeforeFill: true };
}
