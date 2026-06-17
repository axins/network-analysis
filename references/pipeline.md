# Multiplex Network Analysis — Data Processing Pipeline

## Pipeline Overview

The analysis pipeline transforms raw multi-relational edge lists into a complete
multiplex network analysis with academic reports. The pipeline has three stages:

```
RAW DATA (4 .xlsx files)
    │
    ▼
STAGE 1: Preprocessing (01_fuzzy_matching.py)
    │  → Name normalization + ID encoding
    │  → Output: company_mapping.csv, *_encoded.csv
    ▼
STAGE 2: Analysis (02, 05, 07b)
    │  → Single-layer metrics, multiplex overlap,
    │    degree correlation, embedding analysis
    │  → Output: metrics_all.csv, multiplex_*.csv,
    │    enterprise_*.csv
    ▼
STAGE 3: Visualization + Report (03, 06-11)
    │  → Network visualization, merged networks,
    │    academic report generation
    │  → Output: figures/*.png, *.html, *.md
    ▼
FINAL DELIVERABLES
```

---

## Stage 1: Preprocessing (01_fuzzy_matching.py)

### Input
- `cpall.xlsx` — columns: source, target, year
- `dsall.xlsx` — columns: year, source, target (NOTE: different column order!)
- `gdcpall.xlsx` — columns: source, target, year
- `hzall.xlsx` — columns: source, target, year

### Process
1. Read all four Excel files
2. Extract all unique enterprise names
3. Name normalization:
   - Full-width characters → half-width
   - Full-width parentheses （） → half-width ()
   - Remove whitespace and quotation marks
   - Convert to uppercase
4. Deduplicate normalized names → assign unique integer ID (1 to N)
5. Map original edges to encoded edges (source_id, target_id, year)

### Output
Location: `data/processed/`

| File | Description | Size |
|------|-------------|------|
| `company_mapping.csv` | original_name → clean_name → company_id | ~23 MB |
| `clean_to_id.csv` | clean_name → company_id | ~9 MB |
| `cpall_encoded.csv` | source_id, target_id, year | — |
| `dsall_encoded.csv` | source_id, target_id, year | — |
| `gdcpall_encoded.csv` | source_id, target_id, year | — |
| `hzall_encoded.csv` | source_id, target_id, year | — |

### Column Order Warning
**dsall.xlsx** has columns `(year, source, target)` — DIFFERENT from other three
files which have `(source, target, year)`. The loading code must handle this:

```python
if net_name == 'dsall':
    df = df.rename(columns={'year': 'year_col', ...})  # adjust column mapping
```

---

## Stage 2: Analysis Scripts

### 2a. 02_network_metrics.py
**Purpose:** Compute 9 basic metrics for each network × year combination.

**Input:** `*_encoded.csv` files
**Output:** `output/tables/metrics_all.csv`

**Metrics computed:** nodes, edges, density, avg_degree, avg_clustering,
components, gcc_ratio, degree_centralization, assortativity, reciprocity (directed only)

**Runtime:** ~2-3 minutes for 48 network-year combinations

### 2b. 05_multiplex_analysis.py
**Purpose:** Core multiplex analysis — overlap, correlation, aggregation.

**Input:** `*_encoded.csv` files
**Output:** 4 CSV files in `output/tables/`

| CSV | Content |
|-----|---------|
| `multiplex_node_overlap.csv` | Global (all-time) node Jaccard for 6 layer pairs |
| `multiplex_edge_overlap_ts.csv` | Yearly edge Jaccard + edge counts (2009-2020) |
| `multiplex_degree_correlation.csv` | Yearly Spearman ρ for 6 layer pairs |
| `multiplex_aggregated.csv` | Yearly aggregated graph statistics |

**Also generates:** 3 PNG figures in `output/figures/multiplex/`

**Runtime:** ~5-8 minutes (loops over 12 years × 4 networks × 6 layer pairs)

### 2c. 07b_embedding_metrics.py
**Purpose:** Enterprise-level embedding analysis.

