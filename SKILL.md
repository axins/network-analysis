---
name: multiplex-network-analysis
description: >
  This skill provides a complete framework for multiplex network analysis following
  social network research methodology. It covers data preprocessing (entity name
  normalization, cross-network ID alignment), construction of multilayer/multiplex
  networks, computation of intra-layer metrics, inter-layer overlap (Jaccard), 
  inter-layer degree correlation (Spearman), participation coefficient, multiplex
  clustering, aggregated network dynamics, embedding scores, and academic report
  generation (HTML + MD with publication-formatted tables). The skill should be used
  when the user needs to: (1) analyze multiplex/multilayer/multi-relational networks,
  (2) compute cross-layer overlap, coupling, or embedding metrics, (3) generate 
  academic-style reports with formatted tables and interpretations for multiplex
  networks, (4) perform social network analysis involving multiple relationship types
  among the same set of actors. Triggers include mentions of "multiplex network",
  "multilayer network", "多重网络", "多层网络", "跨层分析", "层间耦合",
  "inter-layer", "cross-layer", or requests to analyze multiple network layers together.
---

# Multiplex Network Analysis

## Overview

This skill enables comprehensive multiplex (multilayer) network analysis as practiced
by social network researchers. It transforms raw multi-relational edge lists into a
unified multiplex network, computes a four-tier metrics system, and produces
publication-ready academic reports with formatted tables and scholarly interpretation.

The framework follows the canonical approach established by Boccaletti et al. (2014,
*Physics Reports*) and Battiston et al. (2014) for multilayer network analysis,
adapted for large-scale organizational network research.

## When to Use This Skill

Trigger this skill when the user's request involves:

- "Analyze multiplex/multilayer/multi-relational networks"
- "Compute cross-layer overlap / layer coupling / inter-layer correlation"
- "Generate academic report for multiple network layers"
- "多重网络分析" / "多层网络" / "跨层分析" / "层间耦合"
- "Compare network layers" with shared node sets
- "Compute participation coefficient" or "multiplex clustering"
- "Generate publication-formatted tables for network analysis"

## Prerequisites

Before using this skill, verify that the following project structure exists:

```
project_root/
├── [data_files].xlsx              # Raw edge lists (source, target, year)
├── multi_network_analysis/
│   ├── src/
│   │   ├── 01_fuzzy_matching.py   # Entity name normalization + ID encoding
│   │   ├── 02_network_metrics.py  # Single-layer network metrics
│   │   ├── 05_multiplex_analysis.py # Core multiplex metrics
│   │   ├── 07b_embedding_metrics.py # Node embedding analysis
│   │   └── 11_multiplex_comprehensive_report.py # Full report generation
│   ├── data/
│   │   └── processed/             # Encoded edge CSVs + company_mapping.csv
│   └── output/
│       ├── tables/                # All metric CSV files
│       └── figures/               # All visualization PNGs
```

## Core Capabilities

### 1. Data Preprocessing — Entity Alignment Across Networks

Align enterprise names across multiple relational datasets through a deterministic
pipeline documented in `references/pipeline.md`. The core steps are:

**Name Normalization (01_fuzzy_matching.py):**
- Full-width → half-width character conversion
- Bracket/parenthesis unification (（）→())
- Whitespace removal, quote removal, case normalization
- Dictionary-based exact matching for ID assignment
- Output: `company_mapping.csv` (name→ID) and `{network}_encoded.csv` (edge lists with int IDs)

**Critical constraint:** All four network layers share the same integer ID space
[1, N] where N is the number of unique enterprise entities. A node with ID=20662
represents the same enterprise across all layers — this is the foundational
requirement for multiplex network construction.

### 2. Single-Layer Network Metrics (02_network_metrics.py)

For each layer and each year, compute:

| Metric | Type | Formula / Notes |
|--------|------|-----------------|
| Nodes, Edges | Count | N^α, M^α |
| Density | Float | 2M^α / [N^α(N^α−1)] |
| Avg Degree | Float | 2M^α / N^α |
| Avg Clustering | Float | Average of local clustering coefficients |
| Components | Int | Number of connected components |
| GCC Ratio | Float | Size of giant component / N^α |
| Assortativity | Float | Degree-degree Pearson correlation |
| Reciprocity | Float | For directed networks only (cpall, hzall) |

**Output:** `metrics_all.csv`

### 3. Multiplex Network Construction

