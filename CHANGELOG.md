# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] – 2026-03-24

### Added

- **GemeinwohlEngine** with six-dimensional normative metric formula
- **NormativeWeights** frozen dataclass with validation
- **GemeinwohlScore** result container with qualitative interpretation labels
- **KritikalitaetsChecker** with four-level criticality classification (SAFE/WARNING/CRITICAL/EMERGENCY)
- **EthicalImplication** framework with eight built-in implication rules (E001–E008)
- **NormativeConsistencyResult** for time-series sequential consistency analysis
- **PersonhoodLevel** five-tier AI personhood model with minimum score thresholds
- **PolicyEngine** with four built-in governance rules (P001–P004)
- **GemeinwohlAlignment** alignment decision container
- **Typer CLI**: `gemeinwohl assess`, `gemeinwohl policy infer`, `gemeinwohl policy rules`, `gemeinwohl kritikalitaet check`
- Integration adapters for: `unified-mandala`, `worldview`, `aeon-ai`, `genesis-os`, `universums-sim`, `entropy-governance`, `sigillin`
- `[full-stack]` optional dependency group for the full GenesisAeon ecosystem
- MkDocs documentation with KaTeX math rendering (mkdocs --strict compliant)
- GitHub Actions CI workflow (lint + mypy + tests on Python 3.10/3.11/3.12)
- GitHub Actions release workflow (PyPI trusted publisher + GitHub Pages + GitHub Release)
- Zenodo metadata for scientific citation (`.zenodo.json`)
- >150 tests across unit, integration, and contract test suites with >99% coverage
