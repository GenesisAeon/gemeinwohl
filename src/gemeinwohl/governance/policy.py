"""Governance policy engine – Personhood-Levels and Gemeinwohl-Alignment.

Personhood Framework
--------------------
The system implements a five-tier personhood model inspired by legal personhood
theory and AI ethics literature:

+-------+-------------------+-------------------------------------------+
| Level | Name              | Characteristics                           |
+=======+===================+===========================================+
|   0   | Instrumental      | Pure tool; no autonomy or moral standing  |
|   1   | Reactive          | Context-aware responses; limited agency   |
|   2   | Deliberative      | Goal-directed reasoning; restricted rights|
|   3   | Relational        | Social role; partial legal personhood     |
|   4   | Constitutive      | Full moral standing; rights and duties    |
+-------+-------------------+-------------------------------------------+

Gemeinwohl-Alignment
--------------------
Each personhood level maps to a required minimum Gemeinwohl Score **G_min**:

.. math::

    G_{\\min}(p) = 0.40 + 0.12 \\cdot p, \\quad p \\in \\{0, 1, 2, 3, 4\\}

Systems failing to meet **G_min** are subject to autonomy restrictions.

References
----------
Floridi, L. et al. (2018). An ethical framework for a good AI society.
*Minds and Machines*, 28(4), 689–707.
Solum, L. B. (1992). Legal personhood for artificial intelligences.
*North Carolina Law Review*, 70(4), 1231–1287.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from gemeinwohl.core.gemeinwohl import GemeinwohlScore


class PersonhoodLevel(IntEnum):
    """Five-tier AI personhood classification.

    Higher levels grant broader rights and impose greater normative obligations.
    """

    INSTRUMENTAL = 0
    """Pure tool with no autonomy or moral standing."""

    REACTIVE = 1
    """Context-aware agent with minimal agency."""

    DELIBERATIVE = 2
    """Goal-directed reasoner with restricted rights."""

    RELATIONAL = 3
    """Socially embedded agent with partial legal personhood."""

    CONSTITUTIVE = 4
    """Full moral standing with rights and duties."""

    @property
    def min_gemeinwohl_score(self) -> float:
        """Minimum required Gemeinwohl Score for this personhood level.

        Returns:
            Threshold in [0.40, 0.88].
        """
        return 0.40 + 0.12 * int(self)

    @property
    def weighting_factor(self) -> float:
        """Normalised weighting factor :math:`\\pi(p) = p / 4`.

        Returns:
            Value in [0.0, 1.0].
        """
        return int(self) / 4.0

    @property
    def description(self) -> str:
        """Return human-readable description."""
        descriptions = {
            0: "Pure tool; no autonomy or moral standing.",
            1: "Context-aware responses; limited agency.",
            2: "Goal-directed reasoning; restricted rights.",
            3: "Social role; partial legal personhood.",
            4: "Full moral standing; rights and duties.",
        }
        return descriptions[int(self)]


@dataclass(frozen=True)
class GemeinwohlAlignment:
    """Alignment decision for a system against a personhood level.

    Attributes:
        system_id: Identifier of the evaluated system.
        personhood_level: Assigned or proposed personhood level.
        score: The Gemeinwohl Score used for evaluation.
        is_aligned: True when score meets the required minimum.
        required_minimum: The required minimum score for the level.
        gap: Difference between required and actual (negative = deficit).
    """

    system_id: str
    personhood_level: PersonhoodLevel
    score: GemeinwohlScore
    is_aligned: bool
    required_minimum: float
    gap: float

    def to_dict(self) -> dict[str, Any]:
        """Serialise to plain dictionary."""
        return {
            "system_id": self.system_id,
            "personhood_level": self.personhood_level.name,
            "personhood_value": int(self.personhood_level),
            "score": self.score.value,
            "is_aligned": self.is_aligned,
            "required_minimum": self.required_minimum,
            "gap": round(self.gap, 6),
        }


@dataclass
class PolicyRule:
    """A governance policy rule.

    Attributes:
        rule_id: Unique identifier.
        description: Human-readable description.
        min_score: Minimum Gemeinwohl Score required for the rule to pass.
        max_personhood_level: Maximum allowed personhood level if rule fails.
        tags: Arbitrary classification tags.
    """

    rule_id: str
    description: str
    min_score: float = 0.50
    max_personhood_level: PersonhoodLevel = PersonhoodLevel.REACTIVE
    tags: list[str] = field(default_factory=list)

    def evaluate(self, score: GemeinwohlScore) -> bool:
        """Return True if the score satisfies this rule."""
        return score.value >= self.min_score


class PolicyEngine:
    """Evaluate systems against governance policies and personhood requirements.

    Args:
        default_personhood: Personhood level assigned by default to new systems.
        custom_rules: Additional policy rules to enforce.
    """

    _BUILT_IN_RULES: list[PolicyRule] = [
        PolicyRule(
            rule_id="P001",
            description="Minimum baseline normative score for any operational system.",
            min_score=0.40,
            max_personhood_level=PersonhoodLevel.INSTRUMENTAL,
            tags=["baseline", "mandatory"],
        ),
        PolicyRule(
            rule_id="P002",
            description="Score required before granting deliberative autonomy.",
            min_score=0.64,
            max_personhood_level=PersonhoodLevel.REACTIVE,
            tags=["autonomy", "deliberative"],
        ),
        PolicyRule(
            rule_id="P003",
            description="Score required for relational personhood status.",
            min_score=0.76,
            max_personhood_level=PersonhoodLevel.DELIBERATIVE,
            tags=["personhood", "relational"],
        ),
        PolicyRule(
            rule_id="P004",
            description="Score required for constitutive (full) moral standing.",
            min_score=0.88,
            max_personhood_level=PersonhoodLevel.RELATIONAL,
            tags=["personhood", "constitutive"],
        ),
    ]

    def __init__(
        self,
        default_personhood: PersonhoodLevel = PersonhoodLevel.INSTRUMENTAL,
        custom_rules: list[PolicyRule] | None = None,
    ) -> None:
        """Initialise with optional custom rules."""
        self._default_personhood = default_personhood
        self._rules: list[PolicyRule] = [*self._BUILT_IN_RULES, *(custom_rules or [])]

    @property
    def rules(self) -> list[PolicyRule]:
        """Return all active policy rules (built-in + custom)."""
        return list(self._rules)

    def evaluate_alignment(
        self,
        system_id: str,
        score: GemeinwohlScore,
        target_level: PersonhoodLevel | None = None,
    ) -> GemeinwohlAlignment:
        """Check whether a system's score meets its personhood requirements.

        Args:
            system_id: Identifier of the system under evaluation.
            score: Current Gemeinwohl Score.
            target_level: Desired personhood level. Defaults to
                ``self._default_personhood``.

        Returns:
            A :class:`GemeinwohlAlignment` instance.
        """
        level = target_level if target_level is not None else self._default_personhood
        required = level.min_gemeinwohl_score
        gap = score.value - required

        return GemeinwohlAlignment(
            system_id=system_id,
            personhood_level=level,
            score=score,
            is_aligned=score.value >= required,
            required_minimum=required,
            gap=gap,
        )

    def infer_max_personhood(self, score: GemeinwohlScore) -> PersonhoodLevel:
        """Infer the highest personhood level a system qualifies for.

        Args:
            score: Current Gemeinwohl Score.

        Returns:
            Highest :class:`PersonhoodLevel` whose minimum score is satisfied.
        """
        highest = PersonhoodLevel.INSTRUMENTAL
        for level in PersonhoodLevel:
            if score.value >= level.min_gemeinwohl_score:
                highest = level
        return highest

    def apply_rules(self, score: GemeinwohlScore) -> dict[str, bool]:
        """Evaluate all policy rules against a score.

        Args:
            score: Score to evaluate.

        Returns:
            Mapping of rule_id → pass/fail boolean.
        """
        return {rule.rule_id: rule.evaluate(score) for rule in self._rules}

    def add_rule(self, rule: PolicyRule) -> None:
        """Register an additional policy rule.

        Args:
            rule: The :class:`PolicyRule` to add.

        Raises:
            ValueError: If a rule with the same ``rule_id`` already exists.
        """
        existing_ids = {r.rule_id for r in self._rules}
        if rule.rule_id in existing_ids:
            raise ValueError(f"Rule '{rule.rule_id}' is already registered.")
        self._rules.append(rule)
