# Network Analysis Toolkit

AI skills, code, and data for social network analysis, including ERGM, SAOM, Multiplex, and Multilayer network methodologies.

## Skills

### `multiplex-network-analysis`

A comprehensive framework for multiplex (multilayer) network analysis following social network research methodology.

**Capabilities:**
- Data preprocessing: enterprise name normalization and cross-network ID alignment
- Construction of multilayer/multiplex networks from multi-relational edge lists
- Intra-layer metrics: density, clustering, assortativity, GCC ratio
- Inter-layer overlap: node Jaccard, edge Jaccard (time series)
- Inter-layer coupling: Spearman degree correlation, participation coefficient
- Multiplex clustering coefficient, aggregated network dynamics
- Enterprise embedding scores and layer participation distribution
- Academic report generation (HTML + MD) with publication-formatted tables

**Triggers:** "multiplex network", "multilayer network", "多重网络", "多层网络", "跨层分析", "层间耦合", "inter-layer", "cross-layer"

**Structure:**
```
multiplex-network-analysis/
├── SKILL.md                    # Main instruction file with decision tree
├── scripts/
│   └── analyze_multiplex.py    # Pipeline orchestrator
├── references/
│   ├── methodology.md          # Complete metric formulas and interpretation guides
│   └── pipeline.md             # Data processing pipeline documentation
└── assets/                     # Asset directory (templates, etc.)
```

**Installation:** Copy to `~/.codebuddy/skills/multiplex-network-analysis/` (user scope) or `.codebuddy/skills/multiplex-network-analysis/` (project scope).

## License

MIT
