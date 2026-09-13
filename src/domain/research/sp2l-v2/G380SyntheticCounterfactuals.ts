/** G380 research-only counterfactual executor. Every formula is a named hypothesis encoding, not a Strategy A rule. */
export interface Ohlc { open:number; high:number; low:number; close:number; }
export type G380Family='PGAP'|'ABCD'|'ENTRY'|'SL'|'TP';
export interface G380Fixture{id:string;family:G380Family;bars:readonly Ohlc[];hypothesisA:string;hypothesisB:string;expected:'DISTINCT'|'EQUIVALENT';canonical:false;}
export interface G380Observation{id:string;family:G380Family;hypothesisA:string;hypothesisB:string;outputA:number|boolean;outputB:number|boolean;classification:'DISTINCT'|'EQUIVALENT';canonical:false;}
const bodyHigh=(b:Ohlc)=>Math.max(b.open,b.close); const bodyLow=(b:Ohlc)=>Math.min(b.open,b.close);
function pgH01(b:readonly Ohlc[]):boolean{return b.length>=3&&b[2]!.low>b[0]!.high;}
function pgH02(b:readonly Ohlc[]):boolean{return b.length>=3&&b[0]!.close>b[0]!.open&&b[1]!.close>b[1]!.open&&b[2]!.low>b[0]!.high;}
function pgH03(b:readonly Ohlc[]):boolean{return b.length>=3&&b[2]!.low>b[0]!.high;}
function pgH04(b:readonly Ohlc[]):boolean{return b.length>=3&&b[2]!.low>b[0]!.high&&b[1]!.low>b[0]!.low;}
function abcdH01(b:readonly Ohlc[]):number{return b.length<2?0:b[1]!.high-b[0]!.low;}
function abcdH02(b:readonly Ohlc[]):number{return b.length<2?0:bodyHigh(b[1]!)-bodyLow(b[0]!);}
function abcdH03(b:readonly Ohlc[]):number{return b.length<2?0:b[1]!.close-b[0]!.close;}
function enH01(b:readonly Ohlc[]):number{return b.length<1?0:b[0]!.low;}
function enH02(b:readonly Ohlc[]):number{return b.length<2?0:b[1]!.low;}
function enH03(b:readonly Ohlc[]):number{return b.length<1?0:(b[0]!.low+b[0]!.high)/2;}
function slH01(b:readonly Ohlc[]):number{return b.length===0?0:b[0]!.low;}
function slH02(b:readonly Ohlc[]):number{return b.length===0?0:bodyLow(b[0]!);}
function tpH01(b:readonly Ohlc[]):number{return b.length<3?0:b[2]!.close+(b[1]!.high-b[0]!.low);}
function tpH04(b:readonly Ohlc[]):number{if(b.length<3)return 0;const e=b[2]!.close;return e+(e-b[0]!.low);}
export const G380_FIXTURES:readonly G380Fixture[]=[
{id:'G380-PG-01',family:'PGAP',bars:[{open:100,high:102,low:99,close:101},{open:101,high:103,low:100,close:102},{open:103,high:106,low:104,close:105}],hypothesisA:'PG-H01',hypothesisB:'PG-H02',expected:'EQUIVALENT',canonical:false},
{id:'G380-PG-02',family:'PGAP',bars:[{open:100,high:102,low:99,close:101},{open:101,high:103,low:100,close:102},{open:103,high:106,low:104,close:105}],hypothesisA:'PG-H01',hypothesisB:'PG-H03',expected:'EQUIVALENT',canonical:false},
{id:'G380-PG-03',family:'PGAP',bars:[{open:100,high:102,low:99,close:101},{open:98,high:100,low:96,close:99},{open:103,high:106,low:104,close:105}],hypothesisA:'PG-H03',hypothesisB:'PG-H04',expected:'DISTINCT',canonical:false},
{id:'G380-AB-01',family:'ABCD',bars:[{open:100,high:102,low:95,close:101},{open:101,high:110,low:100,close:108}],hypothesisA:'ABCD-H01',hypothesisB:'ABCD-H02',expected:'DISTINCT',canonical:false},
{id:'G380-AB-02',family:'ABCD',bars:[{open:100,high:102,low:95,close:101},{open:101,high:110,low:100,close:108}],hypothesisA:'ABCD-H02',hypothesisB:'ABCD-H03',expected:'DISTINCT',canonical:false},
{id:'G380-EN-01',family:'ENTRY',bars:[{open:100,high:104,low:96,close:103},{open:103,high:105,low:98,close:99}],hypothesisA:'EN-H01',hypothesisB:'EN-H02',expected:'DISTINCT',canonical:false},
{id:'G380-EN-02',family:'ENTRY',bars:[{open:100,high:104,low:96,close:103},{open:103,high:105,low:98,close:99}],hypothesisA:'EN-H02',hypothesisB:'EN-H03',expected:'DISTINCT',canonical:false},
{id:'G380-SL-01',family:'SL',bars:[{open:100,high:104,low:96,close:103}],hypothesisA:'SL-H01',hypothesisB:'SL-H02',expected:'DISTINCT',canonical:false},
{id:'G380-TP-01',family:'TP',bars:[{open:100,high:102,low:95,close:101},{open:101,high:110,low:100,close:108},{open:108,high:112,low:106,close:109}],hypothesisA:'TP-H01',hypothesisB:'TP-H04',expected:'DISTINCT',canonical:false},
{id:'G380-TP-02',family:'TP',bars:[{open:100,high:102,low:99,close:101},{open:101,high:103,low:100,close:102},{open:102,high:104,low:101,close:103}],hypothesisA:'TP-H01',hypothesisB:'TP-H04',expected:'EQUIVALENT',canonical:false}];
function evaluate(f:G380Fixture,h:string):number|boolean{switch(h){case'PG-H01':return pgH01(f.bars);case'PG-H02':return pgH02(f.bars);case'PG-H03':return pgH03(f.bars);case'PG-H04':return pgH04(f.bars);case'ABCD-H01':return abcdH01(f.bars);case'ABCD-H02':return abcdH02(f.bars);case'ABCD-H03':return abcdH03(f.bars);case'EN-H01':return enH01(f.bars);case'EN-H02':return enH02(f.bars);case'EN-H03':return enH03(f.bars);case'SL-H01':return slH01(f.bars);case'SL-H02':return slH02(f.bars);case'TP-H01':return tpH01(f.bars);case'TP-H04':return tpH04(f.bars);default:throw new Error(`Unsupported research hypothesis: ${h}`);}}
export function runG380():readonly G380Observation[]{return G380_FIXTURES.map(f=>{const a=evaluate(f,f.hypothesisA),b=evaluate(f,f.hypothesisB);return{id:f.id,family:f.family,hypothesisA:f.hypothesisA,hypothesisB:f.hypothesisB,outputA:a,outputB:b,classification:Object.is(a,b)?'EQUIVALENT':'DISTINCT',canonical:false};});}
export function g380ExpectedClassificationsMatch():boolean{return runG380().every(r=>G380_FIXTURES.find(f=>f.id===r.id)?.expected===r.classification);}
export function g380AllNonCanonical():boolean{return G380_FIXTURES.every(f=>f.canonical===false)&&runG380().every(r=>r.canonical===false);}
