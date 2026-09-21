export type EventSemantics="TOUCH"|"BREACH"|"CLOSE"|"FILL";
export type Lifecycle="PLACE"|"REFRESH"|"DELETE"|"REPLACE"|"EXPIRE"|"FILL";
export interface Obs{id:string;family:"F11_LIFECYCLE"|"F12_TRIGGER";event:EventSemantics;lifecycle:Lifecycle;direction:"BUY"|"SELL";status:"SOURCE_SHAPED_UNRESOLVED";canonicalEligible:false;}
export const EXECUTION_MATRIX:readonly Obs[]=[
{id:"F11-001",family:"F11_LIFECYCLE",event:"FILL",lifecycle:"PLACE",direction:"BUY",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F11-002",family:"F11_LIFECYCLE",event:"FILL",lifecycle:"REFRESH",direction:"BUY",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F11-003",family:"F11_LIFECYCLE",event:"TOUCH",lifecycle:"DELETE",direction:"SELL",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F11-004",family:"F11_LIFECYCLE",event:"BREACH",lifecycle:"REPLACE",direction:"SELL",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F11-005",family:"F12_TRIGGER",event:"TOUCH",lifecycle:"PLACE",direction:"BUY",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F12-002",family:"F12_TRIGGER",event:"BREACH",lifecycle:"PLACE",direction:"BUY",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F12-003",family:"F12_TRIGGER",event:"CLOSE",lifecycle:"PLACE",direction:"BUY",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F12-004",family:"F12_TRIGGER",event:"TOUCH",lifecycle:"PLACE",direction:"SELL",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F12-005",family:"F12_TRIGGER",event:"BREACH",lifecycle:"PLACE",direction:"SELL",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
{id:"F12-006",family:"F12_TRIGGER",event:"CLOSE",lifecycle:"PLACE",direction:"SELL",status:"SOURCE_SHAPED_UNRESOLVED",canonicalEligible:false},
];