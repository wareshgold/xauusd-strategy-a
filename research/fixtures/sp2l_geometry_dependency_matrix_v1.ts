export type Family="F08_SWING"|"F09_ENTRY"|"F10_STOP"|"F14_ABCD";
export interface Dependency{id:string;from:Family;to:Family;relation:"DEPENDENT"|"INDEPENDENT_OR_UNRESOLVED";status:"UNRESOLVED";canonicalEligible:false;note:string}
export const GEOMETRY_DEPENDENCIES:readonly Dependency[]=[
{id:"DEP-001",from:"F08_SWING",to:"F09_ENTRY",relation:"DEPENDENT",status:"UNRESOLVED",canonicalEligible:false,note:"entry may depend on structural correction/swing selection"},
{id:"DEP-002",from:"F08_SWING",to:"F10_STOP",relation:"DEPENDENT",status:"UNRESOLVED",canonicalEligible:false,note:"stop source says spike-origin candle; exact swing-to-candle mapping unresolved"},
{id:"DEP-003",from:"F08_SWING",to:"F14_ABCD",relation:"DEPENDENT",status:"UNRESOLVED",canonicalEligible:false,note:"structural endpoints are one candidate anchor family; exact A/B/C/D unresolved"},
{id:"DEP-004",from:"F09_ENTRY",to:"F10_STOP",relation:"INDEPENDENT_OR_UNRESOLVED",status:"UNRESOLVED",canonicalEligible:false,note:"entry/stop relationship must not imply a lifecycle rule"},
{id:"DEP-005",from:"F09_ENTRY",to:"F14_ABCD",relation:"INDEPENDENT_OR_UNRESOLVED",status:"UNRESOLVED",canonicalEligible:false,note:"entry geometry does not by itself establish AB=CD anchors"},
{id:"DEP-006",from:"F10_STOP",to:"F14_ABCD",relation:"INDEPENDENT_OR_UNRESOLVED",status:"UNRESOLVED",canonicalEligible:false,note:"stop distance may affect 2X relation but does not define AB=CD tolerance"},
];