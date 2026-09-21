from datetime import datetime
from zoneinfo import ZoneInfo

from scripts.sp2l_telegram_trade_formatter import (
    format_result_notification,
    format_signal_notification,
)


def test_signal_template_uses_tehran_time_and_excludes_internal_fields():
    at = datetime(2026, 9, 21, 6, 12, tzinfo=ZoneInfo("UTC"))
    message = format_signal_notification(
        direction="BUY",
        entry=4353.15,
        sl=4350.59,
        tp=4355.71,
        at=at,
    )
    assert message == """🟢 XAUUSD BUY

Entry: 4353.15
SL: 4350.59
TP: 4355.71

SL: -2.56
TP: +2.56

Time: 09:42
Date: 21/09/2026"""
    assert "Volume" not in message
    assert "Signal ID" not in message
    assert "Status" not in message


def test_result_template_reports_observed_exit_distance():
    at = datetime(2026, 9, 21, 6, 48, tzinfo=ZoneInfo("UTC"))
    message = format_result_notification(
        direction="BUY",
        entry=4353.15,
        exit_price=4355.71,
        outcome="TP",
        at=at,
    )
    assert message == """✅ XAUUSD BUY — TP

Entry: 4353.15
Exit: 4355.71

TP: +2.56
SL: +0.00

Time: 10:18
Date: 21/09/2026"""
