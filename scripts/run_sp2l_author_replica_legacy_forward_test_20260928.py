"""Research-only forward runner using preserved legacy author-replica geometry."""
from __future__ import annotations
import os
os.environ['SP2L_SYMBOLS']='XAUUSD'
os.environ['SP2L_P_GAP_PRICE']='1.0'
os.environ['SP2L_SPIKE_MULTIPLIER']='1.5'
os.environ['SP2L_MAX_SL_DISTANCE']='10.0'
os.environ['SP2L_TP_R']='1.0'
os.environ.setdefault('MT5_FORWARD_ORDER_MODE','PENDING_LIMIT_RESEARCH')
import run_sp2l_author_replica_multi_symbol_forward_test as runner
P_GAP_PRICE=1.0; SPIKE_MULTIPLIER=1.5; MAX_SL_DISTANCE=10.0; TP_R=1.0

def body(c): return abs(float(c['close'])-float(c['open']))

def legacy_signal(candles,i):
 if candles is None or i<4 or i>len(candles): return None
 a,spike,corr,trig=candles[i-4],candles[i-3],candles[i-2],candles[i-1]
 buy=(float(trig['low'])<float(corr['low']) and float(corr['close'])>float(spike['close']) and float(corr['open'])>float(spike['open']) and float(spike['open'])>float(a['open']) and float(corr['close'])>float(corr['open']) and float(spike['close'])>float(spike['open']) and float(a['close'])>float(a['open']) and float(corr['low'])>float(a['high'])+P_GAP_PRICE and body(spike)>SPIKE_MULTIPLIER*body(corr) and body(spike)>SPIKE_MULTIPLIER*body(a) and body(spike)>SPIKE_MULTIPLIER*body(trig))
 sell=(float(trig['high'])>float(corr['high']) and float(corr['close'])<float(spike['close']) and float(corr['open'])<float(spike['open']) and float(spike['close'])<float(a['close']) and float(spike['open'])<float(a['open']) and float(corr['close'])<float(corr['open']) and float(spike['close'])<float(spike['open']) and float(a['close'])<float(a['open']) and float(corr['high'])<float(a['low'])-P_GAP_PRICE and body(spike)>SPIKE_MULTIPLIER*body(corr) and body(spike)>SPIKE_MULTIPLIER*body(a) and body(spike)>SPIKE_MULTIPLIER*body(trig))
 if buy==sell: return None
 if buy:
  entry=float(trig['low']); sl=float(a['low']); risk=entry-sl
  if risk<=0 or risk>MAX_SL_DISTANCE: return None
  return {'direction':'BUY','trigger_time':int(trig['time']),'theoretical_entry':entry,'sl':sl,'risk':risk,'tp':entry+TP_R*risk,'symbol':None}
 entry=float(trig['high']); sl=float(a['high']); risk=sl-entry
 if risk<=0 or risk>MAX_SL_DISTANCE: return None
 return {'direction':'SELL','trigger_time':int(trig['time']),'theoretical_entry':entry,'sl':sl,'risk':risk,'tp':entry-TP_R*risk,'symbol':None}

def legacy_find_latest_candidate(candles,symbol):
 if candles is None or len(candles)<5: return None
 c=legacy_signal(candles,len(candles)-1)
 if c is None: return None
 c['symbol']=symbol
 return c
runner.find_latest_candidate=legacy_find_latest_candidate
if __name__=='__main__': runner.main()
