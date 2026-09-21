export interface Counterexample{id:string;type:"WICK_VS_BODY"|"STRUCTURAL_TURN_VS_FIXED_PIVOT"|"ASYMMETRIC_WINDOW";direction:"BUY"|"SELL";status:"UNRESOLVED";canonicalEligible:false}
export const F08_COUNTEREXAMPLES:readonly Counterexample[]=[
{id:"F08-CX-001",type:"WICK_VS_BODY",direction:"BUY",status:"UNRESOLVED",canonicalEligible:false},
{id:"F08-CX-002",type:"WICK_VS_BODY",direction:"SELL",status:"UNRESOLVED",canonicalEligible:false},
{id:"F08-CX-003",type:"STRUCTURAL_TURN_VS_FIXED_PIVOT",direction:"BUY",status:"UNRESOLVED",canonicalEligible:false},
{id:"F08-CX-004",type:"STRUCTURAL_TURN_VS_FIXED_PIVOT",direction:"SELL",status:"UNRESOLVED",canonicalEligible:false},
{id:"F08-CX-005",type:"ASYMMETRIC_WINDOW",direction:"BUY",status:"UNRESOLVED",canonicalEligible:false},
{id:"F08-CX-006",type:"ASYMMETRIC_WINDOW",direction:"SELL",status:"UNRESOLVED",canonicalEligible:false},
];