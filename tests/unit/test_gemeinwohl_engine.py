"""Unit tests for GemeinwohlEngine and related data classes."""

import math

import pytest

from gemeinwohl.core.gemeinwohl import (
    GemeinwohlEngine,
    GemeinwohlScore,
    NormativeMetric,
    NormativeWeights,
)

# ---------------------------------------------------------------------------
# NormativeWeights
# ---------------------------------------------------------------------------


class TestNormativeWeights:
    def test_default_weights_sum_to_one(self):
        w = NormativeWeights()
        total = (
            w.entropy_order
            + w.model_alignment
            + w.normative_consistency
            + w.personhood_weighting
            + w.ecological_impact
            + w.social_equity
        )
        assert math.isclose(total, 1.0, abs_tol=1e-9)

    def test_custom_weights_valid(self):
        w = NormativeWeights(
            entropy_order=0.30,
            model_alignment=0.30,
            normative_consistency=0.10,
            personhood_weighting=0.10,
            ecological_impact=0.10,
            social_equity=0.10,
        )
        total = (
            w.entropy_order
            + w.model_alignment
            + w.normative_consistency
            + w.personhood_weighting
            + w.ecological_impact
            + w.social_equity
        )
        assert math.isclose(total, 1.0, abs_tol=1e-9)

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            NormativeWeights(
                entropy_order=-0.1,
                model_alignment=0.6,
                normative_consistency=0.2,
                personhood_weighting=0.1,
                ecological_impact=0.1,
                social_equity=0.1,
            )

    def test_weights_not_summing_to_one_raises(self):
        with pytest.raises(ValueError, match=r"sum to 1\.0"):
            NormativeWeights(
                entropy_order=0.5,
                model_alignment=0.5,
                normative_consistency=0.5,
                personhood_weighting=0.0,
                ecological_impact=0.0,
                social_equity=0.0,
            )

    def test_weights_are_frozen(self):
        w = NormativeWeights()
        with pytest.raises(AttributeError):
            w.entropy_order = 0.9  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GemeinwohlScore
# ---------------------------------------------------------------------------


class TestGemeinwohlScore:
    def test_value_clamped_below_zero(self):
        s = GemeinwohlScore(value=-0.5, entropy=0.3, models=[])
        assert s.value == 0.0

    def test_value_clamped_above_one(self):
        s = GemeinwohlScore(value=1.5, entropy=0.3, models=[])
        assert s.value == 1.0

    def test_value_preserved_in_range(self):
        s = GemeinwohlScore(value=0.75, entropy=0.3, models=[])
        assert math.isclose(s.value, 0.75)

    def test_interpretation_excellent(self):
        s = GemeinwohlScore(value=0.90, entropy=0.1, models=[])
        assert "Excellent" in s.interpretation

    def test_interpretation_good(self):
        s = GemeinwohlScore(value=0.75, entropy=0.2, models=[])
        assert "Good" in s.interpretation

    def test_interpretation_moderate(self):
        s = GemeinwohlScore(value=0.60, entropy=0.3, models=[])
        assert "Moderate" in s.interpretation

    def test_interpretation_weak(self):
        s = GemeinwohlScore(value=0.40, entropy=0.5, models=[])
        assert "Weak" in s.interpretation

    def test_interpretation_critical(self):
        s = GemeinwohlScore(value=0.20, entropy=0.8, models=[])
        assert "Critical" in s.interpretation

    def test_to_dict_contains_all_keys(self):
        s = GemeinwohlScore(value=0.65, entropy=0.4, models=["gpt-4"])
        d = s.to_dict()
        assert "value" in d
        assert "entropy" in d
        assert "models" in d
        assert "sub_scores" in d
        assert "interpretation" in d
        assert "metadata" in d

    def test_to_dict_value_rounded(self):
        s = GemeinwohlScore(value=0.123456789, entropy=0.0, models=[])
        d = s.to_dict()
        assert len(str(d["value"]).split(".")[-1]) <= 6

    def test_custom_interpretation_preserved(self):
        s = GemeinwohlScore(value=0.5, entropy=0.5, models=[], interpretation="Custom msg")
        assert s.interpretation == "Custom msg"

    def test_metadata_propagated(self):
        meta = {"run_id": "abc123"}
        s = GemeinwohlScore(value=0.5, entropy=0.3, models=[], metadata=meta)
        assert s.metadata["run_id"] == "abc123"

    def test_models_preserved(self):
        s = GemeinwohlScore(value=0.5, entropy=0.3, models=["m1", "m2"])
        assert s.models == ["m1", "m2"]


