"""Offline broker-object ownership contract for multi-account research.

Pure Python only: no MT5, network, filesystem, Telegram, or Runner imports.
The caller must supply the account identity observed by its session adapter.
This module classifies synthetic/observed facts; it never queries or mutates a
broker account and deliberately does not infer order-to-position linkage.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from scripts.sp2l_account_isolation_contract_research import (
    AccountIdentity,
    ObservedAccountIdentity,
    assert_account_identity,
    account_state_namespace,
)


class BrokerObjectKind(str, Enum):
    ORDER = "order"
    POSITION = "position"


class BrokerObjectOwnershipError(RuntimeError):
    """Raised when an inventory object is malformed or ownership is ambiguous."""


@dataclass(frozen=True)
class BrokerObjectObservation:
    """Minimal broker-object facts needed for an ownership filter."""

    kind: BrokerObjectKind
    symbol: str
    magic: int
    ticket: int


@dataclass(frozen=True, order=True)
class BrokerObjectKey:
    """Account-scoped object key; order and position ticket spaces stay distinct."""

    account_key: str
    kind: BrokerObjectKind
    ticket: int

    @property
    def namespace(self) -> str:
        return broker_object_namespace(self.account_key, self.kind, self.ticket)


@dataclass(frozen=True)
class InventoryOwnershipResult:
    """Deterministic classification summary for one verified account snapshot."""

    owned_objects: tuple[BrokerObjectKey, ...]
    ignored_foreign_count: int
    duplicate_observations: int


def broker_object_namespace(
    account_key: str,
    kind: BrokerObjectKind,
    ticket: int,
) -> str:
    """Build a relative, account-scoped namespace for one broker object."""
    account_ns = account_state_namespace(account_key)
    if not isinstance(kind, BrokerObjectKind):
        raise ValueError("kind must be a BrokerObjectKind")
    if isinstance(ticket, bool) or not isinstance(ticket, int) or ticket <= 0:
        raise ValueError("ticket must be a positive integer")
    return f"{account_ns}/broker/{kind.value}/{ticket}"


def classify_broker_inventory(
    expected_identity: AccountIdentity,
    observed_identity: ObservedAccountIdentity,
    *,
    symbol: str,
    magic: int,
    objects: Iterable[BrokerObjectObservation],
) -> InventoryOwnershipResult:
    """Verify the session identity, then classify one account's inventory.

    Exact account identity is checked before looking at object metadata.
    Objects outside the requested symbol+magic scope are counted and ignored.
    Malformed objects or conflicting duplicate keys halt classification.
    The same numeric ticket may exist for an ORDER and a POSITION because the
    object kind is part of the key. No order.position_id/position.identifier
    equivalence or order-to-position linkage is inferred here.
    """
    assert_account_identity(expected_identity, observed_identity)

    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("symbol must be explicit and non-empty")
    if isinstance(magic, bool) or not isinstance(magic, int) or magic < 0:
        raise ValueError("magic must be a non-negative integer")

    seen: dict[BrokerObjectKey, BrokerObjectObservation] = {}
    owned: list[BrokerObjectKey] = []
    ignored_foreign_count = 0
    duplicate_observations = 0

    for item in objects:
        if not isinstance(item, BrokerObjectObservation):
            raise BrokerObjectOwnershipError("inventory contains an unsupported object record")
        if not isinstance(item.kind, BrokerObjectKind):
            raise BrokerObjectOwnershipError("inventory object kind is invalid")
        if not isinstance(item.symbol, str) or not item.symbol.strip():
            raise BrokerObjectOwnershipError("inventory object symbol is invalid")
        if isinstance(item.magic, bool) or not isinstance(item.magic, int) or item.magic < 0:
            raise BrokerObjectOwnershipError("inventory object magic is invalid")
        if isinstance(item.ticket, bool) or not isinstance(item.ticket, int) or item.ticket <= 0:
            raise BrokerObjectOwnershipError("inventory object ticket is invalid")

        key = BrokerObjectKey(
            account_key=expected_identity.account_key,
            kind=item.kind,
            ticket=item.ticket,
        )
        previous = seen.get(key)
        if previous is not None:
            if previous != item:
                raise BrokerObjectOwnershipError(
                    "conflicting duplicate broker-object key; inventory is ambiguous"
                )
            duplicate_observations += 1
            continue

        seen[key] = item
        if item.symbol == symbol and item.magic == magic:
            owned.append(key)
        else:
            ignored_foreign_count += 1

    owned.sort(key=lambda key: (key.kind.value, key.ticket))
    return InventoryOwnershipResult(
        owned_objects=tuple(owned),
        ignored_foreign_count=ignored_foreign_count,
        duplicate_observations=duplicate_observations,
    )
