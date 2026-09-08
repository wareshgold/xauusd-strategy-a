export type SP2LPGAPTimingVariant = 'V1' | 'V2' | 'V3';

export interface SP2LPGAPTimingResolutionFixture {
  readonly id: SP2LPGAPTimingVariant;
  readonly sourceTimingObservation: string;
  readonly gapMustBeWithinSpikeSequence: true;
  readonly exactCandleIndexResolved: false;
  readonly exactBoundaryResolved: false;
  readonly threeCandleFormulaCanonical: false;
}

/** Research-only timing observations from the authoritative teaching sequence. */
export const SP2L_PGAP_TIMING_RESOLUTION_FIXTURES: readonly SP2LPGAPTimingResolutionFixture[] = [
  {
    id: 'V1',
    sourceTimingObservation: 'breakout followed by continuation/gap evidence',
    gapMustBeWithinSpikeSequence: true,
    exactCandleIndexResolved: false,
    exactBoundaryResolved: false,
    threeCandleFormulaCanonical: false,
  },
  {
    id: 'V2',
    sourceTimingObservation: 'directional higher-low sequence followed by gap evidence',
    gapMustBeWithinSpikeSequence: true,
    exactCandleIndexResolved: false,
    exactBoundaryResolved: false,
    threeCandleFormulaCanonical: false,
  },
  {
    id: 'V3',
    sourceTimingObservation: 'distinct accepted-looking candle arrangement with gap evidence',
    gapMustBeWithinSpikeSequence: true,
    exactCandleIndexResolved: false,
    exactBoundaryResolved: false,
    threeCandleFormulaCanonical: false,
  },
];
