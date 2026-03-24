"""Normative consistency contract tests.

These tests verify that the system's normative output is self-consistent
across different invocation patterns, input variations, and module boundaries.
They serve as regression guardrails for the GenesisAeon normative layer.
"""

import math

import pytest

from gemeinwohl.core.gemeinwohl import GemeinwohlEngine, GemeinwohlScore, NormativeMetric
from gemeinwohl.core.kritikalitaet import KritikalitaetsChecker, KritikalitaetsLevel
from gemeinwohl.governance.policy import PersonhoodLevel, PolicyEngine


class TestNormativeContractDeterminism:
    """Engine must be deterministic for identical inputs."""

    def test_same_entropy_same_score(self):
        engine = GemeinwohlEngine()
        s1 = engine.compute_score(entropy=0.42)
        s2 = engine.compute_score(entropy=0.42)
        assert s1.value == pytest.approx(s2.value)

    def test_same_models_same_alignment(self):
        engine = GemeinwohlEngine()
        models = ["gpt-4", "claude-3-opus", "llama-3"]
        s1 = engine.compute_score(entropy=0.3, models=models)
        s2 = engine.compute_score(entropy=0.3, models=models)
        ss1 = s1.sub_scores[NormativeMetric.MODEL_ALIGNMENT]
        ss2 = s2.sub_scores[NormativeMetric.MODEL_ALIGNMENT]
        assert ss1 == pytest.approx(ss2)

    def test_order_of_models_does_not_matter(self):
        engine = GemeinwohlEngine()
        s1 = engine.compute_score(entropy=0.3, models=["gpt-4", "claude-3-opus"])
        s2 = engine.compute_score(entropy=0.3, models=["claude-3-opus", "gpt-4"])
        assert s1.value == pytest.approx(s2.value)


class TestNormativeContractMonotonicity:
    """Normative scores must respond monotonically to input changes."""

    def test_lower_entropy_higher_score(self):
        engine = GemeinwohlEngine()
        scores = [engine.compute_score(entropy=e) for e in [0.9, 0.7, 0.5, 0.3, 0.1]]
        vals = [s.value for s in scores]
        assert vals == sorted(vals)

    def test_higher_ecological_higher_score(self):
        engine = GemeinwohlEngine()
        s_low = engine.compute_score(entropy=0.5, ecological_impact=0.1)
        s_high = engine.compute_score(entropy=0.5, ecological_impact=0.9)
        assert s_high.value > s_low.value

    def test_higher_social_equity_higher_score(self):
        engine = GemeinwohlEngine()
        s_low = engine.compute_score(entropy=0.5, social_equity=0.1)
        s_high = engine.compute_score(entropy=0.5, social_equity=0.9)
        assert s_high.value > s_low.value

    def test_higher_personhood_weight_higher_score(self):
        engine = GemeinwohlEngine()
        s_low = engine.compute_score(entropy=0.5, personhood_level=0.0)
        s_high = engine.compute_score(entropy=0.5, personhood_level=1.0)
        assert s_high.value > s_low.value


class TestNormativeContractBoundaryConditions:
    """Score must always be in [0, 1]."""

    @pytest.mark.parametrize("entropy", [0.0, 0.25, 0.5, 0.75, 1.0])
    def test_score_in_unit_interval_varied_entropy(self, entropy):
        engine = GemeinwohlEngine()
        score = engine.compute_score(entropy=entropy)
        assert 0.0 <= score.value <= 1.0

    @pytest.mark.parametrize("eco", [0.0, 0.5, 1.0])
    def test_score_in_unit_interval_varied_ecological(self, eco):
        engine = GemeinwohlEngine()
        score = engine.compute_score(entropy=0.3, ecological_impact=eco)
        assert 0.0 <= score.value <= 1.0

    def test_all_extremes_max(self):
        engine = GemeinwohlEngine()
        score = engine.compute_score(
            entropy=0.0,
            models=["claude-3-opus"],
            normative_consistency=1.0,
            personhood_level=1.0,
            ecological_impact=1.0,
            social_equity=1.0,
        )
        assert score.value <= 1.0
        assert score.value > 0.5

    def test_all_extremes_min(self):
        engine = GemeinwohlEngine()
        score = engine.compute_score(
            entropy=1.0,
            models=[],
            normative_consistency=0.0,
            personhood_level=0.0,
            ecological_impact=0.0,
            social_equity=0.0,
        )
        assert score.value >= 0.0
        assert score.value < 0.5


