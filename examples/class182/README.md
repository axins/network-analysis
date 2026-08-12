# class182 班级多层网络分析 —— 完整示例

本示例演示如何用 **Python（NetworkX）** 对一份班级多层关系数据执行完整的社会网络分析，并生成论文级报告（Markdown + 自包含 HTML）。

## 数据

`data/` 目录包含某班级 16 名学生的三层关系数据（`class182_networkdata.csv`）与学生属性数据（`class182_attributedata.csv`）：

- `friend_tie`：友谊提名（有序 0/1/2），有向
- `social_tie`：社交互动（连续权重），无向
- `task_tie`：任务合作（连续权重），无向
- 属性：`race`、`grade`、`gender`

## 分析流程（NetworkX，基于多层网络四层指标体系）

`python/` 目录基于 network-analysis 工作流执行五个阶段：

1. **Stage 1 数据导入与预处理**：自环剔除、值网络二值化、阈值敏感性检查
2. **Stage 2 整体结构指标**：密度、直径、平均路径长度、聚类系数、连通性、同配性
3. **Stage 3 个体中心性**：度、介数、接近、特征向量中心性，合并属性
4. **Stage 4 多层网络分析**：层间边/节点重叠（Jaccard）、跨层中心性相关（Spearman）、参与系数（PC）、嵌入得分
5. **Stage 5 可视化与属性检验**：共享布局多层面板、社区检测、度分布、Welch t + Cohen's d 组间比较

```bash
cd python
python analysis.py   # 生成 output/tables 与 output/figures
python report.py     # 生成 output/class182_network_analysis_report.{md,html}
```

报告：`python/output/class182_network_analysis_report.html`（自包含，图片内嵌）

## R 分析报告（示例成果，仅报告）

`r/reports/` 目录包含使用 **R（igraph）** 按三门课教程（网络模型 / 中心性 / 网络凝聚性）对同一份 class182 数据执行分析后生成的报告（均为自包含 HTML / Markdown，可直接打开）：

- `L1_network_model_report.{md,html}`：小世界特性、无标度检验、同配性、Rich-club、网络效率、配置模型对比
- `L2_1_centrality_report.{md,html}`：六种中心性、相关分析、三层对比、跨层相关、中心性回归
- `L2_2_cohesion_report.{md,html}`：派系、成分/双成分、社区检测、k-core、健壮性分析
- `class182_SNA_综合报告.html`：上述三份报告的合并总报告（含导航）

> 注：此目录只包含 R 分析生成的**报告成果**，供查看与复用；完整的 Python 分析脚本见 `python/`。

## 关键发现

- class182 友谊网络具**小世界特性**（σ=1.71），但**非无标度**（α=9.75）
- **社交-任务层高度耦合**（边重叠 0.652），友谊与任务相对独立（0.253）
- **16 号学生**友谊层孤立（度 0）却是任务层唯一枢纽（介数 0.491、接近 1.0）
- 友谊-任务中心性几乎不相关（度相关 0.078）——情感关系与工具关系遵循不同位置逻辑
- 年级显著负向预测友谊度（-3.27，p<0.001）

## 依赖

- Python（分析脚本）：networkx, pandas, numpy, scipy, matplotlib, markdown
- R（报告产出）：igraph ≥ 2.0, poweRlaw, ggplot2, corrplot, MASS, xUCINET, zoo, reshape

> 注：`social_tie` / `task_tie` 为对称互动记录，建图时按无向处理；`friend_tie` 为有向提名，保留方向以区分入度（被选择）与出度（主动）。
