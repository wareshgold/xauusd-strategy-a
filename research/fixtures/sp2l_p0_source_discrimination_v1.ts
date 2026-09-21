export type Status="SOURCE_CONFIRMED_MEANING"|"SOURCE_DISCRIMINATED_BUT_FIELD_UNRESOLVED";
export interface Finding{id:string;family:"F08_SWING"|"F10_STOP";direction:"BUY"|"SELL";finding:string;status:Status;canonicalEligible:false}
export const P0_FINDINGS:readonly Finding[]=[
{id:"P0-001",family:"F08_SWING",direction:"BUY",finding:"Source visual evidence supports a structural directional leg between visible turning areas; exact OHLC endpoint/pivot algorithm is not specified.",status:"SOURCE_DISCRIMINATED_BUT_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"P0-002",family:"F08_SWING",direction:"SELL",finding:"Bearish visual evidence is structurally mirrored; exact OHLC endpoint/pivot algorithm is not specified.",status:"SOURCE_DISCRIMINATED_BUT_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"P0-003",family:"F10_STOP",direction:"BUY",finding:"Source meaning places SL behind the candle from which the spike originated; exact field and invalidation event remain unspecified.",status:"SOURCE_CONFIRMED_MEANING",canonicalEligible:false},
{id:"P0-004",family:"F10_STOP",direction:"SELL",finding:"Source meaning is directionally mirrored; exact field and invalidation event remain unspecified.",status:"SOURCE_CONFIRMED_MEANING",canonicalEligible:false},
];