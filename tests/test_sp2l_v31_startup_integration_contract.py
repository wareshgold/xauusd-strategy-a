"""Cross-module startup/recovery/lifecycle/entry-lock contract tests.

These tests combine the pure recovery and exposure classifiers and inspect
runner control-flow wiring. They do not initialize MT5 or execute orders.
"""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.sp2l_v31_entry_guard import inspect_owned_exposure
from scripts.sp2l_v31_startup_recovery import recover_owned_broker_inventory
from scripts.sp2l_v31_startup_safety import inspect_account_inventory
from scripts.sp2l_v31_startup_failure_alert import report_startup_failure


ROOT = Path(__file__).resolve().parents[1]
BASE_RUNNER = ROOT / "scripts" / "run_sp2l_author_replica_multi_symbol_forward_test.py"
V31_RUNNER = ROOT / "scripts" / "run_sp2l_v3_1_xauusd_forward_test.py"
SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301
BUY_LIMIT = 2
SELL_LIMIT = 3


def broker_item(ticket, *, symbol=SYMBOL, magic=MAGIC, order_type=None):
    fields = {"ticket": ticket, "symbol": symbol, "magic": magic}
    if order_type is not None:
        fields["type"] = order_type
    return SimpleNamespace(**fields)


@pytest.mark.parametrize(
    ("orders", "positions", "expected_reason"),
    [
        ((broker_item(201, order_type=BUY_LIMIT),), (), "OWN_PENDING_ORDER_ACTIVE"),
        ((), (broker_item(301),), "OWN_POSITION_ACTIVE"),
        (
            (broker_item(201, order_type=SELL_LIMIT),),
            (broker_item(301),),
            "OWN_ORDER_AND_POSITION_ACTIVE",
        ),
        ((), (), "NO_OWN_EXPOSURE"),
    ],
)
def test_recovery_and_entry_guard_share_the_same_owned_inventory_contract(
    orders, positions, expected_reason
):
    state = {"orders": set(), "positions": set()}
    recover_owned_broker_inventory(
        state,
        symbol=SYMBOL,
        magic=MAGIC,
        orders=orders,
        positions=positions,
        buy_limit_type=BUY_LIMIT,
        sell_limit_type=SELL_LIMIT,
    )

    assert state["orders"] == {item.ticket for item in orders}
    assert state["positions"] == {item.ticket for item in positions}

    result = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=orders,
        positions=positions,
    )
    assert result["ok"] is True
    assert result["reason"] == expected_reason
    assert result["active"] is bool(orders or positions)


def test_entry_guard_only_reopens_after_both_owned_inventory_sets_are_empty():
    state = {"orders": set(), "positions": set()}
    owned_order = broker_item(401, order_type=BUY_LIMIT)
    owned_position = broker_item(501)

    recover_owned_broker_inventory(
        state,
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(owned_order,),
        positions=(owned_position,),
        buy_limit_type=BUY_LIMIT,
        sell_limit_type=SELL_LIMIT,
    )

    still_open = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(),
        positions=(owned_position,),
    )
    assert still_open["active"] is True

    fully_flat = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(),
        positions=(),
    )
    assert fully_flat["ok"] is True
    assert fully_flat["active"] is False
    assert fully_flat["reason"] == "NO_OWN_EXPOSURE"


def test_account_wide_foreign_inventory_is_not_mistaken_for_owned_recovery():
    foreign_order = broker_item(601, symbol="EURUSD", magic=77, order_type=BUY_LIMIT)
    result = inspect_account_inventory(
        orders=(foreign_order,),
        positions=(),
        owned_pairs={(SYMBOL, MAGIC)},
    )
    assert result["ok"] is False
    assert result["reason"] == "UNRECOGNIZED_ACCOUNT_INVENTORY"
    assert result["foreign_orders"][0]["ticket"] == 601


def _function(tree, name):
    return next(
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == name
    )


def _call_lines(function):
    found = {}
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            continue
        found.setdefault(name, []).append(node.lineno)
    return found


def test_initial_account_preflight_failure_hook_runs_before_start_and_polling():
    source = BASE_RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    main = _function(tree, "main")
    calls = _call_lines(main)

    account_query_line = min(calls["account_info"])
    notify_lines = calls["_notify_startup_failure"]
    start_event_line = next(
        node.lineno
        for node in ast.walk(main)
        if isinstance(node, ast.Dict)
        and any(
            isinstance(key, ast.Constant)
            and key.value == "event"
            and isinstance(value, ast.Constant)
            and value.value == "START"
            for key, value in zip(node.keys, node.values)
        )
    )
    polling_loop_line = next(
        node.lineno for node in ast.walk(main) if isinstance(node, ast.While)
    )
    assert notify_lines
    assert min(notify_lines) > account_query_line
    assert max(notify_lines) < start_event_line < polling_loop_line
    assert "startup_failure_hook" in source