Build a NetworkX `MultiGraph` where each edge carries a `layer` attribute:

```python
def build_multiplex(layers):
    M = nx.MultiGraph()
    for net_name, df in layers.items():
        for s, t in zip(df['source_id'], df['target_id']):
            M.add_edge(s, t, layer=net_name)
    return M
```

**Key insight:** For undirected layers (dsall, gdcpall), edge direction must be
standardized (s = min, t = max) to avoid double-counting in overlap computations.

### 4. Inter-Layer Overlap Analysis (Tier 2 Metrics)

#### 4.1 Node Overlap — Jaccard Coefficient

For each pair of layers (α, β):
```
J_V^{αβ} = |V^α ∩ V^β| / |V^α ∪ V^β|
```

Also compute directional overlap rates:
```
overlap_rate_α = |V^α ∩ V^β| / |V^α|
overlap_rate_β = |V^α ∩ V^β| / |V^β|
```

**Interpretation guidance:**
- **J > 0.5**: Layers share majority of nodes → strong institutional coupling
- **overlap_rate = 1.0**: One layer is complete subset of another → containment relationship (critical finding)
- **J < 0.05**: Layers operate on almost entirely separate populations

#### 4.2 Edge Overlap — Jaccard Coefficient (Time Series)

For each year and layer pair:
```
J_E^{αβ}(t) = |E^α(t) ∩ E^β(t)| / |E^α(t) ∪ E^β(t)|
```

**Interpretation guidance:**
- **J_E < 0.05**: Edges functionally independent — relationships serve different purposes even with node overlap
- **J_E declining over time**: Explosive growth in one layer outpaces overlap (natural consequence of scaling)
- **J_E increasing over time**: Convergence — relationships increasingly coincide

### 5. Inter-Layer Degree Correlation (Tier 3 Metrics)

#### 5.1 Spearman Rank Correlation

For common nodes across layers:
```
ρ^{αβ} = Spearman(k_i^α, k_i^β) for i ∈ V^α ∩ V^β
```

**Interpretation guidance:**
- **ρ > 0.6, p < 0.001**: Strong cross-layer centrality transmission — hub in one layer is hub in another
- **ρ ≈ 0, p > 0.05**: Independent centrality structures — "governance elite ≠ business hub"
- **ρ < 0**: Negative coupling — functional substitution

**Important:** Only compute when common_nodes ≥ 5 to ensure statistical validity.

#### 5.2 Participation Coefficient

For each node:
```
P(i) = [M / (M−1)] × [1 − Σ_α (k_i^α / o_i)²]
```
where `o_i = Σ_α k_i^α` is the overlapping degree.

**Interpretation guidance:**
- **P → 1.0**: Balanced connection distribution across layers
- **P → 0.0**: Connections concentrated in a single dominant layer
- **P = 0.0**: Node present in only one layer (by definition)

**Critical finding pattern:** Even 4-layer-embedded nodes often have P < 0.8,
indicating "broad presence, uneven distribution" — versatility ≠ uniformity.

### 6. Aggregated Multiplex Network Dynamics (Tier 4 Metrics)

Project all layers into a single weighted graph:
```
G_agg = ∪_α G^α   (union of all layer edge sets)
```

Compute for each year:
- Aggregated nodes/edges (how many unique entities/connections exist across all layers)
- Aggregated density, avg degree, clustering coefficient
- GCC ratio (network connectivity)
- Common nodes across all 4 layers (the "versatile actors" count)

### 7. Enterprise Embedding Analysis

#### 7.1 Layer Participation Distribution

For each year, count enterprises by number of layers they participate in (1—4).
This reveals the "multi-embedded elite" proportion.

#### 7.2 Embedding Score

```
S(i) = ℓ_i × (1 + ln(1 + d_i))
```
where ℓ_i = layer count, d_i = total degree across all layers.

**Use for:** Ranking enterprises by combined breadth (layers) and depth (connections).

### 8. Academic Report Generation

#### 8.1 Publication-Formatted Tables

