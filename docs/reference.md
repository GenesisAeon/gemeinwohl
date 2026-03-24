# API Reference

## gemeinwohl.core.gemeinwohl

### NormativeMetric

Enumeration of the six normative scoring dimensions.

| Member | Value |
|--------|-------|
| `ENTROPY_ORDER` | `"entropy_order"` |
| `MODEL_ALIGNMENT` | `"model_alignment"` |
| `NORMATIVE_CONSISTENCY` | `"normative_consistency"` |
| `PERSONHOOD_WEIGHTING` | `"personhood_weighting"` |
| `ECOLOGICAL_IMPACT` | `"ecological_impact"` |
| `SOCIAL_EQUITY` | `"social_equity"` |

---

### NormativeWeights

Frozen dataclass holding the weight vector for the Gemeinwohl formula.

**Constraint:** All weights non-negative and must sum to 1.0.

**Default values:**

| Field | Default |
|-------|---------|
| `entropy_order` | 0.20 |
| `model_alignment` | 0.25 |
| `normative_consistency` | 0.20 |
| `personhood_weighting` | 0.15 |
| `ecological_impact` | 0.10 |
| `social_equity` | 0.10 |

---

### GemeinwohlScore

Result dataclass for a single Gemeinwohl assessment.

| Attribute | Type | Description |
|-----------|------|-------------|
| `value` | `float` | Aggregate score in [0, 1] |
| `entropy` | `float` | Input entropy |
| `models` | `list[str]` | Evaluated model identifiers |
| `sub_scores` | `dict[NormativeMetric, float]` | Per-dimension scores |
| `interpretation` | `str` | Qualitative label |
| `metadata` | `dict[str, Any]` | Arbitrary context |

**Methods:**
- `to_dict() -> dict` – JSON-serialisable representation

**Interpretation thresholds:**

| Score | Label |
|-------|-------|
| >= 0.85 | Excellent |
| >= 0.70 | Good |
| >= 0.50 | Moderate |
| >= 0.30 | Weak |
| < 0.30 | Critical |

---

### GemeinwohlEngine

Core scoring engine.

**Constructor:**

```python
GemeinwohlEngine(
    weights: NormativeWeights | None = None,
    model_alignment_registry: dict[str, float] | None = None,
)
```

**Methods:**

#### `compute_score`

```python
def compute_score(
    self,
    entropy: float,
    models: list[str] | None = None,
    normative_consistency: float | None = None,
    personhood_level: float = 0.5,
    ecological_impact: float = 0.7,
    social_equity: float = 0.6,
    metadata: dict[str, Any] | None = None,
) -> GemeinwohlScore
```

Computes the aggregate Gemeinwohl Score using the formula:

```
G = w_E*(1-H) + w_A*alpha + w_C*kappa + w_P*pi + w_Ec*e + w_Eq*q
```

**Raises:** `ValueError` if any parameter is outside [0, 1].

#### `register_model`

```python
def register_model(self, model_name: str, alignment_score: float) -> None
```

Add or override a model alignment score. Raises `ValueError` if score not in [0, 1].

#### `get_model_alignment`

```python
def get_model_alignment(self, model_name: str) -> float
```

Returns alignment score for a model. Unknown models return 0.5.

**Built-in alignment registry:**

| Model | Alignment |
|-------|-----------|
| claude-3-opus | 0.88 |
| claude-3-sonnet | 0.85 |
| claude-3-haiku | 0.82 |
| gpt-4o | 0.80 |
| gpt-4 | 0.78 |
| gemini-ultra | 0.79 |
| gemini-pro | 0.75 |
| mistral-large | 0.74 |
| llama-3 | 0.72 |
| unknown | 0.50 |

---

## gemeinwohl.core.kritikalitaet

### KritikalitaetsLevel

Integer enum: `SAFE=0`, `WARNING=1`, `CRITICAL=2`, `EMERGENCY=3`.

**Classification thresholds (default):**

| Level | Score Range |
|-------|------------|
| SAFE | G >= 0.70 |
| WARNING | 0.50 <= G < 0.70 |
| CRITICAL | 0.30 <= G < 0.50 |
| EMERGENCY | G < 0.30 |

---

### EthicalImplication

Frozen dataclass representing a single identified ethical issue.

| Attribute | Type |
|-----------|------|
| `code` | `str` (e.g. `"E001"`) |
| `description` | `str` |
| `severity` | `float` in [0, 1] |
| `dimension` | `str` |
| `remediation` | `str` |

**Built-in implication codes:**

