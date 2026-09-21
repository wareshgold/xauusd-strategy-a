"""Research-only MT5 forward-test Telegram outcome monitor.

Does not define strategy geometry. It watches MT5 history for orders/deals
created by the SP2L research forward runner and reports lifecycle outcomes.
Telegram credentials are read from TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID.
"""
from __future__ import annotations
import os,time
from datetime import datetime,timezone,timedelta
import MetaTrader5 as mt5
from telegram_client import send_telegram_message

SYMBOL=os.getenv("TRADING_SYMBOL","XAUUSD.ecn")
POLL_SECONDS=float(os.getenv("POLL_SECONDS","2"))
LOOKBACK_HOURS=int(os.getenv("FORWARD_MONITOR_LOOKBACK_HOURS","24"))
MAGIC=int(os.getenv("MT5_MAGIC","26091901"))
seen=set()

def now(): return datetime.now(timezone.utc)
def notify(text):
    r=send_telegram_message(text)
    print({"telegram_success":r.success,"telegram_detail":r.detail})

def main():
    if not mt5.initialize(): raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        end=now(); start=end-timedelta(hours=LOOKBACK_HOURS)
        print({"telegram_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID")),
               "symbol":SYMBOL,"magic":MAGIC})
        while True:
            deals=mt5.history_deals_get(start,end) or []
            for d in deals:
                if str(d.symbol)!=SYMBOL or int(getattr(d,"magic",0))!=MAGIC: continue
                key=f"DEAL:{d.ticket}"
                if key in seen: continue
                seen.add(key)
                entry=int(getattr(d,"entry",-1)); reason=int(getattr(d,"reason",-1))
                notify(f"SP2L DEMO TRADE\nSymbol: {d.symbol}\nDeal: {d.ticket}\nOrder: {d.order}\nVolume: {d.volume}\nPrice: {d.price}\nProfit: {d.profit}\nEntryCode: {entry}\nReasonCode: {reason}\nTime UTC: {datetime.fromtimestamp(d.time,tz=timezone.utc).isoformat()}")
            end=now(); start=end-timedelta(hours=LOOKBACK_HOURS)
            time.sleep(POLL_SECONDS)
    finally: mt5.shutdown()

if __name__=="__main__": main()
