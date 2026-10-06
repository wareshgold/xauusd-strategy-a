"""SP2L Strategy Research Factory foundation.

Research-only orchestration layer. It does not generate production
BUY/SELL decisions and does not modify the live forward runner.
"""

__version__ = "0.1.0"


from .usage import DatasetUsage, DatasetUsageError, DatasetUsageLedger, UsageDisposition
