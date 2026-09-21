export type Priority="P0_SOURCE_BLOCKER"|"P1_DEPENDENT"|"P2_DOWNSTREAM";
export interface Item{id:string;family:string;priority:Priority;blocks:string[];reason:string;canonicalEligible:false}
export const RESOLUTION_PRIORITY:readonly Item[]=[
{id:"RES-001",family:"F08_SWING",priority:"P0_SOURCE_BLOCKER",blocks:["F09_ENTRY","F10_STOP","F14_ABCD"],reason:"swing selection can determine downstream structural anchors",canonicalEligible:false},
{id:"RES-002",family:"F09_ENTRY",priority:"P1_DEPENDENT",blocks:["F13_2X"],reason:"entry geometry is required before entry-relative lifecycle can be frozen",canonicalEligible:false},
{id:"RES-003",family:"F10_STOP",priority:"P0_SOURCE_BLOCKER",blocks:["F13_2X"],reason:"exact stop anchor/field and buffer are required for executable risk geometry",canonicalEligible:false},
{id:"RES-004",family:"F14_ABCD",priority:"P1_DEPENDENT",blocks:["LEG2"],reason:"A/B/C/D anchors and tolerance remain unresolved",canonicalEligible:false},
{id:"RES-005",family:"F11_LIFECYCLE",priority:"P1_DEPENDENT",blocks:["F12_TRIGGER"],reason:"pending lifecycle and trigger/fill semantics must not be conflated",canonicalEligible:false},
{id:"RES-006",family:"F12_TRIGGER",priority:"P1_DEPENDENT",blocks:["EXECUTION"],reason:"touch/breach/close/fill and activation semantics unresolved",canonicalEligible:false},
{id:"RES-007",family:"F15_BEARISH",priority:"P2_DOWNSTREAM",blocks:["CANONICAL_EXECUTION"],reason:"bearish P-Gap remains not independently demonstrated",canonicalEligible:false},
];