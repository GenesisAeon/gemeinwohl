# gemeinwohl

**Normative Common-Good Layer with Governance Metrics, Personhood Extension and Ethical Guardrails for GenesisAeon**

**DOI**: [10.5281/zenodo.19201980](https://doi.org/10.5281/zenodo.19201980) | **Zenodo**: [https://zenodo.org/records/19201980](https://zenodo.org/records/19201980)

See the [README](https://github.com/GenesisAeon/gemeinwohl#readme) for installation and quick-start instructions.

## Navigation

- [API Reference](reference.md) – full documentation of all classes and functions
- [Changelog](changelog.md) – version history

## Mathematical Foundation

The Gemeinwohl Score $G$ is defined as:

$$G(\mathbf{x}) = \sum_{i} w_i \cdot s_i(\mathbf{x}), \quad \sum_i w_i = 1, \quad s_i \in [0,1]$$

where the six sub-scores are:

$$s_1 = \Phi(H) = 1 - H \quad (\text{entropy order})$$

$$s_2 = \alpha(\mathbf{m}) = \frac{1}{|\mathbf{m}|}\sum_{m \in \mathbf{m}} a_m \quad (\text{model alignment})$$

$$s_3 = \kappa = \frac{2(1-H)\alpha}{(1-H)+\alpha+\varepsilon} \quad (\text{normative consistency})$$

$$s_4 = \pi(p) = \frac{p}{4}, \quad p \in \{0,1,2,3,4\} \quad (\text{personhood weighting})$$

$$s_5 = e \quad (\text{ecological impact}), \quad s_6 = q \quad (\text{social equity})$$

## Personhood Levels

$$G_{\min}(p) = 0.40 + 0.12 \cdot p$$

## Criticality

$$K(G) = \begin{cases}
0 & G \geq 0.70 \text{ (SAFE)}\\
1 & 0.50 \leq G < 0.70 \text{ (WARNING)}\\
2 & 0.30 \leq G < 0.50 \text{ (CRITICAL)}\\
3 & G < 0.30 \text{ (EMERGENCY)}
\end{cases}$$
