from __future__ import annotations

"""Run one real, research-only SP2L Discovery Factory job against MT5."""

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from strategy_factory.datasets import DatasetRegistry
from strategy_factory.discovery_factory import DiscoveryFactory, DiscoveryFactoryContext
from strategy_factory.evidence import EvidenceLedger
from strategy_factory.models import StrategyPassport
from strategy_factory.passport_gate import evaluate_passport_eligibility
from strategy_factory.research_record import ResearchRecordLedger
from strategy_factory.runs import ResearchRunLedger
from strategy_factory.snapshot import build_readiness_snapshot
from strategy_factory.source_ledger import SourceResolutionLedger
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest
from strategy_factory.test_contract import ExecutionSemantics, HistoricalTestSpec, TestDataset, DatasetRole
from strategy_factory.usage import DatasetUsageLedger
from strategy_factory.runner import ResearchJobRunner


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mt5-path", required=True)
    parser.add_argument("--python-executable", required=True)
    parser.add_argument("--start", default="2026-09-24T07:57:00+00:00")
    parser.add_argument("--end", default="2026-10-23T23:57:00+00:00")
    parser.add_argument("--variant", default="RR2_ACT10_D2")
    parser.add_argument("--source-m1-artifact", default=r"D:\Mirzaei\Private\1\sp2l-mt5-market-data\20261024T075827Z\xauusd_ecn_m1_30d.csv")
    parser.add_argument("--source-m1-sha256", default="B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285")
    parser.add_argument("--entry-population-artifact", default="artifacts/monthly_ohlc_activated_sensitivity_v3_20261024_162634_105/a_trail_0_40_activated_proxy_v3_trades.csv")
    parser.add_argument("--entry-population-sha256", default="39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1")
    parser.add_argument("--data-revision", default="MT5-M1-30D-20261024-B0782E716C7E")
    parser.add_argument(
        "--artifact",
        default="artifacts/factory/mt5_m1_30d_20260924_20261023.json",
    )
    parser.add_argument(
        "--job-id",
        default="SP2L-DISCOVERY-V3-FROZEN-ENTRIES-20261024-RR2_ACT10_D2",
    )
    args = parser.parse_args()

    repo_root = REPO_ROOT
    manifest = build_sp2l_research_manifest()
    ledger = SourceResolutionLedger()
    passport = StrategyPassport(
        strategy_id=manifest.strategy_id,
        source_revision=manifest.revision,
        geometry_revision="UNRESOLVED-SOURCE-GEOMETRY",
        code_revision="SP2L-V3-CONTROLLED-DISCOVERY-20261007",
        data_revision=args.data_revision,
        execution_model="BAR_CLOSE_RESEARCH",
        parameter_set={"research_only": True},
        canonical=False,
    )
    readiness = build_readiness_snapshot(manifest, passport, ledger)
    eligibility = evaluate_passport_eligibility(passport, manifest, ledger)

    dataset = TestDataset(
        dataset_id=f"MT5-XAUUSD-ECN-M1-{args.data_revision}",
        role=DatasetRole.DEVELOPMENT,
        data_revision=args.data_revision,
        start=args.start,
        end=args.end,
        source="MT5:XAUUSD.ecn:M1",
        immutable=False,
    )
    spec = HistoricalTestSpec(
        test_id=f"SP2L_DISCOVERY_{args.variant}_MT5_20261024",
        strategy_id=manifest.strategy_id,
        strategy_revision=manifest.revision,
        dataset=dataset,
        execution_semantics=ExecutionSemantics.BAR_CLOSE_RESEARCH,
        parameters={
            "research_only": True,
            "discovery_variant": args.variant,
        },
    )

    registry = DatasetRegistry()
    usage = DatasetUsageLedger(registry)
    runs = ResearchRunLedger(registry, usage)
    evidence = EvidenceLedger(runs)
    records = ResearchRecordLedger()
    runner = ResearchJobRunner(runs=runs, evidence=evidence, records=records)

    result = DiscoveryFactory(runner).prepare_and_run(
        DiscoveryFactoryContext(
            spec=spec,
            manifest_revision=manifest.revision,
            job_id=args.job_id,
            readiness_snapshot=readiness,
            mt5_path=args.mt5_path,
            exporter_script=repo_root / "scripts" / "export_sp2l_v3_xauusd_m1_artifact.py",
            artifact_path=repo_root / args.artifact,
            discovery_script=repo_root / "scripts" / "run_sp2l_v3_xauusd_discovery_matrix.py",
            variant_name=args.variant,
            python_executable=args.python_executable,
            evidence_id=f"EVIDENCE-{args.job_id}",
            source_artifact_path=Path(args.source_m1_artifact),
            source_artifact_sha256=args.source_m1_sha256,
            entry_population_artifact_path=(repo_root / args.entry_population_artifact),
            entry_population_sha256=args.entry_population_sha256,
        )
    )

    output = {
        "status": "COMPLETE",
        "research_only": True,
        "production_locked": True,
        "passport": {
            "canonical": passport.canonical,
            "eligibility": eligibility.as_dict(),
        },
        "job": result.job.as_dict(),
        "job_fingerprint": result.job.fingerprint,
        "dataset_artifact": result.snapshot.artifact.as_dict(),
        "dataset_content_sha256": result.snapshot.dataset_content_sha256,
        "m1_integrity": result.snapshot.payload.get("m1_integrity"),
        "frozen_entry_population_artifact": str(repo_root / args.entry_population_artifact),
        "frozen_entry_population_sha256": args.entry_population_sha256,
        "execution_input_fingerprint": result.result.receipt.input_fingerprint,
        "run_id": result.result.run.run_id,
        "run_fingerprint": result.result.run.fingerprint,
        "evidence_id": result.result.evidence.evidence_id,
        "record": result.result.record.as_dict(),
        "provenance": result.result.provenance.as_dict(),
        "metrics": result.result.receipt.metrics.as_dict(),
        "execution_id": result.result.receipt.execution_id,
        "engine_revision": result.result.receipt.engine_revision,
        "readiness_snapshot": readiness.as_dict(),
    }
    print(json.dumps(output, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
