export type Verdict="RETAIN_UNRESOLVED"|"SOURCE_DISCRIMINATES_MEANING"|"NOT_SOURCE_DISCRIMINATED";
export interface Case{id:string;family:"F08_SWING"|"F10_STOP";type:string;direction:"BUY"|"SELL";verdict:Verdict;reason:string;canonicalEligible:false}
export const P0_COUNTEREXAMPLE_DISCRIMINATION:readonly Case[]=[
{id:"CX-08-01",family:"F08_SWING",type:"WICK_VS_BODY",direction:"BUY",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"Source visual does not explicitly select wick or body endpoint.",canonicalEligible:false},
{id:"CX-08-02",family:"F08_SWING",type:"WICK_VS_BODY",direction:"SELL",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"Source visual does not explicitly select wick or body endpoint.",canonicalEligible:false},
{id:"CX-08-03",family:"F08_SWING",type:"STRUCTURAL_TURN_VS_FIXED_PIVOT",direction:"BUY",verdict:"SOURCE_DISCRIMINATES_MEANING",reason:"Source describes/depicts structural turning areas; no fixed pivot algorithm is demonstrated.",canonicalEligible:false},
{id:"CX-08-04",family:"F08_SWING",type:"STRUCTURAL_TURN_VS_FIXED_PIVOT",direction:"SELL",verdict:"SOURCE_DISCRIMINATES_MEANING",reason:"Bearish construction is structural/mirrored; no fixed pivot algorithm is demonstrated.",canonicalEligible:false},
{id:"CX-08-05",family:"F08_SWING",type:"ASYMMETRIC_WINDOW",direction:"BUY",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"No deterministic swing window is source-specified.",canonicalEligible:false},
{id:"CX-08-06",family:"F08_SWING",type:"ASYMMETRIC_WINDOW",direction:"SELL",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"No deterministic swing window is source-specified.",canonicalEligible:false},
{id:"CX-10-01",family:"F10_STOP",type:"WICK_BODY",direction:"BUY",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"Behind-origin-candle meaning is explicit, wick/body field is not.",canonicalEligible:false},
{id:"CX-10-02",family:"F10_STOP",type:"WICK_BODY",direction:"SELL",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"Behind-origin-candle meaning is explicit, wick/body field is not.",canonicalEligible:false},
{id:"CX-10-03",family:"F10_STOP",type:"BUFFER",direction:"BUY",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"No numeric buffer is source-specified.",canonicalEligible:false},
{id:"CX-10-04",family:"F10_STOP",type:"BUFFER",direction:"SELL",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"No numeric buffer is source-specified.",canonicalEligible:false},
{id:"CX-10-05",family:"F10_STOP",type:"TOUCH_BREACH_CLOSE",direction:"BUY",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"Stop placement meaning does not define the invalidation event.",canonicalEligible:false},
{id:"CX-10-06",family:"F10_STOP",type:"TOUCH_BREACH_CLOSE",direction:"SELL",verdict:"NOT_SOURCE_DISCRIMINATED",reason:"Stop placement meaning does not define the invalidation event.",canonicalEligible:false},
{id:"CX-10-07",family:"F10_STOP",type:"SPIKE_ORIGIN_MAPPING",direction:"BUY",verdict:"SOURCE_DISCRIMINATES_MEANING",reason:"Source explicitly ties SL to the candle from which the spike originated; exact mapping within multi-candle spike remains unresolved.",canonicalEligible:false},
{id:"CX-10-08",family:"F10_STOP",type:"SPIKE_ORIGIN_MAPPING",direction:"SELL",verdict:"SOURCE_DISCRIMINATES_MEANING",reason:"Source meaning is directionally mirrored; exact mapping within multi-candle spike remains unresolved.",canonicalEligible:false},
];