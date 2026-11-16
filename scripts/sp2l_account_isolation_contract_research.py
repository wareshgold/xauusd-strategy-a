"""Offline research contract for strict per-account identity isolation.

Pure Python only: no MT5, network, filesystem, Telegram, or Runner imports.
This module validates identity labels and derives deterministic namespaces; it
does not connect accounts or execute/manage trades.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


_ACCOUNT_KEY = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")


@dataclass(frozen=True)
class AccountIdentity:
    """Expected non-secret account identity contract.

    login_ref is an opaque operator-managed identifier, not a raw account
    login, password, token, or other credential. Synthetic fixtures must be
    used in tests. Real values belong only in protected local configuration.
    """

    account_key: str
    broker: str
    server: str
    login_ref: str

    def validate(self) -> None:
        if not isinstance(self.account_key, str) or not _ACCOUNT_KEY.fullmatch(self.account_key):
            raise ValueError("account_key must be a lowercase namespace-safe identifier")
        for name, value in (
            ("broker", self.broker),
            ("server", self.server),
            ("login_ref", self.login_ref),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be explicit and non-empty")


@dataclass(frozen=True)
class ObservedAccountIdentity:
    """Identity facts observed from an adapter boundary; no secrets."""

    broker: str
    server: str
    login_ref: str


class AccountIdentityMismatch(RuntimeError):
    """Raised when the connected account does not match its configured owner."""


def assert_account_identity(
    expected: AccountIdentity,
    observed: ObservedAccountIdentity,
) -> None:
    """Fail closed unless all configured identity fields match exactly."""
    expected.validate()
    actual = {
        "broker": observed.broker,
        "server": observed.server,
        "login_ref": observed.login_ref,
    }
    mismatches = [
        field
        for field in ("broker", "server", "login_ref")
        if actual[field] != getattr(expected, field)
    ]
    if mismatches:
        # Field names only; never include observed or expected identity values.
        raise AccountIdentityMismatch(
            "connected account identity mismatch: " + ", ".join(mismatches)
        )


def account_state_namespace(account_key: str) -> str:
    """Return a deterministic relative namespace, never an absolute path."""
    if not isinstance(account_key, str) or not _ACCOUNT_KEY.fullmatch(account_key):
        raise ValueError("account_key must be a lowercase namespace-safe identifier")
    return f"accounts/{account_key}"


def candidate_idempotency_key(account_key: str, candidate_id: str) -> str:
    """Scope candidate deduplication to one account, never across accounts."""
    namespace = account_state_namespace(account_key)
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be explicit and non-empty")
    if any(ord(char) < 32 for char in candidate_id):
        raise ValueError("candidate_id cannot contain control characters")
    return f"{namespace}/candidate/{candidate_id}"
