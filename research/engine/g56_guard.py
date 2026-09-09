from .source_discrimination_g56 import production_allowed


def strategy_a_execution_gate() -> bool:
    """Return whether source discrimination has fully resolved critical blockers."""
    return production_allowed()
