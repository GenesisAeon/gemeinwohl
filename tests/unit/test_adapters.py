"""Unit tests for integration adapters."""

from unittest.mock import patch

import pytest

from gemeinwohl.integrations.adapters import (
    ALL_ADAPTERS,
    BasePackageAdapter,
    IntegrationResult,
    PackageStatus,
    SigillinAdapter,
    UnifiedMandalAdapter,
    ping_all,
)


class TestPackageStatus:
    def test_available_value(self):
        assert PackageStatus.AVAILABLE.value == "available"

    def test_unavailable_value(self):
        assert PackageStatus.UNAVAILABLE.value == "unavailable"

    def test_error_value(self):
        assert PackageStatus.ERROR.value == "error"


class TestIntegrationResult:
    def test_is_available_true(self):
        r = IntegrationResult(package_name="pkg", status=PackageStatus.AVAILABLE)
        assert r.is_available is True

    def test_is_available_false_unavailable(self):
        r = IntegrationResult(package_name="pkg", status=PackageStatus.UNAVAILABLE)
        assert r.is_available is False

    def test_is_available_false_error(self):
        r = IntegrationResult(package_name="pkg", status=PackageStatus.ERROR)
        assert r.is_available is False

    def test_frozen(self):
        r = IntegrationResult(package_name="pkg", status=PackageStatus.UNAVAILABLE)
        with pytest.raises(AttributeError):
            r.package_name = "other"  # type: ignore[misc]

    def test_version_defaults_none(self):
        r = IntegrationResult(package_name="pkg", status=PackageStatus.UNAVAILABLE)
        assert r.version is None

    def test_error_defaults_none(self):
        r = IntegrationResult(package_name="pkg", status=PackageStatus.UNAVAILABLE)
        assert r.error is None


class TestBasePackageAdapter:
    def test_ping_missing_package_returns_unavailable(self):
        adapter = BasePackageAdapter(
            import_name="__totally_nonexistent_pkg__",
            package_name="nonexistent-pkg",
        )
        result = adapter.ping()
        assert result.status == PackageStatus.UNAVAILABLE

    def test_ping_existing_module_returns_available(self):
        adapter = BasePackageAdapter(import_name="math", package_name="math")
        result = adapter.ping()
        assert result.status == PackageStatus.AVAILABLE

    def test_package_name_property(self):
        adapter = BasePackageAdapter(import_name="math", package_name="python-math")
        assert adapter.package_name == "python-math"

    def test_ping_result_package_name_matches(self):
        adapter = BasePackageAdapter(import_name="math", package_name="python-math")
        result = adapter.ping()
        assert result.package_name == "python-math"


class TestConcreteAdapters:
    def test_unified_mandala_adapter_package_name(self):
        a = UnifiedMandalAdapter()
        assert a.package_name == "unified-mandala"

    def test_sigillin_adapter_package_name(self):
        a = SigillinAdapter()
        assert a.package_name == "sigillin"

    def test_all_adapters_count(self):
        assert len(ALL_ADAPTERS) == 7

    def test_all_adapters_have_package_name(self):
        for adapter in ALL_ADAPTERS:
            assert len(adapter.package_name) > 0

    def test_ping_all_returns_all_packages(self):
        results = ping_all()
        assert len(results) == 7

    def test_ping_all_values_are_integration_results(self):
        results = ping_all()
        for val in results.values():
            assert isinstance(val, IntegrationResult)

    def test_ping_all_unavailable_packages_graceful(self):
        results = ping_all()
        for result in results.values():
            assert result.status in (
                PackageStatus.AVAILABLE,
                PackageStatus.UNAVAILABLE,
                PackageStatus.ERROR,
            )

    def test_ping_returns_error_on_unexpected_exception(self):
        adapter = BasePackageAdapter(import_name="math", package_name="math")
        with patch("importlib.import_module", side_effect=RuntimeError("boom")):
            result = adapter.ping()
        assert result.status == PackageStatus.ERROR
        assert result.error == "boom"
        assert result.is_available is False
