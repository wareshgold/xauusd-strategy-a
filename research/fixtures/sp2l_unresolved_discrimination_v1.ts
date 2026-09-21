export type ResolutionStatus = "UNRESOLVED";

export interface DiscriminationCase {
  id: string;
  family: "PGAP"|"F08"|"F09"|"F10"|"F11"|"F12"|"F13"|"F14"|"F15";
  hypothesisA: string;
  hypothesisB: string;
  expectedStatus: ResolutionStatus;
  canonicalEligible: false;
}

export const SP2L_UNRESOLVED_DISCRIMINATION_FIXTURES: DiscriminationCase[] = [
  {id:"PGAP-EDGE-001",family:"PGAP",hypothesisA:"strict adjacent non-overlap",hypothesisB:"equality accepted",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"PGAP-EDGE-002",family:"PGAP",hypothesisA:"early-trend pressure gap",hypothesisB:"same geometry after repeated extension",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F08-EDGE-001",family:"F08",hypothesisA:"structural turning area",hypothesisB:"fixed pivot window",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F08-EDGE-002",family:"F08",hypothesisA:"wick extreme",hypothesisB:"body endpoint",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F09-EDGE-001",family:"F09",hypothesisA:"pending-limit price field",hypothesisB:"reclaim/trigger price field",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F09-EDGE-002",family:"F09",hypothesisA:"single-candle trigger",hypothesisB:"two/three-candle family",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F10-EDGE-001",family:"F10",hypothesisA:"spike-origin wick extreme",hypothesisB:"spike-origin body field",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F10-EDGE-002",family:"F10",hypothesisA:"touch invalidation",hypothesisB:"breach/close invalidation",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F11-EDGE-001",family:"F11",hypothesisA:"delete on invalidation",hypothesisB:"replace after refreshed structure",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F11-EDGE-002",family:"F11",hypothesisA:"time-based expiry",hypothesisB:"structure-based expiry",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F12-EDGE-001",family:"F12",hypothesisA:"touch activates trigger",hypothesisB:"close/breach activates trigger",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F12-EDGE-002",family:"F12",hypothesisA:"trigger event equals fill",hypothesisB:"trigger and fill are distinct",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F13-EDGE-001",family:"F13",hypothesisA:"50% relation to original Entry/SL",hypothesisB:"50% relation after refresh",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F13-EDGE-002",family:"F13",hypothesisA:"2X optional secondary entry",hypothesisB:"2X mandatory sizing/lifecycle",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F14-EDGE-001",family:"F14",hypothesisA:"structural swing A/B/C/D",hypothesisB:"spike/candle OHLC A/B/C/D",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F14-EDGE-002",family:"F14",hypothesisA:"exact AB=CD equality",hypothesisB:"unspecified approximate equality tolerance",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F15-EDGE-001",family:"F15",hypothesisA:"independently sourced bearish geometry",hypothesisB:"synthetic bullish-to-bearish mirror",expectedStatus:"UNRESOLVED",canonicalEligible:false},
  {id:"F15-EDGE-002",family:"F15",hypothesisA:"bearish trigger directly evidenced",hypothesisB:"bearish trigger inferred by symmetry",expectedStatus:"UNRESOLVED",canonicalEligible:false},
];
