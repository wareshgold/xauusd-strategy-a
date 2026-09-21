export interface LifecycleCase{id:string;from:"PENDING"|"FILLED"|"CANCELLED";to:"PENDING"|"FILLED"|"CANCELLED"|"REPLACED";reason:"STRUCTURE_CHANGED"|"STOP_DISTANCE_CHANGED"|"UNRESOLVED_TIMEOUT"|"UNRESOLVED_FILL";canonicalEligible:false;}
export const LIFECYCLE_CASES:readonly LifecycleCase[]=[
{id:"LIFE-001",from:"PENDING",to:"REPLACED",reason:"STRUCTURE_CHANGED",canonicalEligible:false},
{id:"LIFE-002",from:"PENDING",to:"REPLACED",reason:"STOP_DISTANCE_CHANGED",canonicalEligible:false},
{id:"LIFE-003",from:"PENDING",to:"CANCELLED",reason:"UNRESOLVED_TIMEOUT",canonicalEligible:false},
{id:"LIFE-004",from:"PENDING",to:"FILLED",reason:"UNRESOLVED_FILL",canonicalEligible:false},
{id:"LIFE-005",from:"FILLED",to:"CANCELLED",reason:"STRUCTURE_CHANGED",canonicalEligible:false},
];