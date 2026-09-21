export type Verdict="SOURCE_NARROWS"|"UNRESOLVED";
export interface Case{id:string;family:"F09_ENTRY"|"F14_ABCD";type:string;direction:"BUY"|"SELL";verdict:Verdict;reason:string;canonicalEligible:false}
export const F09_F14:readonly Case[]=[
{id:"D-09-01",family:"F09_ENTRY",type:"TRIGGER_COUNT_1_2_3",direction:"BUY",verdict:"SOURCE_NARROWS",reason:"Source examples support a family of one/two/three-candle developments; fixed count is not frozen.",canonicalEligible:false},
{id:"D-09-02",family:"F09_ENTRY",type:"TRIGGER_COUNT_1_2_3",direction:"SELL",verdict:"SOURCE_NARROWS",reason:"Bearish construction is mirrored; fixed count is not independently frozen.",canonicalEligible:false},
{id:"D-09-03",family:"F09_ENTRY",type:"LIMIT_VS_RECLAIM",direction:"BUY",verdict:"UNRESOLVED",reason:"Source shows pending-limit usage but exact price-field precedence remains unresolved.",canonicalEligible:false},
{id:"D-09-04",family:"F09_ENTRY",type:"LIMIT_VS_RECLAIM",direction:"SELL",verdict:"UNRESOLVED",reason:"Exact bearish entry field and precedence remain unresolved.",canonicalEligible:false},
{id:"D-14-01",family:"F14_ABCD",type:"STRUCTURAL_VS_CANDLE_ANCHOR",direction:"BUY",verdict:"SOURCE_NARROWS",reason:"Visual evidence shows structural swing-to-swing leg construction; exact OHLC endpoint remains unresolved.",canonicalEligible:false},
{id:"D-14-02",family:"F14_ABCD",type:"STRUCTURAL_VS_CANDLE_ANCHOR",direction:"SELL",verdict:"SOURCE_NARROWS",reason:"Bearish visual construction is structurally mirrored; exact OHLC endpoint remains unresolved.",canonicalEligible:false},
{id:"D-14-03",family:"F14_ABCD",type:"RATIO_1_05",direction:"BUY",verdict:"UNRESOLVED",reason:"Near-equality cannot establish a numeric tolerance.",canonicalEligible:false},
{id:"D-14-04",family:"F14_ABCD",type:"RATIO_1_25",direction:"SELL",verdict:"UNRESOLVED",reason:"Material inequality cannot establish an executable acceptance threshold.",canonicalEligible:false},
];