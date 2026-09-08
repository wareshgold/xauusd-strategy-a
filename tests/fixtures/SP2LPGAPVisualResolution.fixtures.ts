export type SP2LPGAPVisualVariant = 'V1' | 'V2' | 'V3' | 'REJECTED';

export interface SP2LPGAPVisualResolutionFixture {
  readonly id: SP2LPGAPVisualVariant;
  readonly sourceLabel: string;
  readonly nonOverlapEvidence: boolean;
  readonly validBreakoutEvidence: boolean;
  readonly exactBoundaryResolved: false;
  readonly exactCandleTimingResolved: false;
  readonly minimumGapResolved: false;
  readonly touchEqualityResolved: false;
}

/**
 * Research-only observations from the authoritative SP2L teaching slide.
 * These fixtures encode only what the visual evidence supports: accepted
 * constructions exhibit a source-described non-overlap/gap relationship;
 * exact OHLC boundaries remain unresolved.
 */
export const SP2L_PGAP_VISUAL_RESOLUTION_FIXTURES: readonly SP2LPGAPVisualResolutionFixture[] = [
  { id: 'V1', sourceLabel: 'accepted-looking construction 1', nonOverlapEvidence: true, validBreakoutEvidence: true, exactBoundaryResolved: false, exactCandleTimingResolved: false, minimumGapResolved: false, touchEqualityResolved: false },
  { id: 'V2', sourceLabel: 'accepted-looking construction 2', nonOverlapEvidence: true, validBreakoutEvidence: true, exactBoundaryResolved: false, exactCandleTimingResolved: false, minimumGapResolved: false, touchEqualityResolved: false },
  { id: 'V3', sourceLabel: 'accepted-looking construction 3', nonOverlapEvidence: true, validBreakoutEvidence: true, exactBoundaryResolved: false, exactCandleTimingResolved: false, minimumGapResolved: false, touchEqualityResolved: false },
  { id: 'REJECTED', sourceLabel: 'red-X construction', nonOverlapEvidence: false, validBreakoutEvidence: false, exactBoundaryResolved: false, exactCandleTimingResolved: false, minimumGapResolved: false, touchEqualityResolved: false },
];