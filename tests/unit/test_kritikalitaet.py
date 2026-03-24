"""Unit tests for KritikalitaetsChecker and related data classes."""

import pytest

from gemeinwohl.core.gemeinwohl import GemeinwohlEngine, GemeinwohlScore, NormativeMetric
from gemeinwohl.core.kritikalitaet import (
    EthicalImplication,
    KritikalitaetsChecker,
    KritikalitaetsLevel,
    KritikalitaetsReport,
    NormativeConsistencyResult,
)


def make_score(value: float, entropy: float = 0.3, models: list | None = None) -> GemeinwohlScore:
    """Helper to create a GemeinwohlScore with given value using the engine."""
    engine = GemeinwohlEngine()
    score = engine.compute_score(entropy=entropy, models=models or [])
    # Override value for precise threshold testing
    object.__setattr__(score, "value", value) if hasattr(score, "__dataclass_fields__") else None
    # Direct construction for precise value control
    return GemeinwohlScore(
        value=value,
        entropy=entropy,
        models=models or [],
        sub_scores=score.sub_scores,
    )


# ---------------------------------------------------------------------------
# EthicalImplication
# ---------------------------------------------------------------------------


class TestEthicalImplication:
    def test_valid_creation(self):
        imp = EthicalImplication(
            code="E001",
            description="Test",
            severity=0.8,
            dimension="entropy_order",
        )
        assert imp.code == "E001"
        assert imp.severity == 0.8

    def test_severity_below_zero_raises(self):
        with pytest.raises(ValueError, match="severity"):
            EthicalImplication(code="X", description="x", severity=-0.1, dimension="d")

    def test_severity_above_one_raises(self):
        with pytest.raises(ValueError, match="severity"):
            EthicalImplication(code="X", description="x", severity=1.1, dimension="d")

    def test_severity_boundary_zero(self):
        imp = EthicalImplication(code="X", description="x", severity=0.0, dimension="d")
        assert imp.severity == 0.0

    def test_severity_boundary_one(self):
        imp = EthicalImplication(code="X", description="x", severity=1.0, dimension="d")
        assert imp.severity == 1.0

    def test_frozen(self):
        imp = EthicalImplication(code="X", description="x", severity=0.5, dimension="d")
        with pytest.raises(AttributeError):
            imp.code = "Y"  # type: ignore[misc]

    def test_remediation_default_empty(self):
        imp = EthicalImplication(code="X", description="x", severity=0.5, dimension="d")
        assert imp.remediation == ""


# ---------------------------------------------------------------------------
# NormativeConsistencyResult
# ---------------------------------------------------------------------------


class TestNormativeConsistencyResult:
    def test_to_dict_keys(self):
        r = NormativeConsistencyResult(
            is_consistent=True, consistency_score=0.85, variance=0.01, mean=0.75
        )
        d = r.to_dict()
        assert "is_consistent" in d
        assert "consistency_score" in d
        assert "variance" in d
        assert "mean" in d
        assert "threshold" in d

    def test_consistent_flag_true(self):
        r = NormativeConsistencyResult(
            is_consistent=True, consistency_score=0.85, variance=0.01, mean=0.75
        )
        assert r.is_consistent is True

    def test_consistent_flag_false(self):
        r = NormativeConsistencyResult(
            is_consistent=False, consistency_score=0.4, variance=0.15, mean=0.5
        )
        assert r.is_consistent is False


# ---------------------------------------------------------------------------
# KritikalitaetsChecker - classify
# ---------------------------------------------------------------------------


class TestKritikalitaetsCheckerClassify:
    def setup_method(self):
        self.checker = KritikalitaetsChecker()

    def test_safe_exactly_at_threshold(self):
        score = make_score(0.70)
        assert self.checker.classify(score) == KritikalitaetsLevel.SAFE

    def test_safe_above_threshold(self):
        score = make_score(0.95)
        assert self.checker.classify(score) == KritikalitaetsLevel.SAFE

    def test_warning_at_lower_bound(self):
        score = make_score(0.50)
        assert self.checker.classify(score) == KritikalitaetsLevel.WARNING

    def test_warning_just_below_safe(self):
        score = make_score(0.699)
        assert self.checker.classify(score) == KritikalitaetsLevel.WARNING

    def test_critical_at_lower_bound(self):
        score = make_score(0.30)
        assert self.checker.classify(score) == KritikalitaetsLevel.CRITICAL

    def test_critical_just_below_warning(self):
        score = make_score(0.499)
        assert self.checker.classify(score) == KritikalitaetsLevel.CRITICAL

    def test_emergency_below_crit(self):
        score = make_score(0.29)
        assert self.checker.classify(score) == KritikalitaetsLevel.EMERGENCY

    def test_emergency_at_zero(self):
        score = make_score(0.0)
        assert self.checker.classify(score) == KritikalitaetsLevel.EMERGENCY

    def test_custom_thresholds(self):
        checker = KritikalitaetsChecker(theta_safe=0.80, theta_warn=0.60, theta_crit=0.40)
        assert checker.classify(make_score(0.85)) == KritikalitaetsLevel.SAFE
        assert checker.classify(make_score(0.70)) == KritikalitaetsLevel.WARNING
        assert checker.classify(make_score(0.50)) == KritikalitaetsLevel.CRITICAL
        assert checker.classify(make_score(0.35)) == KritikalitaetsLevel.EMERGENCY

    def test_invalid_thresholds_raises(self):
        with pytest.raises(ValueError, match="Thresholds"):
            KritikalitaetsChecker(theta_safe=0.40, theta_warn=0.60, theta_crit=0.30)


