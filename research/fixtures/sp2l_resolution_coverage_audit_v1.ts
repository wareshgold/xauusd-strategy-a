export type State="COVERED_UNRESOLVED"|"SOURCE_CONFIRMED_PARTIAL"|"NOT_INDEPENDENTLY_DEMONSTRATED";
export interface Row{id:string;family:string;state:State;blocks:string[];canonicalEligible:false}
export const COVERAGE:readonly Row[]=[
{id:"COV-F08",family:"F08_SWING",state:"COVERED_UNRESOLVED",blocks:["F09","F10","F14"],canonicalEligible:false},
{id:"COV-F09",family:"F09_ENTRY",state:"COVERED_UNRESOLVED",blocks:["EXECUTION"],canonicalEligible:false},
{id:"COV-F10",family:"F10_STOP",state:"COVERED_UNRESOLVED",blocks:["F13"],canonicalEligible:false},
{id:"COV-F11",family:"F11_LIFECYCLE",state:"COVERED_UNRESOLVED",blocks:["EXECUTION"],canonicalEligible:false},
{id:"COV-F12",family:"F12_TRIGGER",state:"COVERED_UNRESOLVED",blocks:["EXECUTION"],canonicalEligible:false},
{id:"COV-F13",family:"F13_2X",state:"SOURCE_CONFIRMED_PARTIAL",blocks:["EXECUTION","RISK_AGGREGATION"],canonicalEligible:false},
{id:"COV-F14",family:"F14_ABCD",state:"COVERED_UNRESOLVED",blocks:["LEG2"],canonicalEligible:false},
{id:"COV-F15",family:"F15_BEARISH",state:"NOT_INDEPENDENTLY_DEMONSTRATED",blocks:["CANONICAL_EXECUTION"],canonicalEligible:false},
];