from types import SimpleNamespace

import pytest

from scripts.sp2l_v31_entry_guard import inspect_owned_exposure


SYMBOL = "XAUUSD.ecn"
MAGIC = 26092301


def broker_item(ticket, magic=MAGIC, symbol=SYMBOL):
    return SimpleNamespace(ticket=ticket, magic=magic, symbol=symbol)


def test_open_owned_position_blocks_new_entry():
    result = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(),
        positions=(broker_item(101),),
    )

    assert result["ok"] is True
    assert result["active"] is True
    assert result["reason"] == "OWN_POSITION_ACTIVE"
    assert result["position_tickets"] == [101]
    assert result["order_tickets"] == []


def test_owned_pending_order_blocks_new_entry():
    result = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(broker_item(202),),
        positions=(),
    )

    assert result["ok"] is True
    assert result["active"] is True
    assert result["reason"] == "OWN_PENDING_ORDER_ACTIVE"
    assert result["order_tickets"] == [202]


def test_owned_position_and_pending_order_both_block():
    result = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(broker_item(202),),
        positions=(broker_item(101),),
    )

    assert result["active"] is True
    assert result["reason"] == "OWN_ORDER_AND_POSITION_ACTIVE"
    assert result["order_tickets"] == [202]
    assert result["position_tickets"] == [101]


def test_empty_owned_inventory_allows_entry():
    result = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(),
        positions=(),
    )

    assert result["ok"] is True
    assert result["active"] is False
    assert result["reason"] == "NO_OWN_EXPOSURE"


def test_foreign_magic_or_symbol_does_not_count_as_v31_exposure():
    result = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=(
            broker_item(301, magic=999),
            broker_item(302, symbol="EURUSD"),
        ),
        positions=(broker_item(401, magic=999),),
    )

    assert result["ok"] is True
    assert result["active"] is False


@pytest.mark.parametrize(
    ("orders", "positions", "failed_queries"),
    [
        (None, (), ["orders"]),
        ((), None, ["positions"]),
        (None, None, ["orders", "positions"]),
    ],
)
def test_unknown_inventory_fails_closed(orders, positions, failed_queries):
    result = inspect_owned_exposure(
        symbol=SYMBOL,
        magic=MAGIC,
        orders=orders,
        positions=positions,
    )

    assert result["ok"] is False
    assert result["active"] is False
    assert result["reason"] == "BROKER_INVENTORY_UNAVAILABLE"
    assert result["failed_queries"] == failed_queries


def test_malformed_owned_inventory_fails_loudly():
    malformed = SimpleNamespace(ticket="not-a-ticket", magic=MAGIC, symbol=SYMBOL)

    with pytest.raises(ValueError, match="malformed broker inventory ticket"):
        inspect_owned_exposure(
            symbol=SYMBOL,
            magic=MAGIC,
            orders=(malformed,),
            positions=(),
        )


@pytest.mark.parametrize(
    "malformed",
    [
        SimpleNamespace(ticket=501, magic=MAGIC),
        SimpleNamespace(ticket=501, magic=MAGIC, symbol=""),
        SimpleNamespace(ticket=0, magic=MAGIC, symbol=SYMBOL),
        SimpleNamespace(ticket=-1, magic=MAGIC, symbol=SYMBOL),
        SimpleNamespace(ticket=501, magic=None, symbol=SYMBOL),
    ],
)
def test_incomplete_or_invalid_inventory_fails_loudly(malformed):
    with pytest.raises(ValueError):
        inspect_owned_exposure(
            symbol=SYMBOL,
            magic=MAGIC,
            orders=(malformed,),
            positions=(),
        )


def test_duplicate_owned_ticket_fails_loudly():
    with pytest.raises(ValueError, match="duplicate owned orders ticket"):
        inspect_owned_exposure(
            symbol=SYMBOL,
            magic=MAGIC,
            orders=(broker_item(601), broker_item(601)),
            positions=(),
        )
