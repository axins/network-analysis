# Multiplex Network Analysis — Methodology Reference

## 1. Mathematical Foundation

### 1.1 Multiplex Network Definition

A multiplex network with M layers is defined as:

**M** = {G^α}^M_{α=1}

where each layer G^α = (V^α, E^α), and V^α = V (all layers share the same node set).
Inter-layer edges connect copies of the same physical node across layers:
E^{αβ} = {(v_i^α, v_i^β) : v_i ∈ V}.

### 1.2 Supra-Adjacency Matrix

The MN × MN block matrix that is the foundation for all multiplex spectral analysis:

```
A = [ A^1    ωI   ...   ωI  ]
    [ ωI    A^2   ...   ωI  ]
    [ ...   ...   ...   ... ]
    [ ωI    ωI    ...   A^M ]
```

where A^α is the adjacency matrix of layer α, ω is the inter-layer coupling
strength (default ω=1), and I is the N × N identity matrix.

---

## 2. Tier 1: Intra-Layer Metrics

### 2.1 Basic Counts

| Metric | Formula | Notes |
|--------|---------|-------|
| Nodes | N^α | Unique enterprise IDs in layer α |
| Edges | M^α | Unique (source, target) pairs in layer α |

### 2.2 Density

```
D^α = 2M^α / [N^α(N^α − 1)]
```

**Interpretation:** Proportion of possible edges actually present.
- D > 0.01: Unusually dense for large networks (>5K nodes)
- D < 0.0001: Typical for large-scale organizational networks
- D declining over time despite edge growth: Normal — node growth outpaces edge growth

### 2.3 Average Degree

```
⟨k^α⟩ = 2M^α / N^α
```

**Key insight:** For large networks, density and average degree are linked:
⟨k⟩ ≈ D × N. A network with 10K nodes and density 0.001 has average degree ≈ 10.

### 2.4 Average Clustering Coefficient

Local clustering for node i:
```
C_i = (number of triangles including i) / [k_i(k_i − 1) / 2]
```

Network average: C^α = (1/N^α) Σ_i C_i

**Interpretation:**
- C > 0.1: Strong local triadic closure — "friend of friend is friend"
- C ≈ 0: Star-like or tree-like structure, no triadic closure
- C stable over time: Network has reached structural equilibrium

### 2.5 Giant Connected Component (GCC) Ratio

```
GCC^α = |largest_component| / N^α
```

**Interpretation:**
- GCC → 1.0: Network is largely connected — most nodes reachable
- GCC < 0.3: Network fragmented into many small isolated communities
- GCC increasing: Integration process — previously isolated clusters merging

### 2.6 Assortativity (Degree-Degree Correlation)

```
r^α = Pearson(k_i, k_j) for all edges (i, j)
```

**Interpretation:**
- **r > 0 (positive assortativity):** High-degree nodes connect to high-degree nodes
  → Elite club structure (typical for director networks)
- **r < 0 (negative assortativity):** High-degree nodes connect to low-degree nodes
  → Hub-and-spoke, core-periphery structure (typical for lawsuit networks)
- **r ≈ 0:** No degree preference in connection

### 2.7 Reciprocity (Directed Networks Only)

```
R^α = |{(i,j) ∈ E^α : (j,i) ∈ E^α}| / |E^α|
```

**Interpretation:** Proportion of edges that are mutual. High reciprocity means
bi-directional relationships dominate (e.g., mutual cooperation); low reciprocity
means asymmetric relations (e.g., plaintiff→defendant direction).

---

## 3. Tier 2: Inter-Layer Overlap Metrics

### 3.1 Node Jaccard Overlap

```
J_V^{αβ} = |V^α ∩ V^β| / |V^α ∪ V^β|
```

**Directional overlap rates:**
```
OR_α^{αβ} = |V^α ∩ V^β| / |V^α|
OR_β^{αβ} = |V^α ∩ V^β| / |V^β|
```

**Interpretation table:**

