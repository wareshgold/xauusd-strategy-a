"""Deterministic research wrapper for the preserved legacy author-replica XAUUSD replay."""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEGACY=ROOT/'scripts'/'run-author-replica-mt5-api.py'
def main():
 import argparse
 p=argparse.ArgumentParser(); p.add_argument('--start',required=True); p.add_argument('--end',required=True); p.add_argument('--mt5-path',required=True); p.add_argument('--output',default='artifacts/author-replica-legacy-20260928.json'); a=p.parse_args()
 env=os.environ.copy(); env.update({'TRADING_SYMBOL':'XAUUSD.ecn','PGAP_PRICE':'1.0','SPIKE_MULTIPLIER':'1.5','MAX_SL_PRICE':'10.0','TP_R':'1.0','MT5_TERMINAL_PATH':a.mt5_path})
 cmd=[sys.executable,str(LEGACY),'--start',a.start,'--end',a.end,'--output',a.output]
 print('LEGACY_AUTHOR_REPLICA symbol=XAUUSD.ecn pGap=1.0 spike=1.5 maxSL=10.0 tpR=1.0',flush=True)
 return subprocess.run(cmd,env=env).returncode
if __name__=='__main__': raise SystemExit(main())
