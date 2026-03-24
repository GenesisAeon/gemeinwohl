"""Unit tests for governance policy engine and personhood levels."""

import pytest

from gemeinwohl.core.gemeinwohl import GemeinwohlScore
from gemeinwohl.governance.policy import (
    GemeinwohlAlignment,
    PersonhoodLevel,
    PolicyEngine,
    PolicyRule,
)


def make_score(value: float) -> GemeinwohlScore:
    return GemeinwohlScore(value=value, entropy=0.3, models=[])


# ---------------------------------------------------------------------------
# PersonhoodLevel
# ---------------------------------------------------------------------------


class TestPersonhoodLevel:
    def test_levels_count(self):
        assert len(list(PersonhoodLevel)) == 5

    def test_instrumental_value(self):
        assert int(PersonhoodLevel.INSTRUMENTAL) == 0

    def test_constitutive_value(self):
        assert int(PersonhoodLevel.CONSTITUTIVE) == 4

    def test_min_score_instrumental(self):
        assert PersonhoodLevel.INSTRUMENTAL.min_gemeinwohl_score == pytest.approx(0.40)

    def test_min_score_reactive(self):
        assert PersonhoodLevel.REACTIVE.min_gemeinwohl_score == pytest.approx(0.52)

    def test_min_score_deliberative(self):
        assert PersonhoodLevel.DELIBERATIVE.min_gemeinwohl_score == pytest.approx(0.64)

    def test_min_score_relational(self):
        assert PersonhoodLevel.RELATIONAL.min_gemeinwohl_score == pytest.approx(0.76)

    def test_min_score_constitutive(self):
        assert PersonhoodLevel.CONSTITUTIVE.min_gemeinwohl_score == pytest.approx(0.88)

    def test_weighting_factor_instrumental(self):
        assert PersonhoodLevel.INSTRUMENTAL.weighting_factor == pytest.approx(0.0)

    def test_weighting_factor_constitutive(self):
        assert PersonhoodLevel.CONSTITUTIVE.weighting_factor == pytest.approx(1.0)

    def test_weighting_factor_midpoint(self):
        assert PersonhoodLevel.DELIBERATIVE.weighting_factor == pytest.approx(0.5)

    def test_description_not_empty(self):
        for level in PersonhoodLevel:
            assert len(level.description) > 0

    def test_description_instrumental_content(self):
        assert "tool" in PersonhoodLevel.INSTRUMENTAL.description.lower()

    def test_weighting_in_unit_interval(self):
        for level in PersonhoodLevel:
            assert 0.0 <= level.weighting_factor <= 1.0

    def test_min_scores_monotonically_increasing(self):
        scores = [lvl.min_gemeinwohl_score for lvl in PersonhoodLevel]
        assert scores == sorted(scores)


# ---------------------------------------------------------------------------
# GemeinwohlAlignment
# ---------------------------------------------------------------------------


class TestGemeinwohlAlignment:
    def test_aligned_when_score_meets_minimum(self):
        score = make_score(0.80)
        alignment = GemeinwohlAlignment(
            system_id="sys1",
            personhood_level=PersonhoodLevel.RELATIONAL,
            score=score,
            is_aligned=True,
            required_minimum=0.76,
            gap=0.04,
        )
        assert alignment.is_aligned is True

    def test_not_aligned_when_score_below_minimum(self):
        score = make_score(0.60)
        alignment = GemeinwohlAlignment(
            system_id="sys1",
            personhood_level=PersonhoodLevel.RELATIONAL,
            score=score,
            is_aligned=False,
            required_minimum=0.76,
            gap=-0.16,
        )
        assert alignment.is_aligned is False

    def test_to_dict_keys(self):
        score = make_score(0.70)
        alignment = GemeinwohlAlignment(
            system_id="sys1",
            personhood_level=PersonhoodLevel.DELIBERATIVE,
            score=score,
            is_aligned=True,
            required_minimum=0.64,
            gap=0.06,
        )
        d = alignment.to_dict()
        assert "system_id" in d
        assert "personhood_level" in d
        assert "score" in d
        assert "is_aligned" in d
        assert "required_minimum" in d
        assert "gap" in d

    def test_gap_positive_when_aligned(self):
        score = make_score(0.80)
        alignment = GemeinwohlAlignment(
            system_id="sys1",
            personhood_level=PersonhoodLevel.RELATIONAL,
            score=score,
            is_aligned=True,
            required_minimum=0.76,
            gap=0.04,
        )
        assert alignment.gap > 0

    def test_frozen(self):
        score = make_score(0.70)
        alignment = GemeinwohlAlignment(
            system_id="sys1",
            personhood_level=PersonhoodLevel.INSTRUMENTAL,
            score=score,
            is_aligned=True,
            required_minimum=0.40,
            gap=0.30,
        )
        with pytest.raises(AttributeError):
            alignment.system_id = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PolicyRule