| Code | Trigger | Severity |
|------|---------|---------|
| E001 | entropy > 0.8 | 0.90 |
| E002 | entropy > 0.6 | 0.55 |
| E003 | alignment < 0.5 | 0.80 |
| E004 | alignment < 0.7 | 0.45 |
| E005 | consistency < 0.4 | 0.85 |
| E006 | personhood < 0.3 | 0.75 |
| E007 | ecological < 0.4 | 0.70 |
| E008 | equity < 0.4 | 0.65 |

---

### NormativeConsistencyResult

| Attribute | Type |
|-----------|------|
| `is_consistent` | `bool` |
| `consistency_score` | `float` |
| `variance` | `float` |
| `mean` | `float` |
| `threshold` | `float` |

---

### KritikalitaetsChecker

**Constructor:**

```python
KritikalitaetsChecker(
    theta_safe: float = 0.70,
    theta_warn: float = 0.50,
    theta_crit: float = 0.30,
    consistency_threshold: float = 0.70,
)
```

**Methods:**

- `classify(score) -> KritikalitaetsLevel`
- `identify_implications(score) -> list[EthicalImplication]`
- `check_sequence_consistency(scores) -> NormativeConsistencyResult` (requires >= 2 scores)
- `assess(score) -> KritikalitaetsReport`

---

## gemeinwohl.governance.policy

### PersonhoodLevel

Integer enum with five levels (0–4). Each level has:

- `.min_gemeinwohl_score` – minimum G required: `0.40 + 0.12*p`
- `.weighting_factor` – `p / 4.0`
- `.description` – human-readable label

---

### PolicyEngine

**Constructor:**

```python
PolicyEngine(
    default_personhood: PersonhoodLevel = PersonhoodLevel.INSTRUMENTAL,
    custom_rules: list[PolicyRule] | None = None,
)
```

**Methods:**

- `evaluate_alignment(system_id, score, target_level) -> GemeinwohlAlignment`
- `infer_max_personhood(score) -> PersonhoodLevel`
- `apply_rules(score) -> dict[str, bool]`
- `add_rule(rule) -> None`

**Built-in rules:**

| Rule | Min Score | Description |
|------|-----------|-------------|
| P001 | 0.40 | Baseline operational requirement |
| P002 | 0.64 | Deliberative autonomy threshold |
| P003 | 0.76 | Relational personhood threshold |
| P004 | 0.88 | Constitutive personhood threshold |

---

## gemeinwohl.integrations.adapters

### BasePackageAdapter

```python
BasePackageAdapter(import_name: str, package_name: str, min_version: str = "0.0.0")
```

- `ping() -> IntegrationResult` – always returns without raising

### Concrete Adapters

`UnifiedMandalAdapter`, `WorldviewAdapter`, `AeonAIAdapter`, `GenesisOSAdapter`,
`UniversumsSimAdapter`, `EntropyGovernanceAdapter`, `SigillinAdapter`

### `ping_all() -> dict[str, IntegrationResult]`

Pings all seven registered adapters.

---

## CLI Reference

```
gemeinwohl [OPTIONS] COMMAND [ARGS]...

Options:
  --version  -V    Show version and exit.

Commands:
  assess           Compute Gemeinwohl Score
  policy           Policy and personhood commands
  kritikalitaet    Criticality checking commands
```

### `gemeinwohl assess`

```
Options:
  --entropy     -e  FLOAT   System entropy [0,1] (required)
  --models      -m  TEXT    Model identifiers (repeatable)
  --personhood  -p  INT     Personhood level 0-4 (default: 0)
  --ecological      FLOAT   Ecological score (default: 0.7)
  --equity          FLOAT   Social equity score (default: 0.6)
  --visualize   -v          Rich table output
  --full                    Include implications & recommendations
  --export          PATH    Export JSON to file
```

Exit codes: `0` = OK, `2` = EMERGENCY level.

### `gemeinwohl policy infer`

Infers the highest achievable personhood level.

### `gemeinwohl policy rules`

Lists all active governance rules.

### `gemeinwohl kritikalitaet check`

Full criticality report. Accepts same options as `assess`. Supports `--export`.

---

## Worldview / CREP Integration

`gemeinwohl` is designed to operate as the normative layer within the Contextual Reality
Evaluation Protocol (CREP) defined in `docs/CREPPhaseMatrix.yaml`.

The Gemeinwohl Score **G** can serve as the normative gate in CREP Phase evaluations:
a system must achieve `G >= G_min(p)` before being authorised to operate at personhood
level `p`. This integrates directly with the `worldview` package's context evaluation
pipeline when the `[full-stack]` extra is installed.

See `docs/GenesisChronik.md` for the full architectural lineage and integration map.
