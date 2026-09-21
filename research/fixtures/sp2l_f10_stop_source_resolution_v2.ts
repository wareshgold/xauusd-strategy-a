export type Anchor="SPIKE_CANDLE_WICK_EXTREME"|"SPIKE_CANDLE_BODY"|"STRUCTURAL_SWING"|"BUFFERED_EXTREME";
export type Event="TOUCH"|"BREACH"|"CLOSE";
export interface Case{id:string;direction:"BUY"|"SELL";anchor:Anchor;event:Event;status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED";canonicalEligible:false}
export const F10_CASES:readonly Case[]=[
{id:"F10-101",direction:"BUY",anchor:"SPIKE_CANDLE_WICK_EXTREME",event:"BREACH",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F10-102",direction:"BUY",anchor:"SPIKE_CANDLE_BODY",event:"BREACH",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F10-103",direction:"BUY",anchor:"STRUCTURAL_SWING",event:"CLOSE",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F10-104",direction:"BUY",anchor:"BUFFERED_EXTREME",event:"TOUCH",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F10-105",direction:"SELL",anchor:"SPIKE_CANDLE_WICK_EXTREME",event:"BREACH",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F10-106",direction:"SELL",anchor:"SPIKE_CANDLE_BODY",event:"BREACH",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F10-107",direction:"SELL",anchor:"STRUCTURAL_SWING",event:"CLOSE",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
{id:"F10-108",direction:"SELL",anchor:"BUFFERED_EXTREME",event:"TOUCH",status:"SOURCE_SUPPORTED_FIELD_UNRESOLVED",canonicalEligible:false},
];