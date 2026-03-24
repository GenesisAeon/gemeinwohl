"""Tests for the top-level package __init__."""

import gemeinwohl


class TestPackageInit:
    def test_version_string(self):
        assert gemeinwohl.__version__ == "0.1.0"

    def test_author(self):
        assert gemeinwohl.__author__ == "GenesisAeon"

    def test_license(self):
        assert gemeinwohl.__license__ == "MIT"

    def test_gemeinwohl_engine_exported(self):
        assert hasattr(gemeinwohl, "GemeinwohlEngine")

    def test_gemeinwohl_score_exported(self):
        assert hasattr(gemeinwohl, "GemeinwohlScore")

    def test_normative_metric_exported(self):
        assert hasattr(gemeinwohl, "NormativeMetric")

    def test_kritikalitaets_checker_exported(self):
        assert hasattr(gemeinwohl, "KritikalitaetsChecker")

    def test_ethical_implication_exported(self):
        assert hasattr(gemeinwohl, "EthicalImplication")

    def test_normative_consistency_result_exported(self):
        assert hasattr(gemeinwohl, "NormativeConsistencyResult")

    def test_gemeinwohl_alignment_exported(self):
        assert hasattr(gemeinwohl, "GemeinwohlAlignment")

    def test_personhood_level_exported(self):
        assert hasattr(gemeinwohl, "PersonhoodLevel")

    def test_policy_engine_exported(self):
        assert hasattr(gemeinwohl, "PolicyEngine")

    def test_all_list_complete(self):
        for name in gemeinwohl.__all__:
            assert hasattr(gemeinwohl, name)
