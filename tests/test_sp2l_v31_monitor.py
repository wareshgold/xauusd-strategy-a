from __future__ import annotations
import importlib
import json
import sys
from types import SimpleNamespace

def load(monkeypatch, tmp_path):
    fake=SimpleNamespace(
        initialize=lambda path=None: True,
        shutdown=lambda: None,
        terminal_info=lambda: SimpleNamespace(connected=True, trade_allowed=True),
        account_info=lambda: SimpleNamespace(login=812930,server="OtetGroup-MT5",balance=994.32,equity=995.10),
        symbol_info_tick=lambda s: SimpleNamespace(bid=4189.66,ask=4189.84),
        orders_get=lambda symbol=None: [],
        positions_get=lambda symbol=None: [],
    )
    monkeypatch.setitem(sys.modules,"MetaTrader5",fake)
    sys.modules.pop("sp2l_v31_monitor",None)
    mod=importlib.import_module("sp2l_v31_monitor")
    monkeypatch.setattr(mod,"STATE_FILE",tmp_path/"state.json")
    monkeypatch.setattr(mod,"EVENTS",tmp_path/"events.jsonl")
    mod.STATE_FILE.write_text(json.dumps({"orders":[],"positions":[],"deals":[]}),encoding="utf-8")
    mod.EVENTS.write_text(json.dumps({"ts_utc":"2026-10-01T06:00:00+00:00","event":"TRAIL_UPDATE","symbol":"XAUUSD.ecn","success":True})+"\n",encoding="utf-8")
    return mod

def test_v31_monitor_is_read_only_and_renders(monkeypatch,tmp_path):
    mod=load(monkeypatch,tmp_path)
    page=mod.render()
    assert "SP2L V3.1" in page
    assert "RR2" in page and "Trail3" in page
    assert "4189.66" in page
    assert "TRAIL_UPDATE" in page
    assert "No XAUUSD.ecn pending orders" in page
