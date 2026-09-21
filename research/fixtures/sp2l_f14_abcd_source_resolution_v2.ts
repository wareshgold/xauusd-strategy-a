export type Anchor="STRUCTURAL_SWINGS"|"SPIKE_EXTREMES"|"CANDLE_OHLC_FIELDS";
export interface Case{id:string;direction:"BUY"|"SELL";anchor:Anchor;ratio:number;toleranceStatus:"UNRESOLVED";canonicalEligible:false}
export const F14_CASES:readonly Case[]=[
{id:"F14-101",direction:"BUY",anchor:"STRUCTURAL_SWINGS",ratio:1,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"F14-102",direction:"BUY",anchor:"SPIKE_EXTREMES",ratio:1.05,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"F14-103",direction:"BUY",anchor:"CANDLE_OHLC_FIELDS",ratio:1.25,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"F14-104",direction:"SELL",anchor:"STRUCTURAL_SWINGS",ratio:1,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"F14-105",direction:"SELL",anchor:"SPIKE_EXTREMES",ratio:1.05,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"F14-106",direction:"SELL",anchor:"CANDLE_OHLC_FIELDS",ratio:1.25,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
];