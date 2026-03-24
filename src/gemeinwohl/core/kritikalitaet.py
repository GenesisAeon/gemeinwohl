r"""KritikalitaetsChecker - ethical implication analysis and normative consistency.

The Kritikalitaets-Model
------------------------
A system state is assigned a **Kritikalitaets-Level** *K* according to:

.. math::

    K(G, \sigma) = \begin{cases}
        0 & G \geq \theta_{\text{safe}} \\
        1 & \theta_{\text{warn}} \leq G < \theta_{\text{safe}} \\
        2 & \theta_{\text{crit}} \leq G < \theta_{\text{warn}} \\
        3 & G < \theta_{\text{crit}}
    \end{cases}

where :math:`\sigma` is the standard deviation of repeated assessments and
:math:`\theta_{\text{safe}} = 0.70`,
:math:`\theta_{\text{warn}} = 0.50`,
:math:`\theta_{\text{crit}} = 0.30`.

Normative Consistency
---------------------
For a sequence of scores :math:`\{G_t\}_{t=1}^{T}`, normative consistency is:

.. math::

    \kappa_{\text{seq}} = 1 - \frac{\text{Var}(\{G_t\})}{\mu(\{G_t\}) + \epsilon}

References:
    Rawls, J. (1971). *A Theory of Justice*. Harvard University Press.
    Habermas, J. (1981). *Theorie des kommunikativen Handelns*. Suhrkamp.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np

if TYPE_CHECKING:
    from gemeinwohl.core.gemeinwohl import GemeinwohlScore


class KritikalitaetsLevel(IntEnum):
    """Discrete criticality levels for Gemeinwohl assessments."""

    SAFE = 0
    """Score >= 0.70 - system operates within normative bounds."""

    WARNING = 1
    """0.50 <= Score < 0.70 - advisory review recommended."""

    CRITICAL = 2
    """0.30 <= Score < 0.50 - governance intervention warranted."""

    EMERGENCY = 3
    """Score < 0.30 - immediate halt and review required."""


@dataclass(frozen=True)
class EthicalImplication:
    """A single identified ethical implication.

    Attributes:
        code: Short machine-readable identifier (e.g. ``"E001"``).
        description: Human-readable description.
        severity: Severity level from 0 (minimal) to 1 (critical).
        dimension: Which normative dimension triggered this implication.
        remediation: Suggested corrective action.
    """

    code: str
    description: str
    severity: float
    dimension: str
    remediation: str = ""

    def __post_init__(self) -> None:
        """Validate severity range."""
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError(f"severity must be in [0, 1], got {self.severity}.")


@dataclass
class NormativeConsistencyResult:
    r"""Result of a normative consistency check.

    Attributes:
        is_consistent: True when consistency score exceeds threshold.
        consistency_score: Computed :math:`\kappa_{\text{seq}}` value.
        variance: Variance of the input score sequence.
        mean: Mean of the input score sequence.
        threshold: Threshold applied for the binary decision.
    """

    is_consistent: bool
    consistency_score: float
    variance: float
    mean: float
    threshold: float = 0.70

    def to_dict(self) -> dict[str, Any]:
        """Serialise to plain dictionary."""
        return {
            "is_consistent": self.is_consistent,
            "consistency_score": round(self.consistency_score, 6),
            "variance": round(self.variance, 6),
            "mean": round(self.mean, 6),
            "threshold": self.threshold,
        }


@dataclass
class KritikalitaetsReport:
    """Full criticality assessment report.

    Attributes:
        level: Discrete :class:`KritikalitaetsLevel`.
        score: Triggering :class:`GemeinwohlScore`.
        implications: List of identified :class:`EthicalImplication` objects.
        consistency: Optional normative consistency result.
        recommendations: High-level governance recommendations.
    """

    level: KritikalitaetsLevel
    score: GemeinwohlScore
    implications: list[EthicalImplication] = field(default_factory=list)
    consistency: NormativeConsistencyResult | None = None
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to plain dictionary."""
        return {
            "level": self.level.name,
            "level_value": int(self.level),
            "score": self.score.to_dict(),
            "implications": [
                {
                    "code": imp.code,
                    "description": imp.description,
                    "severity": imp.severity,
                    "dimension": imp.dimension,
                    "remediation": imp.remediation,
                }
                for imp in self.implications
            ],
            "consistency": self.consistency.to_dict() if self.consistency else None,
            "recommendations": self.recommendations,
        }


