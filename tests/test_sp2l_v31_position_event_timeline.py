from scripts.sp2l_v31_position_event_timeline import build_timeline

def test_event_timeline_keeps_trail_fields_and_broker_deal_rows():
    trades=[{
        "position_id":123,"side":"BUY","status":"CLOSED",
        "entry_time_utc":"2026-11-07T10:00:00+00:00",
        "exit_time_utc":"2026-11-07T10:04:00+00:00",
        "entry_price_volume_weighted":2000.0,"exit_price_volume_weighted":2001.0,
        "exit_reasons":"SL",
    }]
    events=[
        {"ts_utc":"2026-11-07T10:02:00+00:00","event":"TRAIL_UPDATE",
         "position":123,"direction":"BUY","success":True,"old_sl":1998.0,
         "new_sl":2000.2,"bar_high":2001.0,"bar_low":1999.5,"bid":2000.9,"ask":2001.1},
        {"ts_utc":"2026-11-07T10:01:00+00:00","event":"TRAIL_DEFERRED",
         "position":123,"direction":"BUY","reason":"CURRENT_QUOTE_OR_BROKER_DISTANCE"},
    ]
    rows, counts=build_timeline(events,trades)
    assert counts=={"TRAIL_UPDATE":1,"TRAIL_DEFERRED":1}
    assert [r["event_type"] for r in rows]==[
        "BROKER_ENTRY_DEAL","TRAIL_DEFERRED","TRAIL_UPDATE","BROKER_EXIT_DEAL"
    ]
    trail=next(r for r in rows if r["event_type"]=="TRAIL_UPDATE")
    assert trail["old_sl"]==1998.0 and trail["new_sl"]==2000.2
    assert trail["bar_high"]==2001.0 and trail["bar_low"]==1999.5

def test_missing_runner_timestamp_uses_completed_bar_time():
    rows, _=build_timeline([
        {"event":"TRAIL_UPDATE","position":7,"completed_bar_time":1794045600,
         "success":False,"new_sl":2010.0}
    ],[])
    assert rows[0]["time_basis"]=="completed_bar_time"
    assert rows[0]["timestamp_utc"] is not None


def test_explicit_broker_offset_preserves_raw_time_and_never_shifts_runner_time():
    rows, _ = build_timeline(
        [{"ts_utc":"2026-11-07T10:02:00+00:00","event":"TRAIL_DEFERRED","position":123}],
        [{
            "position_id":123,"side":"BUY","status":"CLOSED",
            "entry_time_utc":"2026-11-07T10:00:00+00:00",
            "exit_time_utc":"2026-11-07T10:04:00+00:00",
        }],
        broker_server_offset_hours=2,
    )
    entry = next(r for r in rows if r["event_type"] == "BROKER_ENTRY_DEAL")
    runner = next(r for r in rows if r["event_type"] == "TRAIL_DEFERRED")
    assert entry["timestamp_raw"] == "2026-11-07T10:00:00+00:00"
    assert entry["timestamp_utc"] == "2026-11-07T08:00:00+00:00"
    assert entry["broker_offset_hours"] == 2
    assert runner["timestamp_utc"] == "2026-11-07T10:02:00+00:00"
    assert runner["broker_offset_hours"] is None