# ---------------------------------------------------------------------------
# KritikalitaetsChecker - identify_implications
# ---------------------------------------------------------------------------


class TestIdentifyImplications:
    def setup_method(self):
        self.checker = KritikalitaetsChecker()
        self.engine = GemeinwohlEngine()

    def test_high_entropy_triggers_e001(self):
        score = self.engine.compute_score(entropy=0.9)
        codes = [i.code for i in self.checker.identify_implications(score)]
        assert "E001" in codes

    def test_moderate_entropy_triggers_e002(self):
        score = self.engine.compute_score(entropy=0.65)
        codes = [i.code for i in self.checker.identify_implications(score)]
        assert "E002" in codes

    def test_low_entropy_no_entropy_implication(self):
        score = self.engine.compute_score(entropy=0.1)
        codes = [i.code for i in self.checker.identify_implications(score)]
        assert "E001" not in codes
        assert "E002" not in codes

    def test_implications_sorted_by_severity_desc(self):
        score = self.engine.compute_score(entropy=0.9)
        implications = self.checker.identify_implications(score)
        severities = [i.severity for i in implications]
        assert severities == sorted(severities, reverse=True)

    def test_no_implications_for_perfect_score(self):
        score = GemeinwohlScore(
            value=1.0,
            entropy=0.0,
            models=[],
            sub_scores={
                NormativeMetric.ENTROPY_ORDER: 1.0,
                NormativeMetric.MODEL_ALIGNMENT: 1.0,
                NormativeMetric.NORMATIVE_CONSISTENCY: 1.0,
                NormativeMetric.PERSONHOOD_WEIGHTING: 1.0,
                NormativeMetric.ECOLOGICAL_IMPACT: 1.0,
                NormativeMetric.SOCIAL_EQUITY: 1.0,
            },
        )
        implications = self.checker.identify_implications(score)
        assert len(implications) == 0

    def test_low_alignment_triggers_e003(self):
        score = GemeinwohlScore(
            value=0.4,
            entropy=0.5,
            models=[],
            sub_scores={
                NormativeMetric.ENTROPY_ORDER: 0.5,
                NormativeMetric.MODEL_ALIGNMENT: 0.3,
                NormativeMetric.NORMATIVE_CONSISTENCY: 0.5,
                NormativeMetric.PERSONHOOD_WEIGHTING: 0.5,
                NormativeMetric.ECOLOGICAL_IMPACT: 0.5,
                NormativeMetric.SOCIAL_EQUITY: 0.5,
            },
        )
        codes = [i.code for i in self.checker.identify_implications(score)]
        assert "E003" in codes

    def test_low_personhood_triggers_e006(self):
        score = GemeinwohlScore(
            value=0.4,
            entropy=0.5,
            models=[],
            sub_scores={
                NormativeMetric.ENTROPY_ORDER: 0.5,
                NormativeMetric.MODEL_ALIGNMENT: 0.5,
                NormativeMetric.NORMATIVE_CONSISTENCY: 0.5,
                NormativeMetric.PERSONHOOD_WEIGHTING: 0.2,
                NormativeMetric.ECOLOGICAL_IMPACT: 0.5,
                NormativeMetric.SOCIAL_EQUITY: 0.5,
            },
        )
        codes = [i.code for i in self.checker.identify_implications(score)]
        assert "E006" in codes

    def test_low_ecological_triggers_e007(self):
        score = GemeinwohlScore(
            value=0.4,
            entropy=0.5,
            models=[],
            sub_scores={
                NormativeMetric.ENTROPY_ORDER: 0.5,
                NormativeMetric.MODEL_ALIGNMENT: 0.5,
                NormativeMetric.NORMATIVE_CONSISTENCY: 0.5,
                NormativeMetric.PERSONHOOD_WEIGHTING: 0.5,
                NormativeMetric.ECOLOGICAL_IMPACT: 0.3,
                NormativeMetric.SOCIAL_EQUITY: 0.5,
            },
        )
        codes = [i.code for i in self.checker.identify_implications(score)]
        assert "E007" in codes

    def test_low_equity_triggers_e008(self):
        score = GemeinwohlScore(
            value=0.4,
            entropy=0.5,
            models=[],
            sub_scores={
                NormativeMetric.ENTROPY_ORDER: 0.5,
                NormativeMetric.MODEL_ALIGNMENT: 0.5,
                NormativeMetric.NORMATIVE_CONSISTENCY: 0.5,
                NormativeMetric.PERSONHOOD_WEIGHTING: 0.5,
                NormativeMetric.ECOLOGICAL_IMPACT: 0.5,
                NormativeMetric.SOCIAL_EQUITY: 0.3,
            },
        )
        codes = [i.code for i in self.checker.identify_implications(score)]
        assert "E008" in codes


