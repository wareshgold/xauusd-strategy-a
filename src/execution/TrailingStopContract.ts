export interface TrailingStopExecutionContract {
  readonly enabled: boolean;
  readonly distancePrice: number | null;
  readonly activationPrice: number | null;
  readonly stepPrice: number | null;
  readonly evaluation: 'UNFROZEN';
  readonly brokerConstraints: 'UNFROZEN';
}

/**
 * The contract is deliberately non-executable until every execution semantic
 * is explicitly frozen. No Strategy A/source rule is defined here.
 */
export const UNFROZEN_TRAILING_CONTRACT: TrailingStopExecutionContract = {
  enabled: false,
  distancePrice: null,
  activationPrice: null,
  stepPrice: null,
  evaluation: 'UNFROZEN',
  brokerConstraints: 'UNFROZEN',
};
