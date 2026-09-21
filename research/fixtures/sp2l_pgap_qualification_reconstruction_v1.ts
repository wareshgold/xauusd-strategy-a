/**
 * Research-only P-Gap qualification candidates reconstructed from source wording.
 *
 * This module intentionally exposes source-shaped predicates separately:
 * 1) breakout + follow-through + later P-Gap;
 * 2) higher-lows + later P-Gap;
 * 3) immediate post-low behavior described by the teacher.
 *
 * No candle count, index precedence, minimum gap size, or E-Gap cutoff is frozen.
 */

import type { PgapCandle } from "./sp2l_pgap_source_reconstruction_v1.js";
import { bullishGapPrimitive, bearishGapPrimitive } from "./sp2l_pgap_source_reconstruction_v1.js";

export interface PgapQualificationObservation {
  direction: "bullish" | "bearish";
  breakoutObserved: boolean;
  followThroughObserved: boolean;
  higherLowsObserved: boolean;
  gapObserved: boolean;
  gapPair: readonly [number, number] | null;
  sourceVariant:
    | "breakout-follow-through-gap"
    | "higher-lows-gap"
    | "immediate-post-low"
    | "unresolved";
  canonicalEligible: false;
}

export function bullishBreakoutAbovePreviousHigh(
  previous: PgapCandle,
  breakout: PgapCandle,
): boolean {
  return breakout.close > previous.high;
}

export function bearishBreakoutBelowPreviousLow(
  previous: PgapCandle,
  breakout: PgapCandle,
): boolean {
  return breakout.close < previous.low;
}

export function bullishHigherLowSequence(
  candles: readonly PgapCandle[],
): boolean {
  if (candles.length < 2) return false;
  for (let i = 1; i < candles.length; i += 1) {
    if (candles[i]!.low <= candles[i - 1]!.low) return false;
  }
  return true;
}

export function bearishLowerHighSequence(
  candles: readonly PgapCandle[],
): boolean {
  if (candles.length < 2) return false;
  for (let i = 1; i < candles.length; i += 1) {
    if (candles[i]!.high >= candles[i - 1]!.high) return false;
  }
  return true;
}

export function observeBullishPgapVariants(
  candles: readonly PgapCandle[],
  gapPair: readonly [number, number],
): PgapQualificationObservation {
  const [a, b] = gapPair;
  const gapObserved = a >= 0 && b < candles.length &&
    bullishGapPrimitive(candles[a]!, candles[b]!);

  const breakoutObserved = candles.length >= 2 &&
    bullishBreakoutAbovePreviousHigh(candles[0]!, candles[1]!);

  const followThroughObserved = candles.length >= 3 &&
    candles[2]!.close > candles[1]!.close;

  const higherLowsObserved = bullishHigherLowSequence(
    candles.slice(0, Math.min(candles.length, 3)),
  );

  let sourceVariant: PgapQualificationObservation["sourceVariant"] = "unresolved";
  if (breakoutObserved && followThroughObserved && gapObserved) {
    sourceVariant = "breakout-follow-through-gap";
  } else if (higherLowsObserved && gapObserved) {
    sourceVariant = "higher-lows-gap";
  }

  return {
    direction: "bullish",
    breakoutObserved,
    followThroughObserved,
    higherLowsObserved,
    gapObserved,
    gapPair: gapObserved ? gapPair : null,
    sourceVariant,
    canonicalEligible: false,
  };
}

export function observeBearishGapPrimitive(
  previous: PgapCandle,
  current: PgapCandle,
): boolean {
  return bearishGapPrimitive(previous, current);
}

export type PgapTimingObservation =
  | "early-trend"
  | "repeated-extension"
  | "unresolved";

export interface PgapEGAPComparison {
  gapObserved: boolean;
  priorExtensionCount: number;
  timing: PgapTimingObservation;
  executableQualification: "UNRESOLVED";
  canonicalEligible: false;
}

/**
 * Source-aligned observation only:
 * the transcript distinguishes an early/quick opportunity from repeated
 * extensions where a gap is considered likely E-Gap and entry is avoided.
 *
 * The extension cutoff is intentionally NOT frozen.
 */
export function observePgapTiming(
  gapObserved: boolean,
  priorExtensionCount: number,
): PgapEGAPComparison {
  let timing: PgapTimingObservation = "unresolved";
  if (gapObserved && priorExtensionCount === 0) timing = "early-trend";
  else if (gapObserved && priorExtensionCount >= 1) timing = "repeated-extension";

  return {
    gapObserved,
    priorExtensionCount,
    timing,
    executableQualification: "UNRESOLVED",
    canonicalEligible: false,
  };
}

export interface BreakoutFollowThroughObservation {
  breakoutCloseBeyondPreviousRange: boolean;
  followThroughDoesNotReturn: boolean;
  sourceBreakoutObserved: boolean;
  canonicalEligible: false;
}

/**
 * Source-shaped breakout observation.
 * The preserved transcript describes breakout as a candle close followed by
 * a next candle that cannot return/overlap the breakout area.
 * Exact return boundary and indexing remain unresolved.
 */
export function observeBreakoutFollowThrough(
  previous: PgapCandle,
  breakout: PgapCandle,
  followThrough: PgapCandle,
): BreakoutFollowThroughObservation {
  const breakoutCloseBeyondPreviousRange =
    breakout.close > previous.high || breakout.close < previous.low;

  const bullishFollowThrough = breakout.close > previous.high &&
    followThrough.low > previous.high;
  const bearishFollowThrough = breakout.close < previous.low &&
    followThrough.high < previous.low;

  const followThroughDoesNotReturn =
    bullishFollowThrough || bearishFollowThrough;

  return {
    breakoutCloseBeyondPreviousRange,
    followThroughDoesNotReturn,
    sourceBreakoutObserved:
      breakoutCloseBeyondPreviousRange && followThroughDoesNotReturn,
    canonicalEligible: false,
  };
}
