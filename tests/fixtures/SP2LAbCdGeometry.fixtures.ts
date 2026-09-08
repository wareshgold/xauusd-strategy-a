export type SP2LABCDAnchorHypothesis =
  | 'H1_ORIGIN_TO_SPIKE_EXTREME'
  | 'H2_FIRST_CORRECTION_EXTREME_TO_SPIKE_EXTREME'
  | 'H3_BREAKOUT_LEVEL_TO_SPIKE_EXTREME'
  | 'H4_CLASSICAL_A_B_MAPPING'
  | 'H5_BODY_EDGE_VARIANT';

export interface SP2LABCDGeometryFixture {
  readonly fixtureId: string;
  readonly direction: 'BUY' | 'SELL';
  readonly sourceObservation: 'AB_EQUALS_CD';
  readonly sourceShowsExactAnchors: false;
  readonly sourceShowsExactTolerance: false;
  readonly candidateHypotheses: readonly SP2LABCDAnchorHypothesis[];
  readonly selectedHypothesis: null;
}

/** Research-only guardrails: source semantics are preserved without inventing A/B/C/D anchors. */
export const SP2L_ABCD_GEOMETRY_FIXTURES: readonly SP2LABCDGeometryFixture[] = [
  {
    fixtureId: 'ABCD-BUY-DISTINCT-ANCHORS',
    direction: 'BUY',
    sourceObservation: 'AB_EQUALS_CD',
    sourceShowsExactAnchors: false,
    sourceShowsExactTolerance: false,
    candidateHypotheses: ['H1_ORIGIN_TO_SPIKE_EXTREME', 'H2_FIRST_CORRECTION_EXTREME_TO_SPIKE_EXTREME', 'H3_BREAKOUT_LEVEL_TO_SPIKE_EXTREME', 'H4_CLASSICAL_A_B_MAPPING', 'H5_BODY_EDGE_VARIANT'],
    selectedHypothesis: null,
  },
  {
    fixtureId: 'ABCD-SELL-DISTINCT-ANCHORS',
    direction: 'SELL',
    sourceObservation: 'AB_EQUALS_CD',
    sourceShowsExactAnchors: false,
    sourceShowsExactTolerance: false,
    candidateHypotheses: ['H1_ORIGIN_TO_SPIKE_EXTREME', 'H2_FIRST_CORRECTION_EXTREME_TO_SPIKE_EXTREME', 'H3_BREAKOUT_LEVEL_TO_SPIKE_EXTREME', 'H4_CLASSICAL_A_B_MAPPING', 'H5_BODY_EDGE_VARIANT'],
    selectedHypothesis: null,
  },
  {
    fixtureId: 'ABCD-MIRROR-SYMMETRY',
    direction: 'BUY',
    sourceObservation: 'AB_EQUALS_CD',
    sourceShowsExactAnchors: false,
    sourceShowsExactTolerance: false,
    candidateHypotheses: ['H1_ORIGIN_TO_SPIKE_EXTREME', 'H2_FIRST_CORRECTION_EXTREME_TO_SPIKE_EXTREME', 'H3_BREAKOUT_LEVEL_TO_SPIKE_EXTREME', 'H4_CLASSICAL_A_B_MAPPING', 'H5_BODY_EDGE_VARIANT'],
    selectedHypothesis: null,
  },
];
