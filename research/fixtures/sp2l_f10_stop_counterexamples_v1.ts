export interface Counterexample{id:string;type:"WICK_BODY"|"BUFFER"|"TOUCH_BREACH_CLOSE"|"SPIKE_ORIGIN_MAPPING";direction:"BUY"|"SELL";status:"UNRESOLVED";canonicalEligible:false}
export const F10_COUNTEREXAMPLES:readonly Counterexample[]=[
{id:"F10-CX-101",type:"WICK_BODY",direction:"BUY",status:"UNRESOLVED",canonicalEligible:false},
{id:"F10-CX-102",type:"WICK_BODY",direction:"SELL",status:"UNRESOLVED",canonicalEligible:false},
{id:"F10-CX-103",type:"BUFFER",direction:"BUY",status:"UNRESOLVED",canonicalEligible:false},
{id:"F10-CX-104",type:"BUFFER",direction:"SELL",status:"UNRESOLVED",canonicalEligible:false},
{id:"F10-CX-105",type:"TOUCH_BREACH_CLOSE",direction:"BUY",status:"UNRESOLVED",canonicalEligible:false},
{id:"F10-CX-106",type:"TOUCH_BREACH_CLOSE",direction:"SELL",status:"UNRESOLVED",canonicalEligible:false},
{id:"F10-CX-107",type:"SPIKE_ORIGIN_MAPPING",direction:"BUY",status:"UNRESOLVED",canonicalEligible:false},
{id:"F10-CX-108",type:"SPIKE_ORIGIN_MAPPING",direction:"SELL",status:"UNRESOLVED",canonicalEligible:false},
];