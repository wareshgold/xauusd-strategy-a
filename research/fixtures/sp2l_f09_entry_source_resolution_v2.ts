export type Entry="CURRENT_HIGHER_LOW_LIMIT"|"CORRECTION_EXTREME_LIMIT"|"RECLAIM_CLOSE"|"PENDING_LIMIT";
export interface Case{id:string;direction:"BUY"|"SELL";entry:Entry;triggerCandleCount:1|2|3;status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED";canonicalEligible:false}
export const F09_CASES:readonly Case[]=[
{id:"F09-101",direction:"BUY",entry:"CURRENT_HIGHER_LOW_LIMIT",triggerCandleCount:1,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F09-102",direction:"BUY",entry:"CORRECTION_EXTREME_LIMIT",triggerCandleCount:2,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F09-103",direction:"BUY",entry:"RECLAIM_CLOSE",triggerCandleCount:3,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F09-104",direction:"BUY",entry:"PENDING_LIMIT",triggerCandleCount:1,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F09-105",direction:"SELL",entry:"CURRENT_HIGHER_LOW_LIMIT",triggerCandleCount:1,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F09-106",direction:"SELL",entry:"CORRECTION_EXTREME_LIMIT",triggerCandleCount:2,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F09-107",direction:"SELL",entry:"RECLAIM_CLOSE",triggerCandleCount:3,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F09-108",direction:"SELL",entry:"PENDING_LIMIT",triggerCandleCount:1,status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
];