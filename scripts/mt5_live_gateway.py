"""SP2L MT5 live gateway — infrastructure only.
This component may observe XAUUSD.ecn and execute an explicitly supplied signal.
It intentionally does NOT calculate Strategy A/SP2L signals.
LIVE_TRADING_ENABLED defaults to false.
"""
from __future__ import annotations
import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
import MetaTrader5 as mt5

SYMBOL=os.getenv("TRADING_SYMBOL","XAUUSD.ecn")
POLL_SECONDS=float(os.getenv("POLL_SECONDS","2"))
LIVE=os.getenv("LIVE_TRADING_ENABLED","false").lower()=="true"
MAGIC=int(os.getenv("MT5_MAGIC","26091901"))
JOURNAL=Path(os.getenv("LIVE_JOURNAL","artifacts/live_gateway_journal.jsonl"))
STATE=Path(os.getenv("LIVE_STATE","artifacts/live_gateway_state.json"))
TELEGRAM_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN","")
TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID","")

def now(): return datetime.now(timezone.utc).isoformat()
def log(event, **kw):
    JOURNAL.parent.mkdir(parents=True,exist_ok=True)
    with JOURNAL.open("a",encoding="utf-8") as f: f.write(json.dumps({"ts":now(),"event":event,**kw})+"\n")
def telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return False
    data=urllib.parse.urlencode({"chat_id":TELEGRAM_CHAT_ID,"text":text}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",data=data),timeout=10) as r:
            return 200 <= r.status < 300
    except Exception as e: log("telegram_error",error=str(e)); return False
def state():
    if not STATE.exists(): return {"processed_signal_ids":[]}
    return json.loads(STATE.read_text(encoding="utf-8"))
def save_state(s): STATE.write_text(json.dumps(s,indent=2),encoding="utf-8")
def market_snapshot():
    tick=mt5.symbol_info_tick(SYMBOL); info=mt5.symbol_info(SYMBOL)
    if tick is None or info is None: return None
    return {"symbol":SYMBOL,"bid":tick.bid,"ask":tick.ask,"time_utc":datetime.fromtimestamp(tick.time,timezone.utc).isoformat(),"spread":tick.ask-tick.bid,"trade_mode":int(info.trade_mode)}
def format_trade_message(signal,result):
    return ("SP2L Strategy A\nSignal ID: "+str(signal.get("signal_id"))+
            "\nDirection: "+str(signal.get("direction"))+
            "\nEntry: "+str(signal.get("entry"))+
            "\nSL: "+str(signal.get("sl"))+
            "\nTP: "+str(signal.get("tp"))+
            "\nVolume: "+str(signal.get("volume"))+
            "\nStatus: "+str(result.get("status"))+
            "\nMT5: "+SYMBOL+"\nTime: "+now())
def execute(signal):
    required={"signal_id","direction","entry","sl","tp","volume"}
    missing=required-set(signal)
    if missing: raise ValueError(f"missing fields: {sorted(missing)}")
    sid=str(signal["signal_id"]); s=state()
    if sid in s["processed_signal_ids"]:
        log("duplicate_signal_rejected",signal_id=sid); return {"status":"DUPLICATE_REJECTED","signal_id":sid}
    direction=str(signal["direction"]).upper()
    if direction not in ("BUY","SELL"): raise ValueError("direction must be BUY or SELL")
    tick=mt5.symbol_info_tick(SYMBOL)
    if tick is None: raise RuntimeError(f"tick unavailable: {mt5.last_error()}")
    price=tick.ask if direction=="BUY" else tick.bid
    request={"action":mt5.TRADE_ACTION_DEAL,"symbol":SYMBOL,"volume":float(signal["volume"]),
             "type":mt5.ORDER_TYPE_BUY if direction=="BUY" else mt5.ORDER_TYPE_SELL,
             "price":price,"sl":float(signal["sl"]),"tp":float(signal["tp"]),
             "deviation":int(signal.get("deviation",20)),"magic":MAGIC,
             "comment":f"SP2L:{sid}"[:31],"type_time":mt5.ORDER_TIME_GTC,
             "type_filling":mt5.ORDER_FILLING_IOC}
    if not LIVE:
        result={"status":"DRY_RUN","signal_id":sid,"request":request,"market":market_snapshot()}
        log("dry_run",**result); telegram(format_trade_message(signal,result)); return result
    result=mt5.order_send(request)
    if result is None: raise RuntimeError(f"order_send failed: {mt5.last_error()}")
    out={"status":"EXECUTED" if result.retcode==mt5.TRADE_RETCODE_DONE else "REJECTED","signal_id":sid,
         "retcode":result.retcode,"comment":result.comment,"order":result.order,"deal":result.deal,"price":result.price}
    s["processed_signal_ids"].append(sid); s["processed_signal_ids"]=s["processed_signal_ids"][-1000:]; save_state(s)
    log("order_result",**out); telegram(format_trade_message(signal,out)); return out
def main():
    if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        if not mt5.symbol_select(SYMBOL,True): raise SystemExit(f"symbol_select failed: {mt5.last_error()}")
        log("gateway_started",symbol=SYMBOL,live_trading_enabled=LIVE,magic=MAGIC)
        telegram(f"SP2L MT5 Gateway ONLINE\nSymbol: {SYMBOL}\nLive execution: {'ON' if LIVE else 'DRY-RUN'}")
        while True:
            snap=market_snapshot()
            if snap is not None: log("market_heartbeat",**snap)
            time.sleep(POLL_SECONDS)
    finally: mt5.shutdown()
if __name__=="__main__": main()
