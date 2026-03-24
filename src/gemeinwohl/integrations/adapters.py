"""Integration adapters for the GenesisAeon full-stack optional dependencies.

Each adapter follows the :class:`BasePackageAdapter` contract, exposing a
``ping()`` method that returns :class:`IntegrationResult` regardless of whether
the optional package is installed.  This enables contract-tests to run in the
base environment and full-stack tests when the extras are present.

Supported packages
------------------
- ``unified-mandala`` ≥ 0.2.0
- ``worldview`` ≥ 0.1.0
- ``aeon-ai`` ≥ 0.2.0
- ``genesis-os`` ≥ 0.2.0
- ``universums-sim`` ≥ 0.1.0
- ``entropy-governance`` ≥ 0.1.0
- ``sigillin`` ≥ 0.1.0
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PackageStatus(Enum):
    """Installation and connectivity status for an optional dependency."""

    AVAILABLE = "available"
    """Package installed and responsive."""

    UNAVAILABLE = "unavailable"
    """Package not installed."""

    ERROR = "error"
    """Package installed but raised an error during ping."""


@dataclass(frozen=True)
class IntegrationResult:
    """Result of a package adapter ping.

    Attributes:
        package_name: PyPI name of the package.
        status: Current :class:`PackageStatus`.
        version: Detected version string, or ``None`` if unavailable.
        metadata: Arbitrary adapter-specific context.
        error: Error message if status is ``ERROR``.
    """

    package_name: str
    status: PackageStatus
    version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def is_available(self) -> bool:
        """True when the package is available and error-free."""
        return self.status == PackageStatus.AVAILABLE


class BasePackageAdapter:
    """Abstract base for optional package adapters.

    Args:
        import_name: Python import name (may differ from PyPI name).
        package_name: PyPI distribution name.
        min_version: Minimum required version string.
    """

    def __init__(
        self,
        import_name: str,
        package_name: str,
        min_version: str = "0.0.0",
    ) -> None:
        self._import_name = import_name
        self._package_name = package_name
        self._min_version = min_version

    @property
    def package_name(self) -> str:
        """Return the PyPI package name."""
        return self._package_name

    def ping(self) -> IntegrationResult:
        """Attempt to import the package and retrieve its version.

        Returns:
            :class:`IntegrationResult` with the current status.
        """
        try:
            mod = importlib.import_module(self._import_name)
            version = getattr(mod, "__version__", None)
            return IntegrationResult(
                package_name=self._package_name,
                status=PackageStatus.AVAILABLE,
                version=str(version) if version else "unknown",
            )
        except ImportError:
            return IntegrationResult(
                package_name=self._package_name,
                status=PackageStatus.UNAVAILABLE,
            )
        except Exception as exc:  # noqa: BLE001
            return IntegrationResult(
                package_name=self._package_name,
                status=PackageStatus.ERROR,
                error=str(exc),
            )


# ---------------------------------------------------------------------------
# Concrete adapters
# ---------------------------------------------------------------------------


class UnifiedMandalAdapter(BasePackageAdapter):
    """Adapter for ``unified-mandala`` ≥ 0.2.0."""

    def __init__(self) -> None:
        super().__init__("unified_mandala", "unified-mandala", "0.2.0")


class WorldviewAdapter(BasePackageAdapter):
    """Adapter for ``worldview`` ≥ 0.1.0."""

    def __init__(self) -> None:
        super().__init__("worldview", "worldview", "0.1.0")


class AeonAIAdapter(BasePackageAdapter):
    """Adapter for ``aeon-ai`` ≥ 0.2.0."""

    def __init__(self) -> None:
        super().__init__("aeon_ai", "aeon-ai", "0.2.0")


class GenesisOSAdapter(BasePackageAdapter):
    """Adapter for ``genesis-os`` ≥ 0.2.0."""

    def __init__(self) -> None:
        super().__init__("genesis_os", "genesis-os", "0.2.0")


class UniversumsSimAdapter(BasePackageAdapter):
    """Adapter for ``universums-sim`` ≥ 0.1.0."""

    def __init__(self) -> None:
        super().__init__("universums_sim", "universums-sim", "0.1.0")


class EntropyGovernanceAdapter(BasePackageAdapter):
    """Adapter for ``entropy-governance`` ≥ 0.1.0."""

    def __init__(self) -> None:
        super().__init__("entropy_governance", "entropy-governance", "0.1.0")


class SigillinAdapter(BasePackageAdapter):
    """Adapter for ``sigillin`` ≥ 0.1.0."""

    def __init__(self) -> None:
        super().__init__("sigillin", "sigillin", "0.1.0")


# Registry of all known adapters
ALL_ADAPTERS: list[BasePackageAdapter] = [
    UnifiedMandalAdapter(),
    WorldviewAdapter(),
    AeonAIAdapter(),
    GenesisOSAdapter(),
    UniversumsSimAdapter(),
    EntropyGovernanceAdapter(),
    SigillinAdapter(),
]


def ping_all() -> dict[str, IntegrationResult]:
    """Ping all registered adapters.

    Returns:
        Mapping of package name → :class:`IntegrationResult`.
    """
    return {adapter.package_name: adapter.ping() for adapter in ALL_ADAPTERS}
