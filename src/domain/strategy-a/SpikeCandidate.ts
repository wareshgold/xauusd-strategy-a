import type { BreakoutDirection } from '../market/BreakoutDetector.js';

export type SpikeDirection = BreakoutDirection;

export interface SpikeCandidate {
  readonly startIndex: number;
  readonly endIndex: number;
  readonly direction: SpikeDirection;
  readonly startPrice: number;
  readonly endPrice: number;
  readonly size: number;
  readonly breakoutIndex?: number;
  readonly followThroughIndex?: number;
  readonly structureScore: number;
  readonly overlapScore: number;
  readonly hasPGAPEvidence: boolean;
}

export type SpikeRejectionReason =
  | 'INSUFFICIENT_MOVE'
  | 'DIRTY_STRUCTURE'
  | 'EXCESSIVE_OVERLAP'
  | 'NO_BREAKOUT'
  | 'NO_FOLLOW_THROUGH'
  | 'INSUFFICIENT_EVIDENCE';
