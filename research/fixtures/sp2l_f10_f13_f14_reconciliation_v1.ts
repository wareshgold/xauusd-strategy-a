export type Status="SOURCE_CONFIRMED_RELATION_ONLY"|"SOURCE_SHAPED_UNRESOLVED";
export interface Case{id:string;family:"F10_STOP"|"F13_2X"|"F14_ABCD";direction:"BUY"|"SELL";status:Status;canonicalEligible:false;note:string}
export const RECONCILIATION:readonly Case[]=[
{id:"F10-001",family:"F10_STOP",direction:"BUY",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false,note:"SL behind spike-origin candle; exact wick/body/buffer unresolved"},
{id:"F10-002",family:"F10_STOP",direction:"SELL",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false,note:"mirror of source-shaped stop anchor; exact field unresolved"},
{id:"F13-001",family:"F13_2X",direction:"BUY",status:"SOURCE_CONFIRMED_RELATION_ONLY",canonicalEligible:false,note:"secondary entry is midpoint between Entry and Stop-Loss"},
{id:"F13-002",family:"F13_2X",direction:"SELL",status:"SOURCE_CONFIRMED_RELATION_ONLY",canonicalEligible:false,note:"same documented relation, mirrored direction"},
{id:"F14-001",family:"F14_ABCD",direction:"BUY",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false,note:"Leg1/Leg2 approximately equal; exact A/B/C/D and tolerance unresolved"},
{id:"F14-002",family:"F14_ABCD",direction:"SELL",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false,note:"bearish structural mirror; exact anchors/tolerance unresolved"},
];