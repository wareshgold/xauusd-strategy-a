export type Hypothesis="STRUCTURAL_TURN"|"WICK_EXTREME"|"BODY_ENDPOINT";
export interface Case{id:string;direction:"BUY"|"SELL";hypothesis:Hypothesis;status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED";canonicalEligible:false;counterexample:string}
export const F08_SWING_CASES:readonly Case[]=[
{id:"F08-001",direction:"BUY",hypothesis:"STRUCTURAL_TURN",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false,counterexample:"turn area visible but exact pivot algorithm absent"},
{id:"F08-002",direction:"BUY",hypothesis:"WICK_EXTREME",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false,counterexample:"wick may extend beyond structural body"},
{id:"F08-003",direction:"BUY",hypothesis:"BODY_ENDPOINT",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false,counterexample:"body endpoint can differ from visible structural extreme"},
{id:"F08-004",direction:"SELL",hypothesis:"STRUCTURAL_TURN",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false,counterexample:"bearish turn area visible but exact pivot algorithm absent"},
{id:"F08-005",direction:"SELL",hypothesis:"WICK_EXTREME",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false,counterexample:"wick may extend beyond structural body"},
{id:"F08-006",direction:"SELL",hypothesis:"BODY_ENDPOINT",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false,counterexample:"body endpoint can differ from visible structural extreme"},
];