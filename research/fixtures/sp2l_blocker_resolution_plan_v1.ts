export interface Blocker{readonly id:string;readonly family:string;readonly priority:"P0"|"P1"|"P2";readonly evidenceNeeded:readonly string[];readonly promotionGuard:string;readonly canonicalEligible:false}
export const BLOCKERS:readonly Blocker[]=[
{id:"B08",family:"F08_SWING",priority:"P0",evidenceNeeded:["source-demonstrated pivot/swing selection","wick-vs-body semantics","counterexample discrimination"],promotionGuard:"No deterministic pivot/window inferred from backtest",canonicalEligible:false},
{id:"B10",family:"F10_STOP",priority:"P0",evidenceNeeded:["source-confirmed stop field","buffer semantics if any","touch/breach/close invalidation"],promotionGuard:"No stop anchor selected by performance",canonicalEligible:false},
{id:"B09",family:"F09_ENTRY",priority:"P1",evidenceNeeded:["entry price field","trigger candle precedence","pending-limit semantics"],promotionGuard:"No trigger/entry convention promoted from implementation",canonicalEligible:false},
{id:"B14",family:"F14_ABCD",priority:"P1",evidenceNeeded:["A/B/C/D anchors","leg measurement fields","source-supported tolerance or unresolved declaration"],promotionGuard:"No numeric tolerance optimized from data",canonicalEligible:false},
{id:"B11F12",family:"F11_F12_EXECUTION",priority:"P1",evidenceNeeded:["place/refresh/delete/replace/cancel lifecycle","activation event","touch/breach/close/fill distinction"],promotionGuard:"No fill semantics invented",canonicalEligible:false},
{id:"B13",family:"F13_2X",priority:"P1",evidenceNeeded:["relation retained","lifecycle","risk/sizing","shared SL/TP behavior"],promotionGuard:"Only source-confirmed relation may be retained",canonicalEligible:false},
{id:"B15",family:"F15_BEARISH",priority:"P2",evidenceNeeded:["independent bearish P-Gap source evidence","bearish executable geometry","symmetry counterexample"],promotionGuard:"Source-consistent mirror is not treated as source-proven",canonicalEligible:false},
];
