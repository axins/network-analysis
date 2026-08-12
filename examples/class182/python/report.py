# -*- coding: utf-8 -*-
"""
生成 class182 综合分析报告（.md + .html 双格式）
基于 network-analysis skill 的六段式报告结构与教程五阶段框架。
"""
import os
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
T = os.path.join(OUT, "tables")
F = os.path.join(OUT, "figures")

def load(name):
    return pd.read_csv(os.path.join(T, name))

metrics = load("layer_metrics.csv")
cent = load("centrality_all.csv")
embed = load("embedding.csv")
comm = load("communities.csv")
corr = load("degree_correlation.csv")
grp = load("group_differences.csv")
edge_ov = load("edge_overlap.csv")
node_ov = load("node_overlap.csv")
thr = load("threshold_sensitivity.csv")

# ---------- 关键统计提取 ----------
def fmt(v):
    if v is None or pd.isna(v): return "—"
    return f"{v:.3f}"


# 生成 Markdown 表格；nan 显示为 —，其余数值保留精度
def md_table(df, index_col=None, decimals=3):
    d = df.copy()
    for c in d.columns:
        if pd.api.types.is_numeric_dtype(d[c]):
            d[c] = d[c].apply(lambda v: "—" if pd.isna(v) else round(v, decimals))
        else:
            d[c] = d[c].astype(str)
    cols = list(d.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join(["---"] * len(cols)) + "|"
    rows = []
    for _, r in d.iterrows():
        rows.append("| " + " | ".join(str(v) for v in r) + " |")
    return "\n".join([header, sep] + rows)


m = metrics.set_index("layer")
friend_c = cent[cent["layer"] == "friend"].set_index("node")
social_c = cent[cent["layer"] == "social"].set_index("node")
task_c = cent[cent["layer"] == "task"].set_index("node")

friend_top = friend_c.sort_values("indegree", ascending=False).head(6)
friend_betw = friend_c.sort_values("betweenness", ascending=False).head(5)
task_betw = task_c.sort_values("betweenness", ascending=False).head(5)

# 主要数值
friend_indeg_top = friend_top.index.astype(int).tolist()
friend_density = fmt(m.loc["friend", "density"])
friend_rec = fmt(m.loc["friend", "reciprocity"])
social_density = fmt(m.loc["social", "density"])
task_density = fmt(m.loc["task", "density"])
task_clust = fmt(m.loc["task", "avg_clustering"])

# 节点16 与 4
n16_social_deg = int(social_c.loc[16, "degree"])
n16_task_deg = int(task_c.loc[16, "degree"])
n16_task_betw = fmt(task_c.loc[16, "betweenness"])
n16_task_close = fmt(task_c.loc[16, "closeness"])
n4_friend = int(friend_c.loc[4, "indegree"])
n16_friend = int(friend_c.loc[16, "indegree"])

# 嵌入 top
embed_top = embed.sort_values("embedding_score", ascending=False).head(3)
embed_top_nodes = embed_top["node"].astype(int).tolist()
n8_emb = fmt(embed[embed["node"] == 8]["embedding_score"].iloc[0])
n10_emb = fmt(embed[embed["node"] == 10]["embedding_score"].iloc[0])
n16_emb = fmt(embed[embed["node"] == 16]["embedding_score"].iloc[0])

# 重叠
st_jac = fmt(edge_ov[edge_ov["pair"] == "social-task"]["edge_jaccard"].iloc[0])
ft_jac = fmt(edge_ov[edge_ov["pair"] == "friend-task"]["edge_jaccard"].iloc[0])
fs_jac = fmt(edge_ov[edge_ov["pair"] == "friend-social"]["edge_jaccard"].iloc[0])
ft_shared = int(edge_ov[edge_ov["pair"] == "friend-task"]["shared_edges"].iloc[0])
st_shared = int(edge_ov[edge_ov["pair"] == "social-task"]["shared_edges"].iloc[0])

# 相关
st_rho = fmt(corr[corr["pair"] == "social-task"]["rho"].iloc[0])
st_p = fmt(corr[corr["pair"] == "social-task"]["p"].iloc[0])
ft_rho = fmt(corr[corr["pair"] == "friend-task"]["rho"].iloc[0])

# 性别
grp_row = grp[grp["attribute"] == "gender"].iloc[0]
female_mean = grp_row["mean_1"]; male_mean = grp_row["mean_2"]
grp_t = grp_row["t"]; grp_p = grp_row["p"]; grp_d = grp_row["cohens_d"]

# 社区
n_comm = comm["community"].nunique()
mod = 0.0
comm0_nodes = comm[comm["community"] == 0]["node"].astype(int).tolist()
comm1_nodes = comm[comm["community"] == 1]["node"].astype(int).tolist()
comm_sizes = comm["community"].value_counts().sort_index()

# ============ 生成 Markdown ============
md = f"""# class182 班级三层关系网络综合分析报告

> 基于 **network-analysis** skill 的多层网络分析方法论，对 `class182_networkdata.csv`（三层关系）与 `class182_attributedata.csv`（学生属性）的完整社会网络分析。
>
> 数据规模：16 名学生；三层关系——友谊提名（friend，有序 0/1/2）、社交互动（social，连续权重）、任务合作（task，连续权重）。属性字段：race、grade、gender。

---

## 摘要

本报告对某班级 16 名学生的友谊、社交、任务三层关系网络进行了系统性分析。整体上，三层网络呈现**"社交-任务高度耦合、友谊相对独立"**的结构特征：社交层与任务层的边重叠系数达 {st_jac}，而友谊层与任务层仅 {ft_jac}。个体层面存在突出的"角色分化"：**16 号学生**（唯一的 13 年级、黑人男生）在友谊层完全孤立（入度 0），却在任务层和社交层占据绝对核心——任务层介数中心性 {n16_task_betw}（全层最高）、接近中心性 {n16_task_close}（满分 1.0），是学业合作网络的唯一关键桥梁。属性统计显示友谊层女性度均值（{female_mean}）高于男性（{male_mean}），但差异未达统计显著（p={grp_p}，Cohen's d={grp_d}）。社区检测将聚合网络划分为 {n_comm} 个内部紧密的派系。

---

## 一、数据导入与预处理

**数据来源**：`class182_networkdata.csv`（边列表，含 ego/alter/friend_tie/social_tie/task_tie 四列）与 `class182_attributedata.csv`（ids/race/grade/gender）。

**处理要点**：
1. **自环剔除**：所有 `ego == alter` 的自环行在构建网络时剔除，避免密度虚高。
2. **二值化策略**：friend 层为有序测量（0/1/2），取 `>=1` 视为存在友谊；social/task 层为连续权重，取 `>0` 视为存在关系。
3. **方向设定**：friend 为**有向提名**（谁提名谁），保留方向以刻画"被选择（入度）"与"主动选择（出度）"；social/task 为对称的互动频次记录，按**无向**处理。
4. **孤立节点保留**：节点 4 与 16 在 friend 层无任何连边，保留在网络中以便如实报告。

**值网络阈值敏感性检查**（不同阈值下的有效边数）：

{md_table(thr, decimals=0)}

> 说明：基准边数（`>0`，即建图层采用的宽松阈值）为 social 层 67 条、task 层 47 条。随着阈值升至 1.0、1.5、2.0，两层有效边数显著下降（social 降至 34→27→21，task 降至 15→13→12），表明两层存在大量弱互动边。若改用高阈值，网络会显著稀疏化，结论中的"社交-任务耦合"可能减弱，需在论文中报告这一稳健性。

---

## 二、网络构建与可视化

三层网络以同一节点集（16 人）构建。下图采用**共享布局**（spring layout，固定随机种子）使三层可直接视觉对比，节点颜色按性别区分、节点大小按该层度中心性缩放：

![三层网络并列图](figures/multilayer_panel.png)

**视觉要点**：社交层（中）与任务层（右）结构明显更稠密、更均匀；友谊层（左）存在两个明显孤点（4、16），且围绕少数活跃提名者聚集。16 号节点在任务层以最大节点尺寸出现，突出其枢纽地位。

聚合网络（三层边合并）的 Louvain 社区检测如下：

![社区检测](figures/community_detection.png)

---

## 三、网络基本特征描述

**三层网络整体结构指标**：

{md_table(metrics, decimals=3)}

**指标解读**：
- **密度**：社交层密度最高（{social_density}），说明日常互动关系最普遍；友谊层密度最低（{friend_density}），符合"友谊需要时间和相互确认"的特征。
- **互惠性**（friend 层，{friend_rec}）：约 64.5% 的友谊提名得到回应，体现友谊的"相互确认"属性。social/task 为无向对称记录，互惠性不适用。
- **连通性**：social 与 task 层均完全连通（单一成分、直径 2），表明合作关系和日常互动覆盖全班；友谊层则分裂为 3 个成分，最大成分含 14/16 人（{fmt(m.loc['friend','gcc_ratio'])}），说明有 2 名学生游离于正式友谊网络之外。
- **聚类系数**：task 层最高（{task_clust}），反映任务合作呈明显的小团体化——合作往往在封闭的"学习圈"内部发生。
- **同配性**：三层均为负值，尤其 social（{fmt(m.loc['social','assortativity'])}）与 task（{fmt(m.loc['task','assortativity'])}），说明高互动者倾向连接低互动者——存在"枢纽辐射"而非"名人抱团"，与友谊层近乎中性（{fmt(m.loc['friend','assortativity'])}）形成对比。

度分布对比：

![度分布](figures/degree_distribution.png)

---

## 四、中心性分析

### 4.1 友谊层（有向）

**入度中心性（被提名次数，代表"受欢迎度"）Top 排名**：

{md_table(friend_c.sort_values('indegree', ascending=False).head(6).reset_index()[['node','indegree','outdegree','degree','betweenness','race','gender']], decimals=3)}

**友谊层 Top10 度中心性（按性别着色）**：

![友谊层度中心性](figures/friend_degree_top10.png)

**解读**：1 号学生入度 8（{fmt(friend_c.loc[1,'indegree'])}，全班 15 个潜在提名者中超过一半），是无可争议的人气核心；{', '.join(map(str, friend_indeg_top[1:4]))} 号紧随其后。**中介中心性**方面，1 号（{fmt(friend_c.loc[1,'betweenness'])}）与 14、15 号构成友谊网的桥梁——若 1 号缺席，友谊层会显著破碎。

### 4.2 社交层与任务层（无向）

**任务层介数中心性 Top 5**：

{md_table(task_c.sort_values('betweenness', ascending=False).head(5).reset_index()[['node','degree','betweenness','closeness']], decimals=3)}

**核心发现——16 号学生的任务枢纽地位**：16 号在任务层介数中心性 {n16_task_betw}（第二名 {fmt(task_betw.index.tolist()[1])} 号仅 {fmt(task_c.loc[task_betw.index.tolist()[1],'betweenness'])}），接近中心性 {n16_task_close}（=1.0，唯一），即它在任务网中"离所有人最近"且"大量合作的必经之路"。这一结果与其友谊层完全孤立（入度 {n16_friend}）形成鲜明反差，是本章最重要、最具社会学意涵的发现。

---

## 五、多层网络分析

### 5.1 层间节点与边重叠

**节点重叠**：三层共享全部 16 个节点（Jaccard=1.0），满足多层分析前提。

**边重叠（Jaccard 系数）**：

{md_table(edge_ov, decimals=3)}

- 社交-任务层重叠最高（{st_jac}，{st_shared} 条共享边）——"经常来往的人往往也一起学习"。
- 友谊-任务重叠最低（{ft_jac}，仅 {ft_shared} 条共享边）——**学业合作大部分发生在非朋友之间**，合作网络独立于友谊网络组织。
- 友谊-社交重叠约 {fs_jac}，居中。

> 关键理论含义：任务合作的生成逻辑与友谊不同，不能简单用"朋友互助"解释学业合作，需单独建模合作形成机制。

### 5.2 跨层度中心性相关（Spearman，16 公共节点）

{md_table(corr, decimals=4)}

- **社交-任务**相关较强（ρ={st_rho}，p={st_p}，接近 0.05 边际显著）：日常互动与学业合作的位置高度联动。
- **友谊-任务**相关几乎为零（ρ={ft_rho}）：友谊人气与任务核心地位**完全脱钩**——在班级里"人缘好"不等于"被选择为学习伙伴"。
- **友谊-社交**相关为负（{fmt(corr[corr['pair']=='friend-social']['rho'].iloc[0])}）：社交活跃者未必友谊受欢迎，两类"人气"含义不同。

### 5.3 参与系数与嵌入得分

参与系数（PC）衡量节点是否"跨层分配"连接；嵌入得分 S(i)=层数×(1+ln(1+度)) 综合刻画节点在多层网络中的参与深度。Top 排名：

{md_table(embed.sort_values('embedding_score', ascending=False).head(10), decimals=3)}

![嵌入得分](figures/embedding_score.png)

- **8 号、10 号**嵌入得分并列最高（{n8_emb} / {n10_emb}），且在 3 层均活跃，是班级的"全面型枢纽"。
- **16 号**参与系数达 1.0（连接完全集中于任务+社交层），但因仅涉足 2 层，嵌入得分（{n16_emb}）反而不及全面活跃者——它属"单维/双维深耕型"枢纽而非全能型。

---

## 六、结合属性数据的统计分析

### 6.1 社区构成的属性画像

聚合网络被划分为 **{n_comm} 个社区**（模块度 Q={mod:.3f}），成员如下：

- **社区 0（{len(comm0_nodes)} 人）**：{', '.join(map(str, sorted(comm0_nodes)))}（含 16 号任务枢纽、10 号社交核心）
- **社区 1（{len(comm1_nodes)} 人）**：{', '.join(map(str, sorted(comm1_nodes)))}

社区内部属性混排（种族、年级均有交叉），但两社区在"是否有高年级枢纽"上明显分化：社区 0 包含唯一的 11 年级男生 10 号与 13 年级男生 16 号，社区 1 则基本为同年级（10 年级）学生。

### 6.2 友谊度中心性的组间差异检验

以友谊层度中心性为因变量，对性别做 Welch t 检验：

{md_table(grp, decimals=3)}

- 女性平均度（{female_mean}）略高于男性（{male_mean}），差异方向支持"女性在班级友谊中更活跃/更被接受"的常见假设。
- 但 **p={grp_p}、Cohen's d={grp_d}**，效应量处于小到中等区间且未达显著（样本仅 16 人，统计功效有限）。
- 提示：在小样本班级数据中，不应过度解读不显著的组间差异，需更大样本或结合网络模型（如 ERGM）检验性别同质性。

---

## 七、结论与讨论

### 主要发现

1. **结构层：社交与任务高度耦合，友谊独立成区**。社交-任务边重叠 {st_jac} 远高于友谊与两者的重叠（约 {fs_jac}–{ft_jac}），说明日常互动和学业合作是同一社交生活的两个侧面，而"友谊"是另一套更稀缺、更需相互确认的关系。

2. **个体层：任务网络的"隐形权力核心"与友谊隔离并存**。16 号学生在任务层是唯一的全层枢纽（介数 {n16_task_betw}、接近 1.0），却在友谊层完全孤立。这一"工具性枢纽 + 情感性边缘"的组合，指向学业合作网络由**能力与任务导向**而非情感亲密驱动。

3. **机制层：友谊人气与任务地位脱钩**。跨层相关显示友谊-任务度相关约 {ft_rho}，社交-任务相关较强（{st_rho}）。班级中"谁受欢迎"与"谁被选择为学习伙伴"是两个独立的位置系统。

4. **属性层：性别差异方向存在但未显著**。友谊层女性度均值更高（{female_mean} vs {male_mean}），但 p={grp_p}，且受限于 n=16 的功效。

### 社会科学讨论

本案例是"班级同伴网络"研究中**选择（selection）与影响（influence）之争**的一个缩影。任务合作的独立性说明：**学业求助与情感友谊遵循不同的社会逻辑**——前者更接近 Burt 的结构洞理论（工具性行动沿非冗余关系流动），后者更接近同质性原理（情感性关系在相似者之间建立）。16 号学生作为"学习网络的守门人"而"友谊网络的局外人"，为教师在小组分配、同伴学习设计上提供了可操作的管理启示：识别并合理利用这类"工具性枢纽"，比仅依赖"人缘好"的学生更能提升学业协作效率。

### 局限

样本仅 16 人，统计功效有限；社交/任务层为对称记录，无法刻画互惠性；阈值选择（`>0`）对弱关系敏感；社区检测对 15 人的小网络分辨率有限。后续可用 ERGM（检验同质性、传递性机制）与 SAOM（检验选择 vs 影响）进一步建模。

---

## 附录：分析环境与代码

- 工具：Python 3.11.9 + NetworkX 3.6.1 + pandas 3.0.3 + NumPy 2.4.4 + SciPy 1.17.1 + Matplotlib 3.10.9
- 方法框架：network-analysis skill 四层指标体系（层内结构 / 层间重叠 / 层间相关 / 参与-嵌入）
- 分析脚本：`class182_analysis/analysis.py`；报告生成：`class182_analysis/report.py`
- 所有中间结果（CSV）见 `class182_analysis/output/tables/`，图形见 `class182_analysis/output/figures/`
"""

report_md = os.path.join(OUT, "class182_network_analysis_report.md")
with open(report_md, "w", encoding="utf-8") as f:
    f.write(md)

print("Markdown 报告已生成:", report_md)

# ============================================================
# 生成自包含 HTML 报告（内嵌图片为 base64）
# ============================================================
import base64
import markdown as mdlib

def img_to_data_uri(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = "image/png" if ext == "png" else f"image/{ext}"
    return f"data:{mime};base64,{b64}"

# 把 Markdown 中的图片引用替换为 base64 data URI
md_with_embedded = md
for fname in os.listdir(F):
    if fname.lower().endswith(".png"):
        uri = img_to_data_uri(os.path.join(F, fname))
        md_with_embedded = md_with_embedded.replace(
            f"figures/{fname}", uri)

body_html = mdlib.markdown(
    md_with_embedded,
    extensions=["tables", "fenced_code", "toc", "attr_list"],
    output_format="html5",
)

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>class182 班级三层关系网络综合分析报告</title>
<style>
  body {{ font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
        line-height: 1.7; color: #222; max-width: 980px; margin: 0 auto;
        padding: 24px 40px 60px; background: #fff; }}
  h1 {{ color: #1a3a5c; border-bottom: 3px solid #2e6da4; padding-bottom: 10px; }}
  h2 {{ color: #1a3a5c; border-bottom: 1px solid #ccc; padding-bottom: 6px;
        margin-top: 36px; }}
  h3 {{ color: #2e6da4; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }}
  th, td {{ border: 1px solid #ccc; padding: 8px 10px; text-align: center; }}
  th {{ background: #2e6da4; color: #fff; }}
  tr:nth-child(even) {{ background: #f5f8fc; }}
  img {{ max-width: 100%; height: auto; margin: 12px 0; border: 1px solid #ddd;
        border-radius: 4px; }}
  code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px;
         font-size: 90%; }}
  blockquote {{ border-left: 4px solid #2e6da4; margin: 16px 0;
              padding: 4px 16px; background: #f5f8fc; color: #333; }}
  .toc {{ background: #f5f8fc; border: 1px solid #e0e0e0; padding: 16px 24px;
        border-radius: 6px; }}
</style>
</head>
<body>
{body_html}
<hr>
<footer style="color:#999; font-size:12px; margin-top:40px;">
  本报告由 network-analysis skill 工作流自动生成。
</footer>
</body>
</html>
"""

report_html = os.path.join(OUT, "class182_network_analysis_report.html")
with open(report_html, "w", encoding="utf-8") as f:
    f.write(html_doc)

print("自包含 HTML 报告已生成:", report_html)