| Jaccard Range | Meaning |
|:---:|---|
| > 0.5 | Strong institutional coupling — same enterprises dominate both layers |
| 0.1–0.5 | Moderate overlap — partial population sharing |
| < 0.1 | Near-independent populations |
| OR = 1.0 | Complete containment — one layer is subset of the other (CRITICAL finding) |

### 3.2 Edge Jaccard Overlap (Time-Series)

```
J_E^{αβ}(t) = |E^α(t) ∩ E^β(t)| / |E^α(t) ∪ E^β(t)|  for each year t
```

**Interpretation table:**

| Jaccard Range | Meaning |
|:---:|---|
| > 0.3 | High edge convergence — same enterprise pairs connected in both layers |
| 0.05–0.3 | Moderate overlap — some redundant connections |
| < 0.05 | Functional independence — relationships serve completely different purposes |
| ≈ 0 | Complete independence — layers connect completely different pairs |

**Time-series patterns:**

| Pattern | Interpretation |
|--------|---------------|
| J_E declining | Both layers growing but connecting DIFFERENT pairs → functional differentiation |
| J_E stable | Growth rate proportional → structural scaling |
| J_E increasing | Layers converging to connect same pairs → functional convergence |

**Critical finding:** Low edge overlap (< 0.05) combined with high node overlap (> 0.5)
indicates that the SAME enterprises interact through DIFFERENT relationship types with
DIFFERENT partners — a core multiplex pattern.

---

## 4. Tier 3: Inter-Layer Coupling Metrics

### 4.1 Spearman Inter-Layer Degree Correlation

```
ρ^{αβ} = Spearman( {k_i^α} , {k_i^β} )  for i ∈ V^α ∩ V^β
```

where k_i^α is the degree of node i in layer α.

**Prerequisites:**
- Common nodes ≥ 5 (otherwise correlation is unreliable)
- Report both ρ and p-value
- Use *** (p<0.001), ** (p<0.01), * (p<0.05) notation

**Interpretation table:**

| ρ Range | p-value | Meaning |
|:---:|:---:|---|
| > 0.6 | < 0.001 | Strong cross-layer centrality transmission |
| 0.15–0.6 | < 0.05 | Moderate coupling — partial centrality overlap |
| ≈ 0 | > 0.05 | Independent centrality structures |
| < 0 | any | Functional substitution / negative coupling |

**Time-series of ρ:** If ρ is stable over 12 years, the coupling is
STRUCTURAL and institutionalized, not temporary.

### 4.2 Participation Coefficient

```
P(i) = [M / (M − 1)] × [ 1 − Σ_{α=1}^{M} (k_i^α / o_i)² ]
```

where M is the number of layers where node i is present, and
o_i = Σ_{α=1}^{M} k_i^α is the overlapping degree.

**Properties:**
- P(i) ∈ [0, 1]
- P(i) = 0 when node appears in only ONE layer (by definition)
- P(i) → 1 when degrees are evenly distributed across all present layers
- P(i) is MAXIMIZED when k_i^α = o_i / M for all α

**Interpretation by layer count:**

| Layer Count | Expected PC Range | Typical Interpretation |
|:---:|:---:|---|
| 2 | 0.85–1.00 | Binary embedding, participation usually balanced or one-dominated |
| 3 | 0.70–0.95 | "Specialized generalist" — moderate balance across 3 layers |
| 4 | 0.65–0.85 | Versatile actor, but with dominant layers |

**Counterintuitive finding:** 4-layer enterprises often have LOWER mean PC than 3-layer
enterprises because their connections concentrate in 1–2 dominant layers despite
presence in all 4. Versatility of breadth ≠ uniformity of distribution.

### 4.3 Multiplex Degree Centrality

```
k_i^{multi} = Σ_{α=1}^{M} k_i^α
```

or weighted version:
```
k_i^{multi} = Σ_{α=1}^{M} w_α · k_i^α
```

where w_α can be 1 (unweighted) or normalized by layer size (weighted).