All tables follow academic journal conventions:
- **Top/bottom borders:** 2px solid for table framing
- **Header:** Blue background (#eaf2f8), bold text, 1.5px bottom border
- **Zebra striping:** Alternating row colors
- **Hover highlight:** Light blue on mouseover
- **Number alignment:** Right-aligned for numeric columns, left-aligned for labels
- **Significance notation:** *** p<0.001, ** p<0.01, * p<0.05

#### 8.2 Report Structure

The generated report follows a standard 6-section academic paper format:
1. **Abstract** — Key findings with quantitative highlights
2. **Introduction** — Research questions and theoretical motivation
3. **Theoretical Framework** — Multiplex network definition, supra-adjacency matrix, 4-tier metrics
4. **Data & Methods** — Data sources, encoding alignment, computation pipeline
5. **Results** — 10 tables + figure references, grouped by analysis tier
6. **Discussion & Conclusion** — Theoretical contributions, management implications, limitations

#### 8.3 Interpretation Templates

When writing academic interpretations, follow these patterns:

**Finding announcement:**
> **发现X：[Concise label].** [What was observed] + [Quantitative evidence] + [Theoretical implication].

**Management implication:**
> **战略启示X：[Label].** [Actionable insight] + [Supporting data] + [Practical recommendation].

**Coupling finding:**
> [Layer A]与[Layer B]的[metric]达[value]（[significance]），表明[theoretical mechanism].

### 9. Visualization Reference

Refer to existing figures in `output/figures/` for inclusion in reports:

| Figure | Path | Content |
|--------|------|---------|
| Edge overlap trends | `multiplex/edge_overlap_trends.png` | 6 layer-pair Jaccard time series |
| Degree correlation heatmap | `multiplex/degree_correlation_heatmap.png` | 4×4 Spearman ρ matrix (2020) |
| Aggregated trends | `multiplex/aggregated_trends.png` | 4-panel: nodes, edges, density, clustering |
| Merged network panorama | `merged_unified/panorama.png` | Annual 4-color merged network (2009-2020) |
| Ego networks | `ego_networks/ego_panorama.png` | 5 typical enterprise ego-networks |

## Workflow Decision Tree

When the user requests multiplex network analysis, follow this decision flow:

```
User Request
├── "Analyze multiplex network" / "多重网络分析"
│   └── Run 05_multiplex_analysis.py first (computes core overlap + correlation CSVs)
│       └── Then run 11_multiplex_comprehensive_report.py (generates full report)
│
├── "Compute participation coefficient" / "Calculate embedding scores"
│   └── Run 07b_embedding_metrics.py first
│       └── Then run 11_multiplex_comprehensive_report.py (integrates into report)
│
├── "Generate full academic report with all metrics"
│   └── Run 11_multiplex_comprehensive_report.py directly
│       (reads all existing CSV outputs, computes PC and multiplex clustering, generates HTML+MD)
│
├── "Process raw data" / "Align enterprise names"
│   └── Run 01_fuzzy_matching.py → 02_network_metrics.py → 05_multiplex_analysis.py sequentially
│
└── "Add new metrics" / "Extend analysis"
    └── Read references/methodology.md for formula reference
        └── Add computation to a new src/XX_*.py script
        └── Integrate into report generation
```

## Key Implementation Notes

### Edge Direction Handling

Networks have mixed directionality:
- **Undirected:** dsall (interlocking directorate), gdcpall (common shareholder)
- **Directed:** cpall (lawsuit), hzall (cooperative supply)

When computing edge overlap, use **unordered edge pairs** to compare across
directed/undirected layers:
```python
if net_name in UNDIRECTED:
    if s > t: s, t = t, s
```

### Performance Considerations

For networks with 60K—200K edges and 40K—120K nodes:
- **NetworkX Graph/Digraph** is sufficient for degree and basic metrics
- **Spearman correlation** uses `scipy.stats.spearmanr` — fast even for 10K+ common nodes
- **Jaccard overlap** uses Python `set` operations — O(|E1| + |E2|) per pair
- **Participation coefficient** computation is O(N × M) — vectorized with pandas for 60K+ nodes

### Chinese Font Rendering

For matplotlib figures with Chinese labels:
```python
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

## Resources

### references/methodology.md
Complete reference for all multiplex network metrics, including mathematical
definitions, interpretation guidelines, and expected value ranges. Load this
when detailed formula specifications or interpretation patterns are needed.

### references/pipeline.md
Step-by-step documentation of the data processing pipeline from raw Excel files
to final academic reports. Includes file naming conventions, expected outputs at
each stage, and troubleshooting guidance for common issues.

### scripts/analyze_multiplex.py
Standalone entry-point script that orchestrates the full analysis pipeline.
Can be executed directly or read for understanding the analysis flow.
