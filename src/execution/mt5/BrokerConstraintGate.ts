export interface BrokerConstraintState {
  readonly known: boolean;
  readonly minimumStopDistancePrice: number | null;
  readonly freezeDistancePrice: number | null;
}