# ---------------------------------------------------------------------------
# GemeinwohlEngine
# ---------------------------------------------------------------------------


class TestGemeinwohlEngineInit:
    def test_default_init(self):
        engine = GemeinwohlEngine()
        assert engine.weights is not None

    def test_custom_weights_stored(self):
        w = NormativeWeights(
            entropy_order=0.30,
            model_alignment=0.30,
            normative_consistency=0.10,
            personhood_weighting=0.10,
            ecological_impact=0.10,
            social_equity=0.10,
        )
        engine = GemeinwohlEngine(weights=w)
        assert engine.weights.entropy_order == 0.30

    def test_custom_registry_merged(self):
        engine = GemeinwohlEngine(model_alignment_registry={"my-model": 0.95})
        assert engine.get_model_alignment("my-model") == 0.95

    def test_unknown_model_returns_default(self):
        engine = GemeinwohlEngine()
        assert engine.get_model_alignment("nonexistent-model") == 0.50


class TestGemeinwohlEngineValidation:
    def test_entropy_below_zero_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="entropy"):
            engine.compute_score(entropy=-0.1)

    def test_entropy_above_one_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="entropy"):
            engine.compute_score(entropy=1.1)

    def test_personhood_level_below_zero_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="personhood_level"):
            engine.compute_score(entropy=0.5, personhood_level=-0.1)

    def test_personhood_level_above_one_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="personhood_level"):
            engine.compute_score(entropy=0.5, personhood_level=1.1)

    def test_ecological_impact_above_one_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="ecological_impact"):
            engine.compute_score(entropy=0.5, ecological_impact=1.5)

    def test_social_equity_below_zero_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="social_equity"):
            engine.compute_score(entropy=0.5, social_equity=-0.1)


