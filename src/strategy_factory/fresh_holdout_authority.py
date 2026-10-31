from __future__ import annotations

"""Trusted authority boundary for Fresh Holdout.

This module deliberately defines an interface, not source or geometry rules.
A verifier must be supplied by the trusted application composition root.
No caller-provided PASS flag, self-hashed snapshot, or free-form reference is
accepted as a substitute for independent source and geometry verification.
"""

from dataclasses import dataclass
from typing import Protocol

from .manifest import StrategyManifest
from .models import StrategyPassport
from .source_ledger import SourceResolutionLedger


@dataclass(frozen=True)
class AuthorityVerification:
    verified: bool
    authority_reference: str


class FreshHoldoutAuthorityVerifier(Protocol):
    """Trusted, independently configured verifier for Fresh Holdout inputs."""

    def verify_source_authority(
        self, manifest: StrategyManifest, ledger: SourceResolutionLedger
    ) -> AuthorityVerification:
        """Verify source evidence against an externally trusted authority."""

    def verify_frozen_geometry(
        self, passport: StrategyPassport, manifest: StrategyManifest
    ) -> AuthorityVerification:
        """Verify a frozen geometry artifact and its approval independently."""


class FreshHoldoutAuthorityError(RuntimeError):
    """Raised when trusted source or geometry authority cannot be established."""


def require_verified_authority(
    *,
    verifier: FreshHoldoutAuthorityVerifier | None,
    manifest: StrategyManifest | None,
    passport: StrategyPassport | None,
    ledger: SourceResolutionLedger | None,
    strategy_id: str,
    manifest_revision: str,
) -> tuple[AuthorityVerification, AuthorityVerification]:
    if verifier is None:
        raise FreshHoldoutAuthorityError(
            "Fresh Holdout is blocked: no trusted source/geometry authority verifier is configured"
        )
    if manifest is None or passport is None or ledger is None:
        raise FreshHoldoutAuthorityError(
            "Fresh Holdout requires Manifest, Passport, and Source Ledger inputs"
        )
    if manifest.strategy_id != strategy_id or passport.strategy_id != strategy_id:
        raise FreshHoldoutAuthorityError(
            "Fresh Holdout authority inputs do not match the strategy identity"
        )
    if manifest.revision != manifest_revision or passport.source_revision != manifest_revision:
        raise FreshHoldoutAuthorityError(
            "Fresh Holdout authority inputs do not match the frozen manifest revision"
        )

    try:
        source = verifier.verify_source_authority(manifest, ledger)
        geometry = verifier.verify_frozen_geometry(passport, manifest)
    except Exception as exc:
        raise FreshHoldoutAuthorityError(
            "trusted Fresh Holdout authority verification failed"
        ) from exc

    for label, result in (("source", source), ("frozen geometry", geometry)):
        if type(result) is not AuthorityVerification:
            raise FreshHoldoutAuthorityError(
                f"trusted {label} verifier returned an invalid verification result"
            )
        if (
            result.verified is not True
            or not isinstance(result.authority_reference, str)
            or not result.authority_reference.strip()
        ):
            raise FreshHoldoutAuthorityError(
                f"trusted {label} authority is not verified"
            )
    return source, geometry
