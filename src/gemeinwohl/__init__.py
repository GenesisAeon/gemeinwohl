"""Gemeinwohl - Normative Common-Good Layer for GenesisAeon.

This package provides:
- GemeinwohlEngine: normative metric computation and common-good scoring
- KritikalitaetsChecker: ethical implication analysis and normative consistency
- CLI: ``gemeinwohl assess`` command
- Governance: Personhood-Levels and Gemeinwohl-Alignment policies

Example:
    >>> from gemeinwohl import GemeinwohlEngine
    >>> engine = GemeinwohlEngine()
    >>> score = engine.compute_score(entropy=0.3, models=["gpt-4", "claude-3"])
    >>> print(score.value)
"""

from gemeinwohl.core.gemeinwohl import (
    GemeinwohlEngine,
    GemeinwohlScore,
    NormativeMetric,
)
from gemeinwohl.core.kritikalitaet import (
    EthicalImplication,
    KritikalitaetsChecker,
    NormativeConsistencyResult,
)
from gemeinwohl.governance.policy import (
    GemeinwohlAlignment,
    PersonhoodLevel,
    PolicyEngine,
)

__all__ = [
    "EthicalImplication",
    "GemeinwohlAlignment",
    "GemeinwohlEngine",
    "GemeinwohlScore",
    "KritikalitaetsChecker",
    "NormativeConsistencyResult",
    "NormativeMetric",
    "PersonhoodLevel",
    "PolicyEngine",
]

__version__ = "0.1.0"
__author__ = "GenesisAeon"
__license__ = "MIT"