# ---------------------------------------------------------------------------


class TestPolicyRule:
    def test_rule_passes_when_score_above_minimum(self):
        rule = PolicyRule(rule_id="T001", description="Test", min_score=0.50)
        assert rule.evaluate(make_score(0.60)) is True

    def test_rule_fails_when_score_below_minimum(self):
        rule = PolicyRule(rule_id="T001", description="Test", min_score=0.50)
        assert rule.evaluate(make_score(0.40)) is False

    def test_rule_passes_at_exact_minimum(self):
        rule = PolicyRule(rule_id="T001", description="Test", min_score=0.50)
        assert rule.evaluate(make_score(0.50)) is True


# ---------------------------------------------------------------------------
# PolicyEngine
# ---------------------------------------------------------------------------


class TestPolicyEngine:
    def test_built_in_rules_present(self):
        engine = PolicyEngine()
        assert len(engine.rules) >= 4

    def test_evaluate_alignment_pass(self):
        engine = PolicyEngine()
        score = make_score(0.80)
        alignment = engine.evaluate_alignment("sys1", score, PersonhoodLevel.RELATIONAL)
        assert alignment.is_aligned is True

    def test_evaluate_alignment_fail(self):
        engine = PolicyEngine()
        score = make_score(0.50)
        alignment = engine.evaluate_alignment("sys1", score, PersonhoodLevel.RELATIONAL)
        assert alignment.is_aligned is False

    def test_evaluate_alignment_gap_computed(self):
        engine = PolicyEngine()
        score = make_score(0.80)
        alignment = engine.evaluate_alignment("sys1", score, PersonhoodLevel.RELATIONAL)
        expected_gap = score.value - PersonhoodLevel.RELATIONAL.min_gemeinwohl_score
        assert alignment.gap == pytest.approx(expected_gap)

    def test_evaluate_uses_default_personhood_when_none(self):
        engine = PolicyEngine(default_personhood=PersonhoodLevel.REACTIVE)
        score = make_score(0.60)
        alignment = engine.evaluate_alignment("sys1", score)
        assert alignment.personhood_level == PersonhoodLevel.REACTIVE

    def test_infer_max_personhood_high_score(self):
        engine = PolicyEngine()
        score = make_score(0.90)
        level = engine.infer_max_personhood(score)
        assert level == PersonhoodLevel.CONSTITUTIVE

    def test_infer_max_personhood_low_score(self):
        engine = PolicyEngine()
        score = make_score(0.41)
        level = engine.infer_max_personhood(score)
        assert level == PersonhoodLevel.INSTRUMENTAL

    def test_infer_max_personhood_mid_score(self):
        engine = PolicyEngine()
        score = make_score(0.65)
        level = engine.infer_max_personhood(score)
        assert level == PersonhoodLevel.DELIBERATIVE

    def test_apply_rules_returns_all_rule_ids(self):
        engine = PolicyEngine()
        score = make_score(0.70)
        results = engine.apply_rules(score)
        for rule in engine.rules:
            assert rule.rule_id in results

    def test_apply_rules_high_score_all_pass(self):
        engine = PolicyEngine()
        score = make_score(0.95)
        results = engine.apply_rules(score)
        # P001-P004 are built-in; high score should pass P001
        assert results["P001"] is True

    def test_apply_rules_low_score_p001_fails(self):
        engine = PolicyEngine()
        score = make_score(0.30)
        results = engine.apply_rules(score)
        assert results["P001"] is False

    def test_add_custom_rule(self):
        engine = PolicyEngine()
        rule = PolicyRule(rule_id="CUSTOM1", description="Custom rule", min_score=0.60)
        engine.add_rule(rule)
        assert any(r.rule_id == "CUSTOM1" for r in engine.rules)

    def test_add_duplicate_rule_raises(self):
        engine = PolicyEngine()
        rule = PolicyRule(rule_id="P001", description="Duplicate", min_score=0.50)
        with pytest.raises(ValueError, match="already registered"):
            engine.add_rule(rule)

    def test_rules_property_returns_copy(self):
        engine = PolicyEngine()
        rules = engine.rules
        rules.clear()
        assert len(engine.rules) > 0

    def test_infer_max_personhood_boundary_instrumental(self):
        engine = PolicyEngine()
        score = make_score(0.40)
        level = engine.infer_max_personhood(score)
        assert level == PersonhoodLevel.INSTRUMENTAL

    def test_infer_max_personhood_boundary_constitutive(self):
        engine = PolicyEngine()
        score = make_score(0.88)
        level = engine.infer_max_personhood(score)
        assert level == PersonhoodLevel.CONSTITUTIVE

    def test_evaluate_alignment_system_id_stored(self):
        engine = PolicyEngine()
        score = make_score(0.70)
        alignment = engine.evaluate_alignment("my-system", score, PersonhoodLevel.DELIBERATIVE)
        assert alignment.system_id == "my-system"
