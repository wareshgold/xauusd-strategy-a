"""Offline recovery and delivery fixtures for multi-account research.

Pure Python contract only. No MT5, network, filesystem, Telegram, or Runner
imports. It classifies supplied synthetic observations; it does not define
broker fill, order-linkage, or execution semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import AbstractSet, Mapping

from scripts.sp2l_account_isolation_contract_research import (
    account_state_namespace,
    candidate_idempotency_key,
)


class StateStatus(str, Enum):
    MISSING = "missing"
    VALID = "valid"
    CORRUPT = "corrupt"
    INCOMPATIBLE = "incompatible"


class RecoveryDisposition(str, Enum):
    RESTORE = "restore"
    BOOTSTRAP_EMPTY = "bootstrap_empty"
    HALT = "halt"


class DeliveryDisposition(str, Enum):
    NEW = "new"
    DUPLICATE = "duplicate"


@dataclass(frozen=True)
class RecoveryObservation:
    """Explicit facts supplied by a caller; no I/O is performed here."""

    account_identity_verified: bool
    inventory_available: bool
    inventory_is_empty: bool
    event_journal_complete: bool
    linkage_ambiguous: bool = False


def classify_state_snapshot(
    *,
    exists: bool,
    parse_succeeded: bool,
    schema_version: int | None,
    expected_schema_version: int,
    payload_is_mapping: bool,
) -> StateStatus:
    """Classify state without silently converting errors into an empty state."""
    if not exists:
        return StateStatus.MISSING
    if not parse_succeeded or not payload_is_mapping:
        return StateStatus.CORRUPT
    if schema_version != expected_schema_version:
        return StateStatus.INCOMPATIBLE
    return StateStatus.VALID


def decide_recovery(
    state_status: StateStatus,
    observation: RecoveryObservation,
) -> RecoveryDisposition:
    """Fail closed on incomplete identity, inventory, journal, or linkage.

    Missing state permits an empty bootstrap only when a verified account has
    a complete event journal and a successfully observed empty inventory.
    Non-empty inventory with missing state is deliberately ambiguous.
    """
    if not observation.account_identity_verified:
        return RecoveryDisposition.HALT
    if not observation.inventory_available:
        return RecoveryDisposition.HALT
    if not observation.event_journal_complete:
        return RecoveryDisposition.HALT
    if observation.linkage_ambiguous:
        return RecoveryDisposition.HALT

    if state_status is StateStatus.VALID:
        return RecoveryDisposition.RESTORE
    if state_status is StateStatus.MISSING and observation.inventory_is_empty:
        return RecoveryDisposition.BOOTSTRAP_EMPTY
    return RecoveryDisposition.HALT


def account_event_key(account_key: str, event_id: str) -> str:
    """Return an account-scoped event identity; does not persist an event."""
    namespace = account_state_namespace(account_key)
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("event_id must be explicit and non-empty")
    if any(ord(char) < 32 for char in event_id):
        raise ValueError("event_id cannot contain control characters")
    return f"{namespace}/event/{event_id}"


def candidate_delivery_disposition(
    account_key: str,
    candidate_id: str,
    processed_keys: AbstractSet[str],
) -> DeliveryDisposition:
    """Classify duplicate delivery within one account namespace only."""
    key = candidate_idempotency_key(account_key, candidate_id)
    return (
        DeliveryDisposition.DUPLICATE
        if key in processed_keys
        else DeliveryDisposition.NEW
    )


def validate_event_namespace(
    account_key: str,
    event_keys: AbstractSet[str],
) -> bool:
    """Synthetic guard: every supplied event key belongs to the named account."""
    prefix = account_state_namespace(account_key) + "/event/"
    return all(isinstance(key, str) and key.startswith(prefix) for key in event_keys)
