export interface BrokerConstraintState {
  readonly known: boolean;
  readonly minimumStopDistancePrice: number | null;
  readonly freezeDistancePrice: number | null;
}

export function canSubmitStopModification(
  state: BrokerConstraintState,
): boolean {
  if (!state.known) return false;
  if (
    state.minimumStopDistancePrice === null ||
    state.freezeDistancePrice === null
  ) {
    return false;
  }
  return (
    Number.isFinite(state.minimumStopDistancePrice) &&
    Number.isFinite(state.freezeDistancePrice) &&
    state.minimumStopDistancePrice >= 0 &&
    state.freezeDistancePrice >= 0
  );
}