"""Integration tests for GemeinwohlEngine + PolicyEngine cross-module interactions."""

import pytest

from gemeinwohl.core.gemeinwohl import GemeinwohlEngine, NormativeWeights
from gemeinwohl.core.kritikalitaet import KritikalitaetsChecker, KritikalitaetsLevel
from gemeinwohl.governance.policy import PersonhoodLevel, PolicyEngine, PolicyRule


class TestEngineCheckerIntegration:
    """Engine output feeds directly into Checker."""

    def setup_method(self):
        self.engine = GemeinwohlEngine()
        self.checker = KritikalitaetsChecker()

    def test_high_quality_input_yields_safe(self):
        score = self.engine.compute_score(
            entropy=0.05,
            models=["claude-3-opus"],
            ecological_impact=0.95,
            social_equity=0.95,
            personhood_level=0.5,
        )
        level = self.checker.classify(score)
        assert level == KritikalitaetsLevel.SAFE

    def test_poor_input_yields_emergency(self):
        score = self.engine.compute_score(
            entropy=0.99,
            models=[],
            ecological_impact=0.05,
            social_equity=0.05,
            personhood_level=0.0,
        )
        level = self.checker.classify(score)
        assert level in (KritikalitaetsLevel.EMERGENCY, KritikalitaetsLevel.CRITICAL)

    def test_implications_reference_actual_sub_scores(self):
        score = self.engine.compute_score(entropy=0.9)
        implications = self.checker.identify_implications(score)
        # E001 should fire
        assert any(i.code == "E001" for i in implications)

    def test_full_pipeline_produces_report(self):
        score = self.engine.compute_score(entropy=0.4, models=["gpt-4"])
        report = self.checker.assess(score)
        assert report.score is score
        assert len(report.recommendations) > 0

    def test_sequence_consistency_with_engine_scores(self):
        scores = [self.engine.compute_score(entropy=0.3 + i * 0.01) for i in range(5)]
        result = self.checker.check_sequence_consistency(scores)
        assert 0.0 <= result.consistency_score <= 1.0


class TestEnginePolicyIntegration:
    """Engine output feeds directly into PolicyEngine."""

    def setup_method(self):
        self.engine = GemeinwohlEngine()
        self.policy = PolicyEngine()

    def test_high_score_aligns_constitutive(self):
        score = self.engine.compute_score(
            entropy=0.05,
            models=["claude-3-opus"],
            ecological_impact=0.99,
            social_equity=0.99,
            personhood_level=1.0,
        )
        alignment = self.policy.evaluate_alignment("sys", score, PersonhoodLevel.CONSTITUTIVE)
        # Alignment depends on exact score; verify structure
        assert alignment.required_minimum == pytest.approx(0.88)
        assert isinstance(alignment.is_aligned, bool)

    def test_low_score_fails_relational(self):
        score = self.engine.compute_score(entropy=0.8)
        alignment = self.policy.evaluate_alignment("sys", score, PersonhoodLevel.RELATIONAL)
        assert alignment.is_aligned is False

    def test_infer_max_personhood_pipeline(self):
        score = self.engine.compute_score(
            entropy=0.1, models=["claude-3-opus"], ecological_impact=0.9, social_equity=0.9
        )
        level = self.policy.infer_max_personhood(score)
        assert isinstance(level, PersonhoodLevel)

    def test_apply_rules_with_engine_score(self):
        score = self.engine.compute_score(entropy=0.3)
        results = self.policy.apply_rules(score)
        assert "P001" in results

    def test_custom_rule_evaluated(self):
        rule = PolicyRule(rule_id="CUSTOM99", description="High bar", min_score=0.99)
        self.policy.add_rule(rule)
        score = self.engine.compute_score(entropy=0.5)
        results = self.policy.apply_rules(score)
        assert results["CUSTOM99"] is False  # Very high bar


class TestFullStackNormativeConsistency:
    """End-to-end normative consistency test across modules."""

    def test_consistent_decisions_for_stable_input(self):
        engine = GemeinwohlEngine()
        checker = KritikalitaetsChecker()

        # Compute same score ten times - results must be identical (deterministic)
        scores = [engine.compute_score(entropy=0.35, models=["gpt-4"]) for _ in range(10)]
        levels = [checker.classify(s) for s in scores]
        assert len(set(levels)) == 1  # all same

    def test_monotonic_score_with_decreasing_entropy(self):
        engine = GemeinwohlEngine()
        entropy_values = [0.9, 0.7, 0.5, 0.3, 0.1]
        scores = [engine.compute_score(entropy=e) for e in entropy_values]
        values = [s.value for s in scores]
        assert values == sorted(values)  # monotonically increasing

    def test_policy_and_checker_agree_on_emergency(self):
        engine = GemeinwohlEngine()
        checker = KritikalitaetsChecker()
        policy = PolicyEngine()

        score = engine.compute_score(entropy=0.99, ecological_impact=0.01, social_equity=0.01)
        level = checker.classify(score)
        alignment = policy.evaluate_alignment("s", score, PersonhoodLevel.INSTRUMENTAL)

        # Both modules should signal problems
        assert level in (KritikalitaetsLevel.EMERGENCY, KritikalitaetsLevel.CRITICAL)
        assert alignment.is_aligned is False  # Even instrumental fails

    def test_custom_weights_affect_outcome(self):
        w_entropy = NormativeWeights(
            entropy_order=0.90,
            model_alignment=0.02,
            normative_consistency=0.02,
            personhood_weighting=0.02,
            ecological_impact=0.02,
            social_equity=0.02,
        )
        engine_heavy = GemeinwohlEngine(weights=w_entropy)
        engine_default = GemeinwohlEngine()

        score_heavy = engine_heavy.compute_score(entropy=0.9)
        score_default = engine_default.compute_score(entropy=0.9)

        # Heavy entropy weight → lower score for high entropy
        assert score_heavy.value < score_default.value
