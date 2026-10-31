from __future__ import annotations

import pytest

from strategy_factory.fresh_holdout_authority import (
    AuthorityVerification,
    FreshHoldoutAuthorityError,
    require_verified_authority,
)
from strategy_factory.manifest import StrategyManifest
from strategy_factory.models import StrategyPassport
from strategy_factory.source_ledger import SourceResolutionLedger


def _inputs():
    manifest = StrategyManifest(strategy_id="SP2L-A", revision="M1")
    passport = StrategyPassport(
        strategy_id="SP2L-A",
        source_revision="M1",
        geometry_revision="GEOMETRY-REV",
        code_revision="CODE-REV",
        data_revision="DATA-REV",
        execution_model="RESEARCH_ONLY",
        parameter_set={},
    )
    return manifest, passport, SourceResolutionLedger()


class VerifiedStub:
    def __init__(self, *, source=True, geometry=True):
        self.source = source
        self.geometry = geometry

    def verify_source_authority(self, manifest, ledger):
        return AuthorityVerification(self.source, "source-approval://fixture")

    def verify_frozen_geometry(self, passport, manifest):
        return AuthorityVerification(self.geometry, "geometry-freeze://fixture")


def test_fresh_holdout_requires_trusted_verifier():
    manifest, passport, ledger = _inputs()
    with pytest.raises(FreshHoldoutAuthorityError, match="no trusted"):
        require_verified_authority(
            verifier=None,
            manifest=manifest,
            passport=passport,
            ledger=ledger,
            strategy_id="SP2L-A",
            manifest_revision="M1",
        )


def test_fresh_holdout_rejects_unverified_source_authority():
    manifest, passport, ledger = _inputs()
    with pytest.raises(FreshHoldoutAuthorityError, match="source authority is not verified"):
        require_verified_authority(
            verifier=VerifiedStub(source=False),
            manifest=manifest,
            passport=passport,
            ledger=ledger,
            strategy_id="SP2L-A",
            manifest_revision="M1",
        )


def test_fresh_holdout_rejects_unverified_geometry_freeze():
    manifest, passport, ledger = _inputs()
    with pytest.raises(FreshHoldoutAuthorityError, match="frozen geometry authority is not verified"):
        require_verified_authority(
            verifier=VerifiedStub(geometry=False),
            manifest=manifest,
            passport=passport,
            ledger=ledger,
            strategy_id="SP2L-A",
            manifest_revision="M1",
        )


def test_fresh_holdout_rejects_authority_identity_mismatch():
    manifest, passport, ledger = _inputs()
    with pytest.raises(FreshHoldoutAuthorityError, match="manifest revision"):
        require_verified_authority(
            verifier=VerifiedStub(),
            manifest=manifest,
            passport=passport,
            ledger=ledger,
            strategy_id="SP2L-A",
            manifest_revision="M2",
        )
