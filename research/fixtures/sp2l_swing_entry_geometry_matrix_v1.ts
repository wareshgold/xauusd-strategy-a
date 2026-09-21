export type SwingHypothesis="STRUCTURAL_TURN"|"WICK_EXTREME"|"BODY_ENDPOINT";
export type EntryHypothesis="CURRENT_HIGHER_LOW_LIMIT"|"CORRECTION_EXTREME_LIMIT"|"RECLAIM_CLOSE";
export interface Obs{id:string;family:"F08_SWING"|"F09_ENTRY";hypothesis:string;direction:"BUY"|"SELL";sourceStatus:"SOURCE_SHAPED_UNRESOLVED";canonicalEligible:false;}
export const MATRIX:readonly Obs[]=[
{id:"F08-001",family:"F08_SWING",hypothesis:"STRUCTURAL_TURN",direction:"BUY",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F08-002",family:"F08_SWING",hypothesis:"WICK_EXTREME",direction:"BUY",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F08-003",family:"F08_SWING",hypothesis:"BODY_ENDPOINT",direction:"SELL",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F09-001",family:"F09_ENTRY",hypothesis:"CURRENT_HIGHER_LOW_LIMIT",direction:"BUY",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F09-002",family:"F09_ENTRY",hypothesis:"CORRECTION_EXTREME_LIMIT",direction:"SELL",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F09-003",family:"F09_ENTRY",hypothesis:"RECLAIM_CLOSE",direction:"BUY",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F09-004",family:"F09_ENTRY",hypothesis:"CURRENT_HIGHER_LOW_LIMIT",direction:"SELL",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F09-005",family:"F09_ENTRY",hypothesis:"CORRECTION_EXTREME_LIMIT",direction:"BUY",sourceStatus:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
];