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
