"""Contract tests for all optional full-stack package adapters.

These tests run regardless of whether the optional packages are installed.
They verify the adapter contract (ping API) and graceful degradation.
"""

import pytest

from gemeinwohl.integrations.adapters import (
    ALL_ADAPTERS,
    AeonAIAdapter,
    BasePackageAdapter,
    EntropyGovernanceAdapter,
    GenesisOSAdapter,
    IntegrationResult,
    PackageStatus,
    SigillinAdapter,
    UnifiedMandalAdapter,
    UniversumsSimAdapter,
    WorldviewAdapter,
    ping_all,
)


class TestAdapterContract:
    """Verify the BasePackageAdapter contract for all concrete adapters."""

    @pytest.mark.parametrize(
        "adapter_cls",
        [
            UnifiedMandalAdapter,
            WorldviewAdapter,
            AeonAIAdapter,
            GenesisOSAdapter,
            UniversumsSimAdapter,
            EntropyGovernanceAdapter,
            SigillinAdapter,
        ],
    )
    def test_ping_returns_integration_result(self, adapter_cls):
        adapter = adapter_cls()
        result = adapter.ping()
        assert isinstance(result, IntegrationResult)

    @pytest.mark.parametrize(
        "adapter_cls",
        [
            UnifiedMandalAdapter,
            WorldviewAdapter,
            AeonAIAdapter,
            GenesisOSAdapter,
            UniversumsSimAdapter,
            EntropyGovernanceAdapter,
            SigillinAdapter,
        ],
    )
    def test_ping_status_is_valid(self, adapter_cls):
        adapter = adapter_cls()
        result = adapter.ping()
        assert result.status in list(PackageStatus)

    @pytest.mark.parametrize(
        "adapter_cls",
        [
            UnifiedMandalAdapter,
            WorldviewAdapter,
            AeonAIAdapter,
            GenesisOSAdapter,
            UniversumsSimAdapter,
            EntropyGovernanceAdapter,
            SigillinAdapter,
        ],
    )
    def test_ping_package_name_non_empty(self, adapter_cls):
        adapter = adapter_cls()
        result = adapter.ping()
        assert len(result.package_name) > 0

    @pytest.mark.parametrize(
        "adapter_cls",
        [
            UnifiedMandalAdapter,
            WorldviewAdapter,
            AeonAIAdapter,
            GenesisOSAdapter,
            UniversumsSimAdapter,
            EntropyGovernanceAdapter,
            SigillinAdapter,
        ],
    )
    def test_ping_no_exception(self, adapter_cls):
        adapter = adapter_cls()
        # Should never raise regardless of whether package is installed
        try:
            adapter.ping()
        except Exception as e:
            pytest.fail(f"{adapter_cls.__name__}.ping() raised unexpectedly: {e}")

    def test_ping_all_returns_seven_entries(self):
        results = ping_all()
        assert len(results) == 7

    def test_ping_all_keys_are_strings(self):
        results = ping_all()
        for key in results:
            assert isinstance(key, str)

    def test_all_adapters_registered(self):
        package_names = {a.package_name for a in ALL_ADAPTERS}
        expected = {
            "unified-mandala",
            "worldview",
            "aeon-ai",
            "genesis-os",
            "universums-sim",
            "entropy-governance",
            "sigillin",
        }
        assert package_names == expected

    def test_adapter_ping_idempotent(self):
        adapter = UnifiedMandalAdapter()
        r1 = adapter.ping()
        r2 = adapter.ping()
        assert r1.status == r2.status
        assert r1.package_name == r2.package_name

    def test_base_adapter_with_stdlib_module(self):
        adapter = BasePackageAdapter(import_name="json", package_name="json")
        result = adapter.ping()
        assert result.status == PackageStatus.AVAILABLE
        assert result.is_available is True

    def test_unified_mandala_package_name(self):
        assert UnifiedMandalAdapter().package_name == "unified-mandala"

    def test_worldview_package_name(self):
        assert WorldviewAdapter().package_name == "worldview"

    def test_aeon_ai_package_name(self):
        assert AeonAIAdapter().package_name == "aeon-ai"

    def test_genesis_os_package_name(self):
        assert GenesisOSAdapter().package_name == "genesis-os"

    def test_universums_sim_package_name(self):
        assert UniversumsSimAdapter().package_name == "universums-sim"

    def test_entropy_governance_package_name(self):
        assert EntropyGovernanceAdapter().package_name == "entropy-governance"

    def test_sigillin_package_name(self):
        assert SigillinAdapter().package_name == "sigillin"