**Input:** `*_encoded.csv` files, `company_mapping.csv`
**Output:** 3 CSV files in `output/tables/`

| CSV | Content |
|-----|---------|
| `network_degree_comparison.csv` | Yearly degree statistics for each network |
| `enterprise_layer_distribution.csv` | Distribution of enterprises by layer count |
| `top_multilayer_enterprises.csv` | Top-ranked multi-layer enterprises |

**Also generates:** `enterprise_embedding_analysis.xlsx`

**Runtime:** ~3-5 minutes (processes 12 years)

---

## Stage 3: Visualization + Report

### 3a. 03_network_viz.py
Generates yearly network layout figures for each single network (Top-300 degree nodes).
Output to `output/figures/{cpall,dsall,gdcpall,hzall}/`.

### 3b. 07a/09/09b — Merged Network Visualization
Generates 4-color merged network visualizations (all layers on same canvas).
Output to `output/figures/merged_dynamic/` and `output/figures/merged_unified/`.

### 3c. 07c_ego_networks.py
Generates ego-network visualizations for 5 typical multi-embedded enterprises.
Output to `output/figures/ego_networks/`.

### 3d. 11_multiplex_comprehensive_report.py
**Purpose:** The master report generator that reads ALL prior outputs and
produces the final academic report with publication-formatted tables.

**Input:** All CSV files from `output/tables/`
**Output:**
- `output/multiplex_comprehensive_report.html` — Styled academic HTML report
- `output/multiplex_comprehensive_report.md` — Markdown report
- `output/tables/multiplex_comprehensive_analysis.xlsx` — All tables in Excel
- `output/tables/multiplex_participation_coefficient.csv` — New: PC per node
- `output/tables/multiplex_pc_stats.csv` — New: PC statistics by layer count
- `output/tables/multiplex_clustering_ts.csv` — New: yearly multiplex clustering

**Runtime:** ~3-5 minutes (computes PC + multiplex clustering, builds HTML/MD)

---

## Execution Order

### Full pipeline (from raw data):
```
01_fuzzy_matching.py  →  02_network_metrics.py  →  05_multiplex_analysis.py
→  03_network_viz.py  →  07b_embedding_metrics.py  →  07c_ego_networks.py
→  09_merged_unified_network.py  →  11_multiplex_comprehensive_report.py
```

### Quick update (existing processed data, new report):
```
11_multiplex_comprehensive_report.py   (standalone — reads all existing CSVs)
```

### Add new multiplex metric:
1. Write a new `src/XX_new_metric.py` that outputs to `output/tables/`
2. Update `11_multiplex_comprehensive_report.py` to read the new CSV
3. Add a new table + interpretation section to the report template

---

## Environment Requirements

```
Python >= 3.8
pandas, numpy, networkx >= 3.0
scipy, matplotlib, openpyxl
tqdm (progress bars)
```

### Chinese Font Setup (for matplotlib)
```python
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

If SimHei is not installed on the system, use sans-serif fallback:
```python
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

---

## Troubleshooting

### "No such file: *_encoded.csv"
→ Run `01_fuzzy_matching.py` first to generate encoded data.

### "KeyError: 'year'" when loading dsall
→ dsall.xlsx has different column order. Check column mapping in load function.

### Memory error with large networks (100K+ nodes)
→ Use sampling for clustering computation on full networks:
```python
sampled_nodes = list(G.nodes())[:5000]
G_sub = G.subgraph(sampled_nodes)
cc = nx.average_clustering(G_sub)
```

### F-string syntax error with mathematical notation
→ When using f-strings (f'''...'''), escape literal curly braces by doubling:
```
f"𝒢 = {{*G^α*}}_α=1,…,M"    # {{ and }} → literal { and }
```

### PowerShell CLIXML noise in output
→ Output wrapped in `<Objs>` XML is normal PowerShell behavior.
The actual script output appears between the XML blocks. Ignore the XML wrapper.

### Chinese characters display as boxes in figures
→ Install SimHei font or use DejaVu Sans with English labels.
