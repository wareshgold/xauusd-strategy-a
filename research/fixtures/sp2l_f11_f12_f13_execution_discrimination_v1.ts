export type Verdict="SOURCE_NARROWS"|"UNRESOLVED";
export interface Case{id:string;family:"F11_LIFECYCLE"|"F12_TRIGGER"|"F13_2X";type:string;direction:"BUY"|"SELL"|"N_A";verdict:Verdict;reason:string;canonicalEligible:false}
export const EXECUTION_DISCRIMINATION:readonly Case[]=[
{id:"E-11-01",family:"F11_LIFECYCLE",type:"PENDING_DELETE_REPLACE",direction:"BUY",verdict:"SOURCE_NARROWS",reason:"Source shows pending-order usage and deletion/replacement behavior; exact mandatory predicate and timeout remain unresolved.",canonicalEligible:false},
{id:"E-11-02",family:"F11_LIFECYCLE",type:"TOUCH_VS_FILL",direction:"BUY",verdict:"UNRESOLVED",reason:"Order interaction is not enough to equate touch with fill.",canonicalEligible:false},
{id:"E-11-03",family:"F11_LIFECYCLE",type:"TIMEOUT",direction:"SELL",verdict:"UNRESOLVED",reason:"No canonical timeout duration is source-established.",canonicalEligible:false},
{id:"E-12-01",family:"F12_TRIGGER",type:"TOUCH_BREACH_CLOSE",direction:"BUY",verdict:"UNRESOLVED",reason:"Trigger event cannot be silently chosen from OHLC proximity.",canonicalEligible:false},
{id:"E-12-02",family:"F12_TRIGGER",type:"TOUCH_BREACH_CLOSE",direction:"SELL",verdict:"UNRESOLVED",reason:"Bearish trigger event remains unresolved.",canonicalEligible:false},
{id:"E-12-03",family:"F12_TRIGGER",type:"ACTIVATION_VS_FILL",direction:"BUY",verdict:"UNRESOLVED",reason:"Activation and broker fill are distinct states until source evidence resolves them.",canonicalEligible:false},
{id:"E-12-04",family:"F12_TRIGGER",type:"ACTIVATION_VS_FILL",direction:"SELL",verdict:"UNRESOLVED",reason:"Activation and broker fill are distinct states until source evidence resolves them.",canonicalEligible:false},
{id:"E-13-01",family:"F13_2X",type:"ENTRY_SL_MIDPOINT_RELATION",direction:"BUY",verdict:"SOURCE_NARROWS",reason:"Secondary entry relation is source-confirmed; lifecycle and sizing are not.",canonicalEligible:false},
{id:"E-13-02",family:"F13_2X",type:"ENTRY_SL_MIDPOINT_RELATION",direction:"SELL",verdict:"SOURCE_NARROWS",reason:"Directional mirror of source-confirmed relation; lifecycle and sizing remain unresolved.",canonicalEligible:false},
{id:"E-13-03",family:"F13_2X",type:"SIZING_RISK_AGGREGATION",direction:"N_A",verdict:"UNRESOLVED",reason:"Source examples do not freeze a deterministic aggregate risk/sizing state machine.",canonicalEligible:false},
{id:"E-13-04",family:"F13_2X",type:"SHARED_SL_TP_LIFECYCLE",direction:"N_A",verdict:"UNRESOLVED",reason:"Shared versus separate management semantics are unresolved.",canonicalEligible:false},
];
