from types import SimpleNamespace

import pytest

from scripts.sp2l_v31_startup_safety import (
    inspect_account_identity,
    inspect_account_inventory,
)


def item(ticket, symbol="XAUUSD.ecn", magic=26092301):
    return SimpleNamespace(ticket=ticket, symbol=symbol, magic=magic)


def test_account_identity_requires_exact_login_and_server():
    account = SimpleNamespace(login=123456, server="OtetGroup-MT5")
    assert inspect_account_identity(
        account=account,
        expected_login="123456",
        expected_server="OtetGroup-MT5",
    ) == {"ok": True, "reason": "ACCOUNT_IDENTITY_MATCH"}


@pytest.mark.parametrize(
    ("expected_login", "expected_server", "reason"),
    [
        ("", "OtetGroup-MT5", "EXPECTED_ACCOUNT_IDENTITY_NOT_CONFIGURED"),
        ("123456", "", "EXPECTED_ACCOUNT_IDENTITY_NOT_CONFIGURED"),
        ("999999", "OtetGroup-MT5", "ACCOUNT_LOGIN_MISMATCH"),
        ("123456", "Other-Server", "ACCOUNT_SERVER_MISMATCH"),
    ],
)
def test_account_identity_mismatch_fails_closed(expected_login, expected_server, reason):
    result = inspect_account_identity(
        account=SimpleNamespace(login=123456, server="OtetGroup-MT5"),
        expected_login=expected_login,
        expected_server=expected_server,
    )
    assert result == {"ok": False, "reason": reason}


def test_missing_account_info_fails_closed():
    assert inspect_account_identity(
        account=None, expected_login="123456", expected_server="OtetGroup-MT5"
    ) == {"ok": False, "reason": "ACCOUNT_INFO_UNAVAILABLE"}


def test_account_inventory_accepts_only_configured_owned_pair():
    result = inspect_account_inventory(
        orders=(item(101),),
        positions=(item(202),),
        owned_pairs={("XAUUSD.ecn", 26092301)},
    )
    assert result["ok"] is True
    assert result["reason"] == "ACCOUNT_INVENTORY_RECOGNIZED"
    assert result["foreign_orders"] == []
    assert result["foreign_positions"] == []


@pytest.mark.parametrize(
    ("orders", "positions", "failed"),
    [
        (None, (), ["orders"]),
        ((), None, ["positions"]),
        (None, None, ["orders", "positions"]),
    ],
)
def test_account_inventory_query_failure_is_not_empty(orders, positions, failed):
    result = inspect_account_inventory(
        orders=orders,
        positions=positions,
        owned_pairs={("XAUUSD.ecn", 26092301)},
    )
    assert result["ok"] is False
    assert result["reason"] == "BROKER_INVENTORY_UNAVAILABLE"
    assert result["failed_queries"] == failed


@pytest.mark.parametrize(
    "foreign",
    [
        item(303, symbol="EURUSD", magic=26092301),
        item(304, symbol="XAUUSD.ecn", magic=777),
    ],
)
def test_foreign_manual_or_other_strategy_inventory_blocks_startup(foreign):
    result = inspect_account_inventory(
        orders=(foreign,),
        positions=(),
        owned_pairs={("XAUUSD.ecn", 26092301)},
    )
    assert result["ok"] is False
    assert result["reason"] == "UNRECOGNIZED_ACCOUNT_INVENTORY"
    assert result["foreign_orders"] == [{
        "symbol": foreign.symbol,
        "magic": foreign.magic,
        "ticket": foreign.ticket,
    }]


@pytest.mark.parametrize(
    "malformed",
    [
        SimpleNamespace(ticket=1, magic=26092301),
        SimpleNamespace(ticket=1, symbol="XAUUSD.ecn"),
        SimpleNamespace(ticket=0, symbol="XAUUSD.ecn", magic=26092301),
    ],
)
def test_incomplete_account_inventory_fails_loudly(malformed):
    with pytest.raises(ValueError):
        inspect_account_inventory(
            orders=(malformed,),
            positions=(),
            owned_pairs={("XAUUSD.ecn", 26092301)},
        )


def test_duplicate_account_inventory_ticket_fails_loudly():
    with pytest.raises(ValueError, match="duplicate account inventory orders ticket"):
        inspect_account_inventory(
            orders=(item(501), item(501)),
            positions=(),
            owned_pairs={("XAUUSD.ecn", 26092301)},
        )
