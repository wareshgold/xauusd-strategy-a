import type { Candle } from '../domain/market/Candle.js';
import type { BacktestMetrics, BacktestResult, BacktestTrade } from './BacktestTypes.js';

export interface BacktestCandidate {
  readonly entryIndex:number;
  readonly entryTime:string;
  readonly direction:'BUY'|'SELL';
  readonly entry:number;
  readonly stopLoss:number;
  readonly tp1:number;
  readonly tp2?:number;
  readonly session?:string;
  readonly qualityGrade?:'A'|'B'|'C';
  readonly qualityScore?:number;
  readonly structureScore?:number;
  readonly overlapScore?:number;
  readonly hasPGAPEvidence?:boolean;
  readonly nearRoundLevel?:boolean;
  readonly emaAligned?:boolean;
}

function evaluate(candidate: BacktestCandidate, candles: readonly Candle[]): BacktestTrade {
  const risk=Math.abs(candidate.entry-candidate.stopLoss); if(risk<=0) throw new Error('Backtest candidate risk must be positive');
  for(let i=candidate.entryIndex+1;i<candles.length;i++){
    const c=candles[i]!;
    const sl=candidate.direction==='BUY'?c.low<=candidate.stopLoss:c.high>=candidate.stopLoss;
    const tp1=candidate.direction==='BUY'?c.high>=candidate.tp1:c.low<=candidate.tp1;
    const tp2=candidate.tp2===undefined?false:candidate.direction==='BUY'?c.high>=candidate.tp2:c.low<=candidate.tp2;
    if(sl&&(tp1||tp2)) return {...candidate,tp2:candidate.tp2??null,riskDistance:risk,result:'AMBIGUOUS',rMultiple:null};
    if(sl) return {...candidate,tp2:candidate.tp2??null,riskDistance:risk,result:'SL',rMultiple:-1};
    if(tp2) return {...candidate,tp2:candidate.tp2??null,riskDistance:risk,result:'TP2',rMultiple:Math.abs(candidate.tp2!-candidate.entry)/risk};
    if(tp1) return {...candidate,tp2:candidate.tp2??null,riskDistance:risk,result:'TP1',rMultiple:Math.abs(candidate.tp1-candidate.entry)/risk};
  }
  return {...candidate,tp2:candidate.tp2??null,riskDistance:risk,result:'OPEN',rMultiple:null};
}

function calculateMetrics(trades: readonly BacktestTrade[]): BacktestMetrics {
  const closed=trades.filter(t=>t.rMultiple!==null); const wins=closed.filter(t=>t.rMultiple!>0); const losses=closed.filter(t=>t.rMultiple!<0);
  const sumR=closed.reduce((s,t)=>s+t.rMultiple!,0); const grossWin=wins.reduce((s,t)=>s+t.rMultiple!,0); const grossLoss=Math.abs(losses.reduce((s,t)=>s+t.rMultiple!,0));
  let equity=0,peak=0,maxDD=0,streak=0,maxStreak=0; for(const t of closed){equity+=t.rMultiple!;peak=Math.max(peak,equity);maxDD=Math.max(maxDD,peak-equity);streak=t.rMultiple!<0?streak+1:0;maxStreak=Math.max(maxStreak,streak);}
  return {trades:closed.length,wins:wins.length,losses:losses.length,winRate:closed.length?wins.length/closed.length:0,averageR:closed.length?sumR/closed.length:0,expectancyR:closed.length?sumR/closed.length:0,profitFactor:grossLoss?grossWin/grossLoss:null,maxDrawdownR:maxDD,consecutiveLosses:maxStreak};
}

export function runBacktest(candles: readonly Candle[], candidates: readonly BacktestCandidate[]): BacktestResult {
  const valid=candidates.filter(c=>c.entryIndex>=0&&c.entryIndex<candles.length);
  const trades=valid.map(c=>evaluate(c,candles));
  return {trades,metrics:calculateMetrics(trades)};
}
