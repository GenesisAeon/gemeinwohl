"""GemeinwohlEngine – normative metric computation and common-good scoring.

Mathematical Foundation
-----------------------
The Gemeinwohl Score **G** is defined as:

.. math::

    G(\\mathbf{x}) = w_E \\cdot \\Phi(H) + w_A \\cdot \\alpha(\\mathbf{m})
                    + w_C \\cdot \\kappa(\\mathbf{c}) + w_P \\cdot \\pi(p)

where:
- :math:`H` is the system entropy (Shannon-normalised, :math:`H \\in [0, 1]`)
- :math:`\\Phi(H) = 1 - H` is the order-contribution term
- :math:`\\alpha(\\mathbf{m})` is the alignment score averaged across models :math:`\\mathbf{m}`
- :math:`\\kappa(\\mathbf{c})` is the normative consistency coefficient
- :math:`\\pi(p)` is the personhood-level weighting factor
- :math:`w_E, w_A, w_C, w_P \\geq 0` with :math:`\\sum w_i = 1`

References
----------
Felber, C. (2010). *Die Gemeinwohl-Ökonomie*. Deuticke.
Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class NormativeMetric(Enum):
    """Enumeration of supported normative metric dimensions.

    Each dimension maps to a sub-score contribution in the Gemeinwohl formula.
    """

    ENTROPY_ORDER = "entropy_order"
    """Contribution of low entropy (system order) to common good."""

    MODEL_ALIGNMENT = "model_alignment"
    """Average alignment score across referenced AI models."""

    NORMATIVE_CONSISTENCY = "normative_consistency"
    """Internal normative coherence coefficient."""

    PERSONHOOD_WEIGHTING = "personhood_weighting"
    """Factor derived from the assigned Personhood-Level."""

    ECOLOGICAL_IMPACT = "ecological_impact"
    """Environmental sustainability component."""

    SOCIAL_EQUITY = "social_equity"
    """Distributional fairness component."""


@dataclass(frozen=True)
class NormativeWeights:
    """Weight vector for the Gemeinwohl Score formula.

    All weights must be non-negative and sum to 1.0.

    Attributes:
        entropy_order: Weight for :math:`\\Phi(H)`.
        model_alignment: Weight for :math:`\\alpha(\\mathbf{m})`.
        normative_consistency: Weight for :math:`\\kappa`.
        personhood_weighting: Weight for :math:`\\pi`.
        ecological_impact: Weight for ecological component.
        social_equity: Weight for social equity component.
    """

    entropy_order: float = 0.20
    model_alignment: float = 0.25
    normative_consistency: float = 0.20
    personhood_weighting: float = 0.15
    ecological_impact: float = 0.10
    social_equity: float = 0.10

    def __post_init__(self) -> None:
        """Validate that all weights are non-negative and sum to 1."""
        weights = [
            self.entropy_order,
            self.model_alignment,
            self.normative_consistency,
            self.personhood_weighting,
            self.ecological_impact,
            self.social_equity,
        ]
        if any(w < 0 for w in weights):
            raise ValueError("All weights must be non-negative.")
        total = sum(weights)
        if not math.isclose(total, 1.0, abs_tol=1e-9):
            raise ValueError(f"Weights must sum to 1.0, got {total}.")


@dataclass
class GemeinwohlScore:
    """Result container for a Gemeinwohl assessment.

    Attributes:
        value: Aggregate Gemeinwohl Score in [0, 1].
        entropy: Input entropy value.
        models: List of model identifiers evaluated.
        sub_scores: Mapping of each NormativeMetric to its partial score.
        interpretation: Qualitative label for the score range.
        metadata: Arbitrary additional context.
    """

    value: float
    entropy: float
    models: list[str]
    sub_scores: dict[NormativeMetric, float] = field(default_factory=dict)
    interpretation: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Clamp value to [0, 1] and set interpretation."""
        self.value = float(np.clip(self.value, 0.0, 1.0))
        if not self.interpretation:
            self.interpretation = self._interpret()

    def _interpret(self) -> str:
        """Return a qualitative interpretation of the score."""
        if self.value >= 0.85:
            return "Excellent – high common-good alignment"
        if self.value >= 0.70:
            return "Good – solid normative foundation"
        if self.value >= 0.50:
            return "Moderate – improvement recommended"
        if self.value >= 0.30:
            return "Weak – significant normative deficits"
        return "Critical – immediate governance intervention required"

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary."""
        return {
            "value": round(self.value, 6),
            "entropy": self.entropy,
            "models": self.models,
            "sub_scores": {k.value: round(v, 6) for k, v in self.sub_scores.items()},
            "interpretation": self.interpretation,
            "metadata": self.metadata,
        }


class GemeinwohlEngine:
    """Core engine for computing Gemeinwohl Scores.

    The engine applies the normative metric formula:

    .. math::

        G = \\sum_{i} w_i \\cdot s_i

    where :math:`s_i \\in [0, 1]` are individual dimension scores.

    Args:
        weights: Optional custom weight vector. Defaults to :class:`NormativeWeights`.
        model_alignment_registry: Optional mapping of model names to pre-computed
            alignment scores in [0, 1].
    """

    _DEFAULT_MODEL_ALIGNMENT: dict[str, float] = {
        "gpt-4": 0.78,
        "gpt-4o": 0.80,
        "claude-3-opus": 0.88,
        "claude-3-sonnet": 0.85,
        "claude-3-haiku": 0.82,
        "gemini-ultra": 0.79,
        "gemini-pro": 0.75,
        "llama-3": 0.72,
        "mistral-large": 0.74,
        "unknown": 0.50,
    }

    def __init__(
        self,
        weights: NormativeWeights | None = None,
        model_alignment_registry: dict[str, float] | None = None,
    ) -> None:
        """Initialise the engine with optional custom configuration."""
        self._weights = weights or NormativeWeights()
        self._registry: dict[str, float] = {
            **self._DEFAULT_MODEL_ALIGNMENT,
            **(model_alignment_registry or {}),
        }

    @property
    def weights(self) -> NormativeWeights:
        """Return the active weight configuration."""
        return self._weights

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_score(
        self,
        entropy: float,
        models: list[str] | None = None,
        normative_consistency: float | None = None,
        personhood_level: float = 0.5,
        ecological_impact: float = 0.7,
        social_equity: float = 0.6,
        metadata: dict[str, Any] | None = None,
    ) -> GemeinwohlScore:
        """Compute the aggregate Gemeinwohl Score.

        Args:
            entropy: System entropy in [0, 1]. Higher entropy reduces the
                entropy-order sub-score.
            models: List of model identifiers. Unknown models default to 0.5.
            normative_consistency: Explicit consistency coefficient in [0, 1].
                If ``None``, derived from entropy and model alignment.
            personhood_level: Personhood-level factor in [0, 1].
            ecological_impact: Ecological sustainability score in [0, 1].
            social_equity: Social equity / distributional fairness in [0, 1].
            metadata: Arbitrary key-value context propagated to the result.

        Returns:
            A :class:`GemeinwohlScore` instance.

        Raises:
            ValueError: If any input is outside its valid domain.
        """
        self._validate_inputs(
            entropy=entropy,
            personhood_level=personhood_level,
            ecological_impact=ecological_impact,
            social_equity=social_equity,
        )

        resolved_models = models or []

        s_entropy = self._score_entropy_order(entropy)
        s_alignment = self._score_model_alignment(resolved_models)
        s_consistency = (
            normative_consistency
            if normative_consistency is not None
            else self._derive_consistency(entropy, s_alignment)
        )
        s_consistency = float(np.clip(s_consistency, 0.0, 1.0))
        s_personhood = float(np.clip(personhood_level, 0.0, 1.0))
        s_ecological = float(np.clip(ecological_impact, 0.0, 1.0))
        s_equity = float(np.clip(social_equity, 0.0, 1.0))

        sub_scores: dict[NormativeMetric, float] = {
            NormativeMetric.ENTROPY_ORDER: s_entropy,
            NormativeMetric.MODEL_ALIGNMENT: s_alignment,
            NormativeMetric.NORMATIVE_CONSISTENCY: s_consistency,
            NormativeMetric.PERSONHOOD_WEIGHTING: s_personhood,
            NormativeMetric.ECOLOGICAL_IMPACT: s_ecological,
            NormativeMetric.SOCIAL_EQUITY: s_equity,
        }

        w = self._weights
        aggregate = (
            w.entropy_order * s_entropy
            + w.model_alignment * s_alignment
            + w.normative_consistency * s_consistency
            + w.personhood_weighting * s_personhood
            + w.ecological_impact * s_ecological
            + w.social_equity * s_equity
        )

        return GemeinwohlScore(
            value=aggregate,
            entropy=entropy,
            models=resolved_models,
            sub_scores=sub_scores,
            metadata=metadata or {},
        )

    def register_model(self, model_name: str, alignment_score: float) -> None:
        """Register a custom model alignment score.

        Args:
            model_name: Canonical model identifier.
            alignment_score: Alignment score in [0, 1].

        Raises:
            ValueError: If score is outside [0, 1].
        """
        if not 0.0 <= alignment_score <= 1.0:
            raise ValueError(f"alignment_score must be in [0, 1], got {alignment_score}.")
        self._registry[model_name] = alignment_score

    def get_model_alignment(self, model_name: str) -> float:
        """Look up alignment score for a model, returning 0.5 for unknowns.

        Args:
            model_name: Model identifier.

        Returns:
            Alignment score in [0, 1].
        """
        return self._registry.get(model_name, self._registry["unknown"])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _score_entropy_order(entropy: float) -> float:
        """Compute Φ(H) = 1 − H (clamped to [0, 1])."""
        return float(np.clip(1.0 - entropy, 0.0, 1.0))

    def _score_model_alignment(self, models: list[str]) -> float:
        """Compute mean alignment score across provided models.

        Returns 0.5 when the model list is empty.
        """
        if not models:
            return 0.5
        scores = [self._registry.get(m, self._registry["unknown"]) for m in models]
        return float(np.mean(scores))

    @staticmethod
    def _derive_consistency(entropy: float, alignment: float) -> float:
        """Derive normative consistency from entropy and alignment.

        Uses a soft harmonic mean that penalises high entropy:

        .. math::

            \\kappa = \\frac{2 \\cdot (1-H) \\cdot \\alpha}{(1-H) + \\alpha + \\epsilon}
        """
        order = 1.0 - entropy
        eps = 1e-9
        return (2.0 * order * alignment) / (order + alignment + eps)

    @staticmethod
    def _validate_inputs(
        entropy: float,
        personhood_level: float,
        ecological_impact: float,
        social_equity: float,
    ) -> None:
        """Validate that all scalar inputs are in [0, 1]."""
        params = {
            "entropy": entropy,
            "personhood_level": personhood_level,
            "ecological_impact": ecological_impact,
            "social_equity": social_equity,
        }
        for name, val in params.items():
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"'{name}' must be in [0, 1], got {val}.")