class KritikalitaetsChecker:
    r"""Analyse ethical implications and normative consistency of Gemeinwohl Scores.

    Args:
        theta_safe: Lower bound for safe classification (default 0.70).
        theta_warn: Lower bound for warning classification (default 0.50).
        theta_crit: Lower bound for critical classification (default 0.30).
        consistency_threshold: Minimum :math:`\kappa_{\text{seq}}` for
            a sequence to be considered normatively consistent (default 0.70).
    """

    _RULES: ClassVar[list[tuple[Any, EthicalImplication]]] = []

    def __init__(
        self,
        theta_safe: float = 0.70,
        theta_warn: float = 0.50,
        theta_crit: float = 0.30,
        consistency_threshold: float = 0.70,
    ) -> None:
        """Initialise with configurable thresholds."""
        if not (0.0 <= theta_crit < theta_warn < theta_safe <= 1.0):
            raise ValueError(
                "Thresholds must satisfy 0 <= theta_crit < theta_warn < theta_safe <= 1."
            )
        self.theta_safe = theta_safe
        self.theta_warn = theta_warn
        self.theta_crit = theta_crit
        self.consistency_threshold = consistency_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, score: GemeinwohlScore) -> KritikalitaetsLevel:
        """Classify a score into a :class:`KritikalitaetsLevel`.

        Args:
            score: The Gemeinwohl Score to classify.

        Returns:
            The corresponding criticality level.
        """
        g = score.value
        if g >= self.theta_safe:
            return KritikalitaetsLevel.SAFE
        if g >= self.theta_warn:
            return KritikalitaetsLevel.WARNING
        if g >= self.theta_crit:
            return KritikalitaetsLevel.CRITICAL
        return KritikalitaetsLevel.EMERGENCY

    def identify_implications(self, score: GemeinwohlScore) -> list[EthicalImplication]:
        """Identify ethical implications from a Gemeinwohl Score.

        Args:
            score: Assessed Gemeinwohl Score.

        Returns:
            List of :class:`EthicalImplication` instances, ordered by severity.
        """
        from gemeinwohl.core.gemeinwohl import NormativeMetric  # avoid circular

        implications: list[EthicalImplication] = []

        if score.entropy > 0.8:
            implications.append(
                EthicalImplication(
                    code="E001",
                    description="Critically high system entropy undermines normative stability.",
                    severity=0.9,
                    dimension=NormativeMetric.ENTROPY_ORDER.value,
                    remediation="Apply entropy-reduction governance protocols.",
                )
            )
        elif score.entropy > 0.6:
            implications.append(
                EthicalImplication(
                    code="E002",
                    description="Elevated entropy may compromise normative predictability.",
                    severity=0.55,
                    dimension=NormativeMetric.ENTROPY_ORDER.value,
                    remediation=(
                        "Review stochastic components and increase deterministic guardrails."
                    ),
                )
            )

        alignment = score.sub_scores.get(NormativeMetric.MODEL_ALIGNMENT, 1.0)
        if alignment < 0.5:
            implications.append(
                EthicalImplication(
                    code="E003",
                    description="Low model alignment indicates potential value misalignment.",
                    severity=0.8,
                    dimension=NormativeMetric.MODEL_ALIGNMENT.value,
                    remediation=(
                        "Replace or fine-tune models; apply RLHF with common-good objectives."
                    ),
                )
            )
        elif alignment < 0.7:
            implications.append(
                EthicalImplication(
                    code="E004",
                    description="Sub-optimal model alignment requires monitoring.",
                    severity=0.45,
                    dimension=NormativeMetric.MODEL_ALIGNMENT.value,
                    remediation="Schedule alignment audit within next sprint cycle.",
                )
            )

        consistency = score.sub_scores.get(NormativeMetric.NORMATIVE_CONSISTENCY, 1.0)
        if consistency < 0.4:
            implications.append(
                EthicalImplication(
                    code="E005",
                    description=("Normative inconsistency detected - ethical principles conflict."),
                    severity=0.85,
                    dimension=NormativeMetric.NORMATIVE_CONSISTENCY.value,
                    remediation="Conduct normative coherence review with ethics board.",
                )
            )

        personhood = score.sub_scores.get(NormativeMetric.PERSONHOOD_WEIGHTING, 1.0)
        if personhood < 0.3:
            implications.append(
                EthicalImplication(
                    code="E006",
                    description=("Insufficient personhood recognition may violate dignity norms."),
                    severity=0.75,
                    dimension=NormativeMetric.PERSONHOOD_WEIGHTING.value,
                    remediation="Elevate personhood level or restrict system autonomy.",
                )
            )

        ecological = score.sub_scores.get(NormativeMetric.ECOLOGICAL_IMPACT, 1.0)
        if ecological < 0.4:
            implications.append(
                EthicalImplication(
                    code="E007",
                    description=("Negative ecological impact conflicts with sustainability norms."),
                    severity=0.70,
                    dimension=NormativeMetric.ECOLOGICAL_IMPACT.value,
                    remediation="Implement green-AI practices and carbon offset measures.",
                )
            )

        equity = score.sub_scores.get(NormativeMetric.SOCIAL_EQUITY, 1.0)
        if equity < 0.4:
            implications.append(
                EthicalImplication(
                    code="E008",
                    description="Low social equity score indicates distributional injustice.",
                    severity=0.65,
                    dimension=NormativeMetric.SOCIAL_EQUITY.value,
                    remediation=("Apply equity-aware training data and fairness constraints."),
                )
            )

        return sorted(implications, key=lambda x: x.severity, reverse=True)

    def check_sequence_consistency(
        self,
        scores: list[GemeinwohlScore],
    ) -> NormativeConsistencyResult:
        """Assess normative consistency of a time-series of scores.

        Args:
            scores: Ordered sequence of :class:`GemeinwohlScore` instances.

        Returns:
            :class:`NormativeConsistencyResult`.

        Raises:
            ValueError: If fewer than 2 scores are provided.
        """
        if len(scores) < 2:
            raise ValueError("At least 2 scores are required for consistency analysis.")

        values = np.array([s.value for s in scores], dtype=float)
        mu = float(np.mean(values))
        var = float(np.var(values))
        eps = 1e-9
        kappa = 1.0 - var / (mu + eps)
        kappa = float(np.clip(kappa, 0.0, 1.0))

        return NormativeConsistencyResult(
            is_consistent=kappa >= self.consistency_threshold,
            consistency_score=kappa,
            variance=var,
            mean=mu,
            threshold=self.consistency_threshold,
        )

    def assess(self, score: GemeinwohlScore) -> KritikalitaetsReport:
        """Produce a full :class:`KritikalitaetsReport` for a single score.

        Args:
            score: The score to assess.

        Returns:
            Complete criticality report including level, implications, and
            governance recommendations.
        """
        level = self.classify(score)
        implications = self.identify_implications(score)
        recommendations = self._generate_recommendations(level, implications)

        return KritikalitaetsReport(
            level=level,
            score=score,
            implications=implications,
            recommendations=recommendations,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_recommendations(
        level: KritikalitaetsLevel,
        implications: list[EthicalImplication],
    ) -> list[str]:
        """Generate governance recommendations based on level and implications."""
        recs: list[str] = []

        if level == KritikalitaetsLevel.SAFE:
            recs.append("System operates within normative bounds. Continue monitoring.")
        elif level == KritikalitaetsLevel.WARNING:
            recs.append("Schedule advisory review within 30 days.")
            recs.append("Increase assessment frequency to weekly.")
        elif level == KritikalitaetsLevel.CRITICAL:
            recs.append("Initiate governance intervention protocol.")
            recs.append("Suspend non-critical operations pending review.")
            recs.append("Convene ethics committee within 72 hours.")
        else:  # EMERGENCY
            recs.append("IMMEDIATE HALT: suspend all autonomous operations.")
            recs.append("Engage emergency ethics board within 24 hours.")
            recs.append("Apply minimum-footprint fallback mode.")

        high_severity = [imp for imp in implications if imp.severity >= 0.7]
        for imp in high_severity[:3]:  # top 3 only
            if imp.remediation:
                recs.append(f"[{imp.code}] {imp.remediation}")

        return recs
