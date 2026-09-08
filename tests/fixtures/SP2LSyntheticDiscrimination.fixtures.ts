export type SP2LDiscriminationField =
  | 'PGAP_BOUNDARY'
  | 'PGAP_CANDLE_IDENTITY'
  | 'PGAP_TOUCH_RULE'
  | 'ENTRY_CANDLE_IDENTITY'
  | 'ENTRY_PRICE_CONVENTION'
  | 'ENTRY_REVISION_SEMANTICS'
  | 'FILL_TOUCH_SEMANTICS'
  | 'SL_BOUNDARY'
  | 'SPIKE_ORIGIN_IDENTITY'
  | 'LEG1_ANCHORS'
  | 'AB_CD_TOLERANCE';

export interface SP2LSyntheticDiscriminationFixture {
  readonly id: string;
  readonly field: SP2LDiscriminationField;
  readonly purpose: string;
  readonly candidateHypotheses: readonly string[];
  readonly candidatesAreUnresolved: true;
  readonly sourceEvidenceRequiredToSelect: true;
  readonly productionEligible: false;
}

/**
 * Research-only synthetic fixtures. They are designed to make future
 * source evidence discriminating, not to select a rule themselves.
 */
export const SP2L_SYNTHETIC_DISCRIMINATION_FIXTURES: readonly SP2LSyntheticDiscriminationFixture[] = [
  {
    id: 'SD-PGAP-BOUNDARY-WICK-BODY',
    field: 'PGAP_BOUNDARY',
    purpose: 'Separate wick-to-wick from body-edge and prior-extreme interpretations.',
    candidateHypotheses: ['PRIOR_EXTREME_TO_NEXT_EXTREME', 'BODY_EDGE_TO_BODY_EDGE', 'WICK_TO_WICK'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-PGAP-TIMING-INDEX',
    field: 'PGAP_CANDLE_IDENTITY',
    purpose: 'Separate fixed three-candle timing from relational timing across accepted variants.',
    candidateHypotheses: ['FIXED_3_CANDLE', 'BREAKOUT_FOLLOW_THROUGH_RELATIONAL', 'MULTI_CANDLE_RELATIONAL'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-PGAP-TOUCH-EQUALITY',
    field: 'PGAP_TOUCH_RULE',
    purpose: 'Distinguish strict non-overlap from equality/touch-allowed construction.',
    candidateHypotheses: ['STRICT_NON_OVERLAP', 'TOUCH_ALLOWED', 'EQUALITY_ALLOWED'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-ENTRY-CANDLE',
    field: 'ENTRY_CANDLE_IDENTITY',
    purpose: 'Separate previous/relevant candle, first correction candle, and origin-candle references.',
    candidateHypotheses: ['PREVIOUS_RELEVANT', 'FIRST_CORRECTION', 'SPIKE_ORIGIN'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-ENTRY-PRICE-WICK-BODY',
    field: 'ENTRY_PRICE_CONVENTION',
    purpose: 'Separate wick extreme from body edge at the selected structural reference.',
    candidateHypotheses: ['WICK_EXTREME', 'BODY_EDGE'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-ENTRY-REVISION',
    field: 'ENTRY_REVISION_SEMANTICS',
    purpose: 'Distinguish fixed-first-qualification limit from a revised limit as correction evolves.',
    candidateHypotheses: ['FIXED_ON_FIRST_QUALIFICATION', 'REVISED_WHEN_REFERENCE_CHANGES'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-FILL-TOUCH',
    field: 'FILL_TOUCH_SEMANTICS',
    purpose: 'Separate touch, crossing, and bar-close execution interpretations.',
    candidateHypotheses: ['INTRABAR_TOUCH', 'INTRABAR_CROSS', 'BAR_CLOSE_CONFIRMATION'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-SL-WICK-BODY-BUFFER',
    field: 'SL_BOUNDARY',
    purpose: 'Separate origin-candle wick/body boundary and any source-defined strictness.',
    candidateHypotheses: ['ORIGIN_WICK_EXTREME', 'ORIGIN_BODY_EDGE', 'ORIGIN_EXTREME_PLUS_BUFFER'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-SPIKE-ORIGIN-VARIANTS',
    field: 'SPIKE_ORIGIN_IDENTITY',
    purpose: 'Separate origin identification across the source Spike constructions.',
    candidateHypotheses: ['FIRST_DIRECTIONAL_CANDLE', 'STRUCTURAL_ORIGIN_CANDLE', 'SOURCE_VARIANT_SPECIFIC_ORIGIN'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-LEG1-ANCHORS',
    field: 'LEG1_ANCHORS',
    purpose: 'Separate candidate Leg-1 anchor pairs without importing classical harmonic mapping.',
    candidateHypotheses: ['ORIGIN_TO_SPIKE_EXTREME', 'CORRECTION_EXTREME_TO_SPIKE_EXTREME', 'BREAKOUT_LEVEL_TO_SPIKE_EXTREME'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
  {
    id: 'SD-ABCD-TOLERANCE',
    field: 'AB_CD_TOLERANCE',
    purpose: 'Prevent a numerical equality tolerance from being invented before source confirmation.',
    candidateHypotheses: ['EXACT_EQUALITY', 'SOURCE_DEFINED_FIXED_TOLERANCE', 'SOURCE_DEFINED_CONTEXTUAL_TOLERANCE'],
    candidatesAreUnresolved: true,
    sourceEvidenceRequiredToSelect: true,
    productionEligible: false,
  },
];