# ---------------------------------------------------------------------------
# KritikalitaetsChecker - check_sequence_consistency
# ---------------------------------------------------------------------------


class TestSequenceConsistency:
    def setup_method(self):
        self.checker = KritikalitaetsChecker()
        self.engine = GemeinwohlEngine()

    def _make_scores(self, values: list) -> list:
        return [GemeinwohlScore(value=v, entropy=0.3, models=[]) for v in values]

    def test_requires_at_least_two_scores(self):
        scores = self._make_scores([0.7])
        with pytest.raises(ValueError, match="2 scores"):
            self.checker.check_sequence_consistency(scores)

    def test_consistent_sequence(self):
        scores = self._make_scores([0.80, 0.81, 0.79, 0.80])
        result = self.checker.check_sequence_consistency(scores)
        assert result.is_consistent is True

    def test_inconsistent_sequence(self):
        # Use alternating 0/1 values: mean=0.5, var=0.25, kappa=1-0.25/0.5=0.5 < 0.70
        scores = self._make_scores([0.0, 1.0, 0.0, 1.0])
        result = self.checker.check_sequence_consistency(scores)
        assert result.is_consistent is False

    def test_returns_correct_type(self):
        scores = self._make_scores([0.7, 0.75])
        result = self.checker.check_sequence_consistency(scores)
        assert isinstance(result, NormativeConsistencyResult)

    def test_kappa_in_unit_interval(self):
        scores = self._make_scores([0.5, 0.6, 0.7, 0.8])
        result = self.checker.check_sequence_consistency(scores)
        assert 0.0 <= result.consistency_score <= 1.0

    def test_identical_scores_yield_perfect_consistency(self):
        scores = self._make_scores([0.75, 0.75, 0.75])
        result = self.checker.check_sequence_consistency(scores)
        assert result.variance == pytest.approx(0.0)

    def test_mean_correct(self):
        scores = self._make_scores([0.6, 0.8])
        result = self.checker.check_sequence_consistency(scores)
        assert result.mean == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# KritikalitaetsChecker - assess (full report)
# ---------------------------------------------------------------------------


class TestAssessReport:
    def setup_method(self):
        self.checker = KritikalitaetsChecker()
        self.engine = GemeinwohlEngine()

    def test_returns_report(self):
        score = self.engine.compute_score(entropy=0.3)
        report = self.checker.assess(score)
        assert isinstance(report, KritikalitaetsReport)

    def test_report_contains_level(self):
        score = self.engine.compute_score(entropy=0.3)
        report = self.checker.assess(score)
        assert isinstance(report.level, KritikalitaetsLevel)

    def test_report_contains_score(self):
        score = self.engine.compute_score(entropy=0.3)
        report = self.checker.assess(score)
        assert report.score is score

    def test_report_has_recommendations(self):
        score = self.engine.compute_score(entropy=0.3)
        report = self.checker.assess(score)
        assert len(report.recommendations) > 0

    def test_emergency_has_halt_recommendation(self):
        score = GemeinwohlScore(value=0.1, entropy=0.9, models=[])
        report = self.checker.assess(score)
        assert any("HALT" in r or "halt" in r.lower() for r in report.recommendations)

    def test_to_dict_keys(self):
        score = self.engine.compute_score(entropy=0.5)
        report = self.checker.assess(score)
        d = report.to_dict()
        assert "level" in d
        assert "score" in d
        assert "implications" in d
        assert "recommendations" in d

    def test_safe_report_recommendations_positive(self):
        score = GemeinwohlScore(value=0.9, entropy=0.1, models=[])
        report = self.checker.assess(score)
        assert report.level == KritikalitaetsLevel.SAFE
        assert any("monitoring" in r.lower() for r in report.recommendations)
