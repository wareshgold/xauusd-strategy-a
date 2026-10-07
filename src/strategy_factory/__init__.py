"""SP2L Strategy Research Factory foundation.

Research-only orchestration layer. It does not generate production
BUY/SELL decisions and does not modify the live forward runner.
"""

__version__ = "0.1.0"


from .usage import DatasetUsage, DatasetUsageError, DatasetUsageLedger, UsageDisposition

from .runs import ResearchRunError, ResearchRunIdentity, ResearchRunLedger
from .evidence import EvidenceBundle, EvidenceLedger
from .provenance import provenance_gate, metrics_gate

from .metrics import MetricsContractError, ResearchMetrics

from .execution import ExecutionContractError, ExecutionReceipt, execution_gate, validate_execution_binding
from .acceptance import evidence_acceptance_gate, validate_evidence_acceptance
from .adapter import (
    ExecutionAdapter,
    ExecutionAdapterError,
    adapter_semantics,
    build_execution_receipt,
    validate_adapter_output,
)
from .jobs import ResearchJobError, ResearchJobSpec, validate_job_matches_test_spec
from .runner import ResearchJobRunResult, ResearchJobRunner, ResearchJobRunnerError
from .orchestrator import FactoryOrchestrator, QueuedResearchJob, RunnerExecutionContext, build_runner_executor
from .job_events import FactoryJobEvent, FactoryJobEventLedger
from .synthetic import SyntheticExecutionAdapter, SyntheticExecutionError, SyntheticExecutionFixture
from .data import DatasetIngestionError, HistoricalDatasetAdapter, LoadedDataset

from .test_contract import DatasetRole, ExecutionSemantics, HistoricalTestSpec, TestDataset, validate_test_spec

from .execution_kernel import (
    AmbiguityPolicy,
    EntryInstruction,
    ExecutionKernelError,
    HistoricalExecutionKernel,
    KernelResult,
    MarketEvent,
    Side,
    TradeOutcome,
)

from .sp2l_discrimination import (
    DiscriminationFixture,
    FixtureDisposition,
    build_sp2l_discrimination_fixtures,
)
from .source_resolution import (
    SourceEvidence,
    SourceResolutionError,
    SourceResolutionResult,
    SourceVerdict,
    evaluate_source_resolution,
    resolve_fixture_set,
)

from .readiness import SourceReadiness, evaluate_source_readiness
from .source_ledger import ResolutionRecord, ResolutionStatus, SourceLedgerError, SourceResolutionLedger
from .source_gate import SourceGateResult, SourceGateStatus, evaluate_source_gate

from .passport_gate import PassportEligibility, evaluate_passport_eligibility

from .snapshot import ReadinessSnapshot, build_readiness_snapshot, manifest_fingerprint, passport_fingerprint

from .audit import AuditBindingError, ResearchAuditRecord, bind_research_audit

from .dataset_provenance import DatasetProvenanceResult, DatasetProvenanceStatus, evaluate_dataset_provenance
from .research_provenance import ResearchProvenanceResult, ResearchProvenanceStatus, evaluate_research_provenance

from .research_record import ResearchRecord, ResearchRecordError, ResearchRecordLedger

from .statistics import ConfidenceInterval, StatisticalValidationError, StatisticalValidationResult, evaluate_statistical_validation

from .statistical_evidence import StatisticalEvidence, StatisticalEvidenceError, bind_statistical_evidence, validate_statistical_evidence_binding

from .statistical_governance import StatisticalUsage, StatisticalUsageDisposition, StatisticalUsageError, StatisticalUsageLedger

from .stability import StabilityContractError, StabilitySegment, StabilityProfile, evaluate_stability

from .stability_evidence import StabilityEvidenceError, StabilityEvidence, bind_stability_evidence, validate_stability_evidence_binding
from .research_evidence_bundle import (
    ResearchEvidenceBundle,
    ResearchEvidenceBundleError,
    bind_research_evidence_bundle,
    validate_research_evidence_bundle,
)
from .research_evidence_ledger import ResearchEvidenceLedger, ResearchEvidenceLedgerEntry, ResearchEvidenceLedgerError

from .research_acceptance import ResearchAcceptance, ResearchAcceptanceError, evaluate_research_acceptance
from .research_comparison import (
    ComparisonObservation,
    ResearchComparison,
    ResearchComparisonError,
    build_research_comparison,
)

from .robustness import RobustnessMatrixError, RobustnessMember, RobustnessMatrix, build_robustness_matrix
from .robustness_ledger import RobustnessMatrixLedger, RobustnessMatrixLedgerEntry, RobustnessMatrixLedgerError
from .robustness_governance import RobustnessUsage, RobustnessUsageDisposition, RobustnessUsageError, RobustnessUsageLedger
from .multiple_comparison import MultipleComparisonError, MultipleComparisonResult, adjust_p_values
from .statistical_comparison_evidence import StatisticalComparisonEvidence, StatisticalComparisonEvidenceError, bind_statistical_comparison_evidence, validate_statistical_comparison_evidence
from .statistical_comparison_evidence_ledger import StatisticalComparisonEvidenceLedger, StatisticalComparisonEvidenceLedgerEntry, StatisticalComparisonEvidenceLedgerError
from .statistical_comparison_governance import StatisticalComparisonUsage, StatisticalComparisonUsageDisposition, StatisticalComparisonUsageError, StatisticalComparisonUsageLedger
from .comparison_validation_gate import ComparisonValidationGateError, ComparisonValidationGateResult, ComparisonValidationGateStatus, evaluate_comparison_validation_gate
from .unified_research_quality import UnifiedResearchQuality, UnifiedResearchQualityError, evaluate_unified_research_quality

from .research_certification import ResearchCertification, ResearchCertificationError, certify_research_result

from .research_certification_ledger import ResearchCertificationLedger, ResearchCertificationLedgerEntry, ResearchCertificationLedgerError

from .research_audit_package import ResearchAuditPackage, ResearchAuditPackageError, build_research_audit_package

from .dashboard_config import DashboardConfig, DashboardConfigError, ForwardConfig, ResearchConfig, apply_settings, build_config, default_config, load_config, save_config
from .dashboard_config_provenance import DashboardConfigProvenance, DashboardConfigProvenanceError, bind_dashboard_config
from .dashboard_config_provenance_ledger import DashboardConfigProvenanceLedger, DashboardConfigProvenanceLedgerEntry, DashboardConfigProvenanceLedgerError
from .research_run_config_binding import ResearchRunConfigBinding, ResearchRunConfigBindingError, bind_research_run_config
from .research_run_config_binding_ledger import ResearchRunConfigBindingLedger, ResearchRunConfigBindingLedgerEntry, ResearchRunConfigBindingLedgerError

from .handoff import (
    HANDOFF_ROUTES,
    ResearchHandoff,
    ResearchHandoffError,
    build_research_handoff,
    validate_evidence_bound_handoff,
)

from .starnet_adapter import FactoryWorldState, WorldHandoff, WorldWorker, build_world_handoffs, build_world_state


from .forward_gate_factory import ForwardGateContext, ForwardGateError, ForwardGateFactory, ForwardGateResult

from .forward_session_factory import DemoForwardSession, DemoForwardSessionFactory, DemoForwardSessionResult, ForwardSessionError

from .forward_session_lifecycle import (
    DemoForwardSessionEvent,
    DemoForwardSessionLifecycle,
    ForwardSessionLifecycleError,
    ForwardSessionState,
    MT5ReconciliationReceipt,
    bind_mt5_reconciliation,
)
