# gemeinwohl

**Normative Common-Good Layer with Governance Metrics, Personhood Extension and Ethical Guardrails for GenesisAeon**

[![PyPI version](https://img.shields.io/pypi/v/gemeinwohl.svg)](https://pypi.org/project/gemeinwohl/)
[![Python](https://img.shields.io/pypi/pyversions/gemeinwohl.svg)](https://pypi.org/project/gemeinwohl/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/GenesisAeon/gemeinwohl/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/gemeinwohl/actions)
[![Coverage](https://img.shields.io/badge/coverage-%3E99%25-brightgreen)](https://github.com/GenesisAeon/gemeinwohl/actions)

---

## Overview

`gemeinwohl` implements a **normative metric layer** for AI governance within the GenesisAeon ecosystem. It provides:

- **GemeinwohlEngine** – computes the aggregate *Gemeinwohl Score* G in [0, 1]
- **KritikalitaetsChecker** – classifies scores into four criticality levels (SAFE / WARNING / CRITICAL / EMERGENCY)
- **PolicyEngine** – enforces a five-tier personhood model and governance rules
- **CLI** – `gemeinwohl assess`, `gemeinwohl policy`, `gemeinwohl kritikalitaet`
- **Integration adapters** – contract interface to the full GenesisAeon stack

---

## Mathematical Foundation

### Gemeinwohl Score

```
G(x) = w_E * Phi(H) + w_A * alpha(m) + w_C * kappa + w_P * pi(p) + w_Ec * e + w_Eq * q
```

Where `Phi(H) = 1 - H` (entropy-order), `alpha(m)` = mean model alignment,
`kappa` = normative consistency, `pi(p) = p/4` = personhood weighting.

**Default weights:** w_E=0.20, w_A=0.25, w_C=0.20, w_P=0.15, w_Ec=0.10, w_Eq=0.10

### Normative Consistency (derived)

```
kappa = 2*(1-H)*alpha / ((1-H) + alpha + eps)
```

### Criticality Classification

| Range | Level |
|-------|-------|
| G >= 0.70 | SAFE (0) |
| 0.50 <= G < 0.70 | WARNING (1) |
| 0.30 <= G < 0.50 | CRITICAL (2) |
| G < 0.30 | EMERGENCY (3) |

### Personhood Minimum Score

```
G_min(p) = 0.40 + 0.12 * p,   p in {0, 1, 2, 3, 4}
```

### Sequential Normative Consistency

```
kappa_seq = 1 - Var({G_t}) / (mean({G_t}) + eps)
```

---

## Installation

```bash
pip install gemeinwohl
pip install "gemeinwohl[full-stack]"   # GenesisAeon stack
pip install "gemeinwohl[dev]"           # Development tools
```

---

## Quick Start

```python
from gemeinwohl import GemeinwohlEngine, KritikalitaetsChecker, PolicyEngine, PersonhoodLevel

engine = GemeinwohlEngine()
score = engine.compute_score(
    entropy=0.35,
    models=["claude-3-opus", "gpt-4"],
    ecological_impact=0.8,
    social_equity=0.7,
)
print(f"Score: {score.value:.4f}  – {score.interpretation}")

checker = KritikalitaetsChecker()
report = checker.assess(score)
print(f"Level: {report.level.name}")

policy = PolicyEngine()
alignment = policy.evaluate_alignment("my-system", score, PersonhoodLevel.DELIBERATIVE)
print(f"Aligned: {alignment.is_aligned}  (gap = {alignment.gap:+.4f})")
```

### CLI

```bash
gemeinwohl assess --entropy 0.3 --models gpt-4 claude-3-opus
gemeinwohl assess --entropy 0.4 --visualize --full --export report.json
gemeinwohl policy infer --entropy 0.5
gemeinwohl policy rules
gemeinwohl kritikalitaet check --entropy 0.6 --export crit.json
```

---

## Personhood Levels

| Level | Name | G_min | Description |
|------:|------|------:|-------------|
| 0 | INSTRUMENTAL | 0.40 | Pure tool; no autonomy or moral standing |
| 1 | REACTIVE | 0.52 | Context-aware responses; limited agency |
| 2 | DELIBERATIVE | 0.64 | Goal-directed reasoning; restricted rights |
| 3 | RELATIONAL | 0.76 | Social role; partial legal personhood |
| 4 | CONSTITUTIVE | 0.88 | Full moral standing; rights and duties |

---

## Architecture

```
src/gemeinwohl/
├── core/
│   ├── gemeinwohl.py        # GemeinwohlEngine, GemeinwohlScore, NormativeMetric
│   └── kritikalitaet.py     # KritikalitaetsChecker, EthicalImplication
├── cli/
│   └── main.py              # Typer CLI
├── governance/
│   └── policy.py            # PersonhoodLevel, PolicyEngine
└── integrations/
    └── adapters.py          # Full-stack adapters
```

---

## Full-Stack Packages

| Package | Min Version |
|---------|------------|
| `unified-mandala` | >= 0.2.0 |
| `worldview` | >= 0.1.0 |
| `aeon-ai` | >= 0.2.0 |
| `genesis-os` | >= 0.2.0 |
| `universums-sim` | >= 0.1.0 |
| `entropy-governance` | >= 0.1.0 |
| `sigillin` | >= 0.1.0 |

---

## References

1. Felber, C. (2010). *Die Gemeinwohl-Oekonomie*. Deuticke.
2. Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379-423.
3. Rawls, J. (1971). *A Theory of Justice*. Harvard University Press.
4. Habermas, J. (1981). *Theorie des kommunikativen Handelns*. Suhrkamp.
5. Floridi, L. et al. (2018). An ethical framework for a good AI society. *Minds and Machines*, 28(4), 689-707.
6. Solum, L. B. (1992). Legal personhood for artificial intelligences. *North Carolina Law Review*, 70(4), 1231-1287.
7. Amodei, D. et al. (2016). Concrete problems in AI safety. *arXiv:1606.06565*.

---

## Links

- **Worldview / CREP**: `docs/CREPPhaseMatrix.yaml` and the `worldview` package
- **GenesisChronik**: `docs/GenesisChronik.md`
- **Docs**: [genesisaeon.github.io/gemeinwohl](https://genesisaeon.github.io/gemeinwohl)
- **Zenodo**: [doi.org/10.5281/zenodo.gemeinwohl](https://doi.org/10.5281/zenodo.gemeinwohl)

---

## License

MIT (c) GenesisAeon