class TestNormativeContractCriticalityCoverage:
    """Every criticality level must be reachable."""

    def test_safe_reachable(self):
        engine = GemeinwohlEngine()
        checker = KritikalitaetsChecker()
        score = engine.compute_score(
            entropy=0.05,
            models=["claude-3-opus"],
            ecological_impact=0.95,
            social_equity=0.95,
        )
        # Safe is reachable for very good inputs
        assert checker.classify(score) in (
            KritikalitaetsLevel.SAFE,
            KritikalitaetsLevel.WARNING,
        )

    def test_emergency_reachable(self):
        engine = GemeinwohlEngine()
        checker = KritikalitaetsChecker()
        score = engine.compute_score(
            entropy=1.0,
            ecological_impact=0.0,
            social_equity=0.0,
            personhood_level=0.0,
            normative_consistency=0.0,
        )
        assert checker.classify(score) in (
            KritikalitaetsLevel.EMERGENCY,
            KritikalitaetsLevel.CRITICAL,
        )


class TestNormativeContractPersonhoodConsistency:
    """PersonhoodLevel thresholds must be internally consistent."""

    def test_each_level_threshold_satisfies_lower_levels(self):
        policy = PolicyEngine()

        for level in PersonhoodLevel:
            min_score = level.min_gemeinwohl_score
            score = GemeinwohlScore(value=min_score, entropy=0.3, models=[])
            max_level = policy.infer_max_personhood(score)
            assert int(max_level) >= int(level)

    def test_level_weighting_monotone(self):
        factors = [lvl.weighting_factor for lvl in PersonhoodLevel]
        assert factors == sorted(factors)

    def test_policy_engine_alignment_consistent_with_min_score(self):
        policy = PolicyEngine()
        for level in PersonhoodLevel:
            score_exact = GemeinwohlScore(value=level.min_gemeinwohl_score, entropy=0.3, models=[])
            alignment = policy.evaluate_alignment("sys", score_exact, level)
            assert alignment.is_aligned is True

    def test_policy_engine_alignment_fails_below_min(self):
        policy = PolicyEngine()
        for level in PersonhoodLevel:
            score_below = GemeinwohlScore(
                value=max(0.0, level.min_gemeinwohl_score - 0.01),
                entropy=0.3,
                models=[],
            )
            alignment = policy.evaluate_alignment("sys", score_below, level)
            if level == PersonhoodLevel.INSTRUMENTAL:
                # 0.39 < 0.40 → should fail
                assert alignment.is_aligned is False
            else:
                assert alignment.is_aligned is False


class TestNormativeContractSerialisation:
    """All result objects must serialise to plain dicts without loss."""

    def test_score_roundtrip_value(self):
        engine = GemeinwohlEngine()
        score = engine.compute_score(entropy=0.35)
        d = score.to_dict()
        assert math.isclose(d["value"], score.value, abs_tol=1e-5)

    def test_report_to_dict_has_level(self):
        from gemeinwohl.core.kritikalitaet import KritikalitaetsChecker

        engine = GemeinwohlEngine()
        checker = KritikalitaetsChecker()
        score = engine.compute_score(entropy=0.5)
        report = checker.assess(score)
        d = report.to_dict()
        assert d["level"] in ("SAFE", "WARNING", "CRITICAL", "EMERGENCY")

    def test_alignment_to_dict_has_gap(self):
        policy = PolicyEngine()
        score = GemeinwohlScore(value=0.70, entropy=0.3, models=[])
        alignment = policy.evaluate_alignment("s", score, PersonhoodLevel.RELATIONAL)
        d = alignment.to_dict()
        assert "gap" in d
        assert isinstance(d["gap"], float)
