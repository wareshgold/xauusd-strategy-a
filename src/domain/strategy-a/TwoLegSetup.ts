import type { LegProjection } from './LegProjection.js';
import type { Correction } from './CorrectionDetector.js';
import type { SpikeCandidate } from './SpikeCandidate.js';

export interface PotentialSetup {
  readonly strategy: 'A';
  readonly direction: 'BUY' | 'SELL';
  readonly spike: SpikeCandidate;
  readonly correction: Correction;
  readonly legProjection: LegProjection;
  readonly status: 'POTENTIAL' | 'REJECTED';
  readonly reason: string;
}

export function buildPotentialSetup(spike: SpikeCandidate, correction: Correction, legProjection: LegProjection | null): PotentialSetup {
  if (!legProjection) {
    return { strategy: 'A', direction: spike.direction === 'BULLISH' ? 'BUY' : 'SELL', spike, correction, legProjection: null as never, status: 'REJECTED', reason: 'LEG1_NOT_PROJECTABLE' };
  }
  return { strategy: 'A', direction: legProjection.direction, spike, correction, legProjection, status: 'POTENTIAL', reason: 'SPIKE_CORRECTION_LEG2_PROJECTION_READY' };
}