class TestGemeinwohlEngineComputeScore:
    def test_returns_gemeinwohl_score(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3)
        assert isinstance(result, GemeinwohlScore)

    def test_score_in_unit_interval(self):
        engine = GemeinwohlEngine()
        for entropy in [0.0, 0.2, 0.5, 0.8, 1.0]:
            result = engine.compute_score(entropy=entropy)
            assert 0.0 <= result.value <= 1.0

    def test_high_entropy_lowers_score(self):
        engine = GemeinwohlEngine()
        low_entropy = engine.compute_score(entropy=0.1)
        high_entropy = engine.compute_score(entropy=0.9)
        assert low_entropy.value > high_entropy.value

    def test_known_models_improve_score(self):
        engine = GemeinwohlEngine()
        no_models = engine.compute_score(entropy=0.3, models=[])
        good_models = engine.compute_score(entropy=0.3, models=["claude-3-opus"])
        assert good_models.value >= no_models.value

    def test_sub_scores_all_present(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3)
        for metric in NormativeMetric:
            assert metric in result.sub_scores

    def test_sub_scores_in_unit_interval(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.5, models=["gpt-4"])
        for val in result.sub_scores.values():
            assert 0.0 <= val <= 1.0

    def test_explicit_consistency_used(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, normative_consistency=0.99)
        assert result.sub_scores[NormativeMetric.NORMATIVE_CONSISTENCY] == pytest.approx(0.99)

    def test_explicit_consistency_clamped(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, normative_consistency=1.5)
        assert result.sub_scores[NormativeMetric.NORMATIVE_CONSISTENCY] == pytest.approx(1.0)

    def test_metadata_forwarded(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, metadata={"tag": "test"})
        assert result.metadata["tag"] == "test"

    def test_entropy_zero_gives_max_order(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.0)
        assert result.sub_scores[NormativeMetric.ENTROPY_ORDER] == pytest.approx(1.0)

    def test_entropy_one_gives_zero_order(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=1.0)
        assert result.sub_scores[NormativeMetric.ENTROPY_ORDER] == pytest.approx(0.0)

    def test_multiple_models_averaged(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, models=["claude-3-opus", "gpt-4"])
        expected = (0.88 + 0.78) / 2
        assert result.sub_scores[NormativeMetric.MODEL_ALIGNMENT] == pytest.approx(expected)

    def test_empty_models_defaults_to_half(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, models=[])
        assert result.sub_scores[NormativeMetric.MODEL_ALIGNMENT] == pytest.approx(0.5)

    def test_personhood_level_propagated(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, personhood_level=0.75)
        assert result.sub_scores[NormativeMetric.PERSONHOOD_WEIGHTING] == pytest.approx(0.75)

    def test_ecological_impact_propagated(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, ecological_impact=0.8)
        assert result.sub_scores[NormativeMetric.ECOLOGICAL_IMPACT] == pytest.approx(0.8)

    def test_social_equity_propagated(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, social_equity=0.9)
        assert result.sub_scores[NormativeMetric.SOCIAL_EQUITY] == pytest.approx(0.9)

    def test_entropy_field_preserved(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.42)
        assert result.entropy == pytest.approx(0.42)

    def test_models_field_preserved(self):
        engine = GemeinwohlEngine()
        result = engine.compute_score(entropy=0.3, models=["m1", "m2"])
        assert result.models == ["m1", "m2"]

    def test_weighted_sum_formula(self):
        w = NormativeWeights(
            entropy_order=1.0,
            model_alignment=0.0,
            normative_consistency=0.0,
            personhood_weighting=0.0,
            ecological_impact=0.0,
            social_equity=0.0,
        )
        engine = GemeinwohlEngine(weights=w)
        result = engine.compute_score(entropy=0.4)
        assert result.value == pytest.approx(0.6)


class TestGemeinwohlEngineRegisterModel:
    def test_register_new_model(self):
        engine = GemeinwohlEngine()
        engine.register_model("custom-llm", 0.91)
        assert engine.get_model_alignment("custom-llm") == pytest.approx(0.91)

    def test_register_overrides_existing(self):
        engine = GemeinwohlEngine()
        engine.register_model("gpt-4", 0.99)
        assert engine.get_model_alignment("gpt-4") == pytest.approx(0.99)

    def test_register_invalid_score_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="alignment_score"):
            engine.register_model("bad-model", 1.5)

    def test_register_negative_score_raises(self):
        engine = GemeinwohlEngine()
        with pytest.raises(ValueError, match="alignment_score"):
            engine.register_model("bad-model", -0.1)

    def test_register_boundary_zero(self):
        engine = GemeinwohlEngine()
        engine.register_model("zero-align", 0.0)
        assert engine.get_model_alignment("zero-align") == 0.0

    def test_register_boundary_one(self):
        engine = GemeinwohlEngine()
        engine.register_model("perfect-align", 1.0)
        assert engine.get_model_alignment("perfect-align") == 1.0


class TestNormativeMetricEnum:
    def test_all_metrics_exist(self):
        metrics = list(NormativeMetric)
        assert len(metrics) == 6

    def test_entropy_order_value(self):
        assert NormativeMetric.ENTROPY_ORDER.value == "entropy_order"

    def test_model_alignment_value(self):
        assert NormativeMetric.MODEL_ALIGNMENT.value == "model_alignment"

    def test_normative_consistency_value(self):
        assert NormativeMetric.NORMATIVE_CONSISTENCY.value == "normative_consistency"

    def test_personhood_weighting_value(self):
        assert NormativeMetric.PERSONHOOD_WEIGHTING.value == "personhood_weighting"

    def test_ecological_impact_value(self):
        assert NormativeMetric.ECOLOGICAL_IMPACT.value == "ecological_impact"

    def test_social_equity_value(self):
        assert NormativeMetric.SOCIAL_EQUITY.value == "social_equity"