@pytest.mark.parametrize(
    ("log_raises", "alert_raises", "expected_logged", "expected_alerted"),
    [
        (False, False, True, True),
        (True, False, False, True),
        (False, True, True, False),
        (True, True, False, False),
    ],
)
def test_startup_failure_notification_attempts_log_and_alert_independently(
    log_raises, alert_raises, expected_logged, expected_alerted
):
    events = []
    alerts = []

    def log_event(event):
        if log_raises:
            raise OSError("disk unavailable")
        events.append(event)

    def send_alert(message):
        if alert_raises:
            raise RuntimeError("telegram unavailable")
        alerts.append(message)
        return SimpleNamespace(success=True, detail="sent")

    result = report_startup_failure(
        reason="INITIAL_ACCOUNT_INFO_EXCEPTION",
        details={"query": "account_info"},
        version="TEST",
        send_alert=send_alert,
        log_event=log_event,
    )
    assert result["logged"] is expected_logged
    assert result["alerted"] is expected_alerted
    assert bool(alerts) is expected_alerted
    if expected_logged:
        assert events[0]["event"] == "STARTUP_INITIALIZATION_FAILED"


def test_base_runner_recovers_before_start_announcement_and_polling_loop():
    source = BASE_RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    main = _function(tree, "main")
    calls = _call_lines(main)

    recovery_call_line = min(calls["recovery_hook"])
    polling_loop_line = next(
        node.lineno for node in ast.walk(main) if isinstance(node, ast.While)
    )
    assert recovery_call_line < polling_loop_line

    start_event_line = next(
        node.lineno
        for node in ast.walk(main)
        if isinstance(node, ast.Dict)
        and any(
            isinstance(key, ast.Constant)
            and key.value == "event"
            and isinstance(value, ast.Constant)
            and value.value == "START"
            for key, value in zip(node.keys, node.values)
        )
    )
    assert recovery_call_line < start_event_line


def test_base_poll_manages_existing_inventory_before_candidate_entry_path():
    source = BASE_RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    main = _function(tree, "main")
    calls = _call_lines(main)

    lifecycle = [
        min(calls[name])
        for name in (
            "enforce_pending_order_expiry",
            "monitor_pending_order_lifecycle",
            "monitor_position_lifecycle",
            "monitor_symbol_lifecycle",
        )
    ]
    assert max(lifecycle) < min(calls["rates"])
    assert max(lifecycle) < min(calls["find_latest_candidate"])
    assert max(lifecycle) < min(calls["execute_candidate"])


def test_v31_wires_recovery_entry_guard_and_trailing_manager_into_base_runner():
    source = V31_RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assignments = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "runner"
        ):
            assignments[target.attr] = node.value

    assert "startup_recovery_hook" in assignments
    assert "startup_failure_hook" in assignments
    assert isinstance(assignments["startup_failure_hook"], ast.Name)
    assert assignments["startup_failure_hook"].id == "_v31_initial_startup_failure"
    assert "execute_candidate" in assignments
    assert "monitor_position_lifecycle" in assignments
    assert isinstance(assignments["startup_recovery_hook"], ast.Name)
    assert assignments["startup_recovery_hook"].id == "_v31_startup_recovery"
    assert isinstance(assignments["execute_candidate"], ast.Name)
    assert assignments["execute_candidate"].id == "_guarded_execute_candidate"
    assert isinstance(assignments["monitor_position_lifecycle"], ast.Name)
    assert assignments["monitor_position_lifecycle"].id == "trail_positions"


def test_base_position_observer_accepts_recovered_ticket_even_if_magic_metadata_differs():
    source = BASE_RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    observer = _function(tree, "monitor_position_lifecycle")
    condition = next(
        node for node in ast.walk(observer)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.BoolOp)
        and isinstance(node.test.op, ast.And)
    )
    rendered = ast.unparse(condition.test)
    assert "position_magic != magic" in rendered
    assert "position_id not in state['positions']" in rendered

def test_startup_safety_block_uses_independent_alert_channel_and_specific_event():
    events = []
    alerts = []

    def log_event(event):
        if event.get("event") == "STARTUP_SAFETY_BLOCKED":
            raise OSError("event disk unavailable")
        events.append(event)

    def send_alert(message):
        alerts.append(message)
        return SimpleNamespace(success=True, detail="sent")

    result = report_startup_failure(
        reason="UNRECOGNIZED_ACCOUNT_INVENTORY",
        details={"inventory": "foreign"},
        version="TEST",
        send_alert=send_alert,
        log_event=log_event,
        event_name="STARTUP_SAFETY_BLOCKED",
        alert_heading="STARTUP BLOCKED",
        alert_instruction="No new orders will be submitted. Inspect the MT5 account inventory.",
    )

    assert result["logged"] is False
    assert result["alerted"] is True
    assert len(alerts) == 1
    assert "STARTUP BLOCKED" in alerts[0]
    assert "UNRECOGNIZED_ACCOUNT_INVENTORY" in alerts[0]
    assert "No new orders will be submitted" in alerts[0]
    assert events[0]["event"] == "STARTUP_INITIALIZATION_ALERT"