### 4.4 Multiplex Clustering Coefficient

Simplified computation for large networks:
1. Build aggregated graph G_agg = ∪_α G^α
2. Compute average_clustering(G_agg)
3. This captures triangles formed by any combination of layer edges

For full multiplex clustering (Battiston et al., 2014), consider:
```
C_M(i) = (triangles with edges in ≥2 layers for node i) / (connected triples for node i)
```

---

## 5. Tier 4: Aggregated Network Dynamics

### 5.1 Aggregated Graph Construction

```
G_agg(t) = ∪_{α=1}^{M} G^α(t)    for each year t
```

The aggregated graph includes edge (i, j) if it exists in AT LEAST ONE layer.

### 5.2 Evolution Metrics

For each year t:

| Metric | Meaning |
|--------|---------|
| aggregated_nodes | Unique enterprises active in ANY layer |
| aggregated_edges | Unique (i,j) pairs connected in ANY layer |
| aggregated_density | Global connection probability |
| aggregated_avg_degree | Average connections per enterprise |
| aggregated_clustering | Average triadic closure |
| aggregated_components | Number of disconnected clusters |
| aggregated_gcc_ratio | Giant component coverage |

### 5.3 Growth Ratio Analysis

```
Node_growth_ratio = N(t_end) / N(t_start)
Edge_growth_ratio = M(t_end) / M(t_start)
```

**Interpretation:**
- Edge_ratio >> Node_ratio: Network densification — more connections per node
- Edge_ratio ≈ Node_ratio: Proportional scaling
- Edge_ratio < Node_ratio: Network dilution — new nodes don't connect enough

---

## 6. Enterprise Embedding Metrics

### 6.1 Layer Participation Count

```
ℓ_i = Σ_{α=1}^{M} 𝟙(k_i^α > 0)
```

where 𝟙 is the indicator function.

### 6.2 Embedding Score

```
S(i) = ℓ_i × (1 + ln(1 + d_i))
```

where d_i = Σ_{α} k_i^α is the total degree.

**Purpose:** Combined ranking that rewards both breadth (layers) and depth (connections).
Log-transformed total degree prevents excessive dominance by degree outliers.

**Score interpretation:**
- S < 5: Single-layer, low-degree participant
- S 5–15: Moderate embedding — 2 layers or single-layer high-degree
- S 15–25: Deep embedding — 3+ layers with substantial connections
- S > 25: Versatile hub — 4 layers with massive connection volume

---

## 7. Statistical Testing Guidelines

### 7.1 Correlation Testing

- Use **Spearman** (not Pearson) for degree correlation — degree distributions are
  heavy-tailed and violate normality assumptions
- Report exact p-values, not just significance stars
- When common_nodes < 30, interpret correlations with caution

### 7.2 Distribution Comparison

- Use **Kolmogorov-Smirnov** test for comparing degree distributions between layers
- Use **Kruskal-Wallis** for comparing PC across layer-count groups (non-normal distribution)

---

## 8. Interpretation Cheat Sheet

### Finding→Implication Mapping

| Observational Finding | Theoretical Implication | Management/Practice Implication |
|----------------------|------------------------|-------------------------------|
| Low edge Jaccard (< 0.05) | Functional differentiation of relationship types | Build each network layer separately |
| High node Jaccard (> 0.5) | Institutional coupling across relationship domains | Systemic risk: shock in one layer cascades |
| Positive degree correlation (ρ > 0.5) | Centrality cross-layer transmission | Hub identification across multiple dimensions |
| Non-significant degree correlation | Independent centrality structures | Different strategies needed per layer |
| Low 4-layer participation (< 1%) | Multiplex embedding is scarce strategic resource | Competitive advantage for multi-embedded firms |
| GCC ratio increasing | Network integration process | Decreasing structural holes; increasing diffusion risk |
| Positive assortativity | Elite club formation | Concentrated power; entry barriers |
| Negative assortativity | Core-periphery asymmetry | Large→small dependency structure |
