export type Leg1AnchorHypothesis =
  | "FIRST_SPIKE_OPEN_TO_LAST_SPIKE_CLOSE"
  | "FIRST_SPIKE_EXTREME_TO_LAST_SPIKE_EXTREME"
  | "STRUCTURAL_SWING_ENDPOINTS";

export interface Leg1AnchorObservation {
  id: string;
  hypothesis: Leg1AnchorHypothesis;
  direction: "BUY" | "SELL";
  startPrice: number;
  endPrice: number;
  size: number;
  sourceStatus: "STRUCTURE_SUPPORTED_FIELD_UNRESOLVED";
  canonicalEligible: false;
}

export const LEG1_ANCHOR_MATRIX: readonly Leg1AnchorObservation[] = [
  {id:"LEG1-001",hypothesis:"FIRST_SPIKE_OPEN_TO_LAST_SPIKE_CLOSE",direction:"BUY",startPrice:100,endPrice:110,size:10,sourceStatus:"STRUCTURE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
  {id:"LEG1-002",hypothesis:"FIRST_SPIKE_EXTREME_TO_LAST_SPIKE_EXTREME",direction:"BUY",startPrice:98,endPrice:112,size:14,sourceStatus:"STRUCTURE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
  {id:"LEG1-003",hypothesis:"STRUCTURAL_SWING_ENDPOINTS",direction:"BUY",startPrice:99,endPrice:111,size:12,sourceStatus:"STRUCTURE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
  {id:"LEG1-004",hypothesis:"FIRST_SPIKE_OPEN_TO_LAST_SPIKE_CLOSE",direction:"SELL",startPrice:110,endPrice:100,size:10,sourceStatus:"STRUCTURE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
  {id:"LEG1-005",hypothesis:"FIRST_SPIKE_EXTREME_TO_LAST_SPIKE_EXTREME",direction:"SELL",startPrice:112,endPrice:98,size:14,sourceStatus:"STRUCTURE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
  {id:"LEG1-006",hypothesis:"STRUCTURAL_SWING_ENDPOINTS",direction:"SELL",startPrice:111,endPrice:99,size:12,sourceStatus:"STRUCTURE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
] as const;
