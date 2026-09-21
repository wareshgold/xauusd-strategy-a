export type AbcdAnchorFamily = "STRUCTURAL_SWINGS" | "SPIKE_EXTREMES" | "CANDLE_OHLC_FIELDS";
export interface AbcdObservation { id:string; family:AbcdAnchorFamily; direction:"BUY"|"SELL"; a:number;b:number;c:number;d:number; leg1:number;leg2:number; ratio:number; toleranceStatus:"UNRESOLVED"; canonicalEligible:false; }
export const ABCD_ANCHOR_MATRIX: readonly AbcdObservation[] = [
{id:"ABCD-001",family:"STRUCTURAL_SWINGS",direction:"BUY",a:100,b:120,c:110,d:130,leg1:20,leg2:20,ratio:1,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"ABCD-002",family:"SPIKE_EXTREMES",direction:"BUY",a:98,b:122,c:109,d:133,leg1:24,leg2:24,ratio:1,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"ABCD-003",family:"CANDLE_OHLC_FIELDS",direction:"BUY",a:101,b:121,c:111,d:132,leg1:20,leg2:21,ratio:1.05,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"ABCD-004",family:"STRUCTURAL_SWINGS",direction:"SELL",a:120,b:100,c:110,d:90,leg1:20,leg2:20,ratio:1,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"ABCD-005",family:"SPIKE_EXTREMES",direction:"SELL",a:122,b:98,c:111,d:87,leg1:24,leg2:24,ratio:1,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"ABCD-006",family:"CANDLE_OHLC_FIELDS",direction:"SELL",a:121,b:101,c:111,d:90,leg1:20,leg2:21,ratio:1.05,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"ABCD-007",family:"STRUCTURAL_SWINGS",direction:"BUY",a:100,b:120,c:110,d:131,leg1:20,leg2:21,ratio:1.05,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
{id:"ABCD-008",family:"STRUCTURAL_SWINGS",direction:"BUY",a:100,b:120,c:110,d:135,leg1:20,leg2:25,ratio:1.25,toleranceStatus:"UNRESOLVED",canonicalEligible:false},
];