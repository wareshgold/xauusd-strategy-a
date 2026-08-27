import type { SpikeCandidate } from './SpikeCandidate.js';
import type { StrategyAContext } from './Context.js';

export type SetupQuality = 'A' | 'B' | 'C';

export interface QualityScore {
  readonly score: number;
  readonly grade: SetupQuality;
  readonly factors: readonly { name: string; points: number; reason: string }[];
  readonly tradeAllowed: boolean;
}

/** Transparent baseline score. Thresholds are research parameters, not validated edge claims. */
export function scoreSetup(spike: SpikeCandidate, context: StrategyAContext): QualityScore {
  const factors = [
    { name: 'structure', points: spike.structureScore >= 0.7 ? 2 : 1, reason: `directional fraction=${spike.structureScore.toFixed(2)}` },
    { name: 'overlap', points: spike.overlapScore >= 0.7 ? 2 : 1, reason: `cleanliness=${spike.overlapScore.toFixed(2)}` },
    { name: 'p-gap-evidence', points: spike.hasPGAPEvidence ? 2 : 0, reason: spike.hasPGAPEvidence ? 'research evidence present' : 'not validated/present' },
    { name: 'location', points: context.location.nearRoundLevel ? 1 : 0, reason: context.location.locationLabel },
    { name: 'ema-context', points: context.ema.aligned ? 1 : 0, reason: `price ${context.ema.side} EMA` },
    { name: 'session', points: context.session.sessionRisk === 'NORMAL' ? 1 : 0, reason: context.session.sessionRisk },
  ];
  const score = factors.reduce((sum, f) => sum + f.points, 0);
  const grade: SetupQuality = score >= 8 ? 'A' : score >= 5 ? 'B' : 'C';
  return { score, grade, factors, tradeAllowed: grade !== 'C' && context.session.sessionRisk !== 'BLOCKED' };
}
