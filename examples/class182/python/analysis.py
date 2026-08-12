# -*- coding: utf-8 -*-
"""
class182 班级三层关系网络 —— 完整社会网络分析
基于 network-analysis skill 的方法论框架（4 层指标体系）
与教程 network analysis skill_tutorial.md 的五阶段报告结构。
"""
import os
import json
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats

# 中文字体设置
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(ROOT), "data")
OUT = os.path.join(ROOT, "output")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)
os.makedirs(os.path.join(OUT, "tables"), exist_ok=True)

RNG = np.random.default_rng(42)
plt.rcParams["figure.dpi"] = 120

# ============================================================
# Stage 1: 数据导入与预处理
# ============================================================
def load_data():
    ties = pd.read_csv(os.path.join(DATA, "class182_networkdata.csv"))
    attrs = pd.read_csv(os.path.join(DATA, "class182_attributedata.csv"))
    return ties, attrs

def build_layer(ties, attrs, col, directed=True, threshold=None, weighted=False):
    """按关系列构建网络层。阈值二值化 + 去自环。"""
    if threshold is not None:
        sub = ties[ties[col] >= threshold]
    else:
        sub = ties[ties[col] > 0]
    sub = sub[sub["ego"] != sub["alter"]]
    edges = list(zip(sub["ego"], sub["alter"]))
    weights = None
    if weighted:
        w = sub.groupby(["ego", "alter"])[col].mean().to_dict()
        weights = [w.get((a, b), w.get((b, a), 1.0)) for a, b in edges]
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(attrs["ids"].astype(int).tolist())
    G.add_edges_from(edges)
    if weighted:
        for i, (a, b) in enumerate(G.edges()):
            G[a][b]["weight"] = weights[i] if i < len(weights) else 1.0
    # 属性
    for _, r in attrs.iterrows():
        G.nodes[int(r["ids"])]["race"] = str(r["race"])
        G.nodes[int(r["ids"])]["grade"] = int(r["grade"])
        G.nodes[int(r["ids"])]["gender"] = str(r["gender"])
    return G

# ============================================================
# Stage 2: 整体结构指标
# ============================================================
def layer_metrics(G, name):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    und = G.to_undirected() if G.is_directed() else G
    comp = list(nx.connected_components(und))
    gcc_nodes = max(comp, key=len) if comp else set()
    gcc = und.subgraph(gcc_nodes)
    # 有向：入度、出度；无向：度
    if G.is_directed():
        avg_deg = m / n
    else:
        avg_deg = 2 * m / n
    metrics = {
        "layer": name,
        "nodes": n,
        "edges": m,
        "density": nx.density(und),
        "avg_degree": round(avg_deg, 4),
        "avg_clustering": round(nx.average_clustering(und), 4) if n > 0 else np.nan,
        "components": len(comp),
        "gcc_ratio": round(len(gcc_nodes) / n, 4) if n > 0 else np.nan,
        "diameter": nx.diameter(gcc) if gcc.number_of_nodes() > 1 else np.nan,
        "avg_path_length": round(nx.average_shortest_path_length(gcc), 4) if gcc.number_of_nodes() > 1 else np.nan,
        "assortativity": round(nx.degree_assortativity_coefficient(und), 4),
    }
    if G.is_directed():
        rec = nx.reciprocity(G)
        metrics["reciprocity"] = round(rec, 4)
    return metrics

# ============================================================
# Stage 3: 中心性分析
# ============================================================
def centrality_df(G, name):
    und = G.to_undirected() if G.is_directed() else G
    df = pd.DataFrame(index=list(G.nodes()))
    if G.is_directed():
        df["indegree"] = pd.Series(dict(G.in_degree()))
        df["outdegree"] = pd.Series(dict(G.out_degree()))
        df["degree"] = df["indegree"] + df["outdegree"]
    else:
        df["degree"] = pd.Series(dict(G.degree()))
    df["betweenness"] = pd.Series(nx.betweenness_centrality(und, normalized=True))
    df["closeness"] = pd.Series(nx.closeness_centrality(und))
    df["eigenvector"] = pd.Series(nx.eigenvector_centrality(und, max_iter=1000, tol=1e-6))
    df["layer"] = name
    df.index.name = "node"
    return df.reset_index()

# ============================================================
# Stage 4: 多层网络分析
# ============================================================
def edge_set(G):
    if G.is_directed():
        return {(a, b) for a, b in G.edges()}
    return {(min(a, b), max(a, b)) for a, b in G.edges()}

def node_overlap(G1, G2):
    v1, v2 = set(G1.nodes()), set(G2.nodes())
    inter = v1 & v2
    jac = len(inter) / len(v1 | v2) if (v1 | v2) else 0
    return round(jac, 4), round(len(inter) / len(v1), 4) if v1 else 0, round(len(inter) / len(v2), 4) if v2 else 0

def edge_overlap(G1, G2):
    e1, e2 = edge_set(G1), edge_set(G2)
    inter = e1 & e2
    jac = len(inter) / len(e1 | e2) if (e1 | e2) else 0
    return round(jac, 4), len(inter), len(e1), len(e2)

def participation_coefficient(layer_dict, node):
    degs = {}
    for name, G in layer_dict.items():
        d = G.degree(node) if node in G else 0
        if d > 0:
            degs[name] = d
    M = len(degs)
    if M <= 1:
        return 0.0
    o = sum(degs.values())
    if o == 0:
        return 0.0
    pc = (M / (M - 1)) * (1 - sum((d / o) ** 2 for d in degs.values()))
    return round(pc, 4)

def embedding_score(layer_dict, node):
    L = sum(1 for G in layer_dict.values() if node in G and G.degree(node) > 0)
    if L == 0:
        return 0.0
    d = sum(G.degree(node) for G in layer_dict.values() if node in G)
    return round(L * (1 + np.log(1 + d)), 4)

# ============================================================
# Stage 5: 可视化
# ============================================================
def plot_network(G, name, attrs_map, pos=None, ax=None, title=None, colors=None, sizes=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 6))
    if pos is None:
        pos = nx.spring_layout(G, seed=42, k=1.2)
    node_colors = [colors.get(n, "#cccccc") for n in G.nodes()] if colors else "#5b9bd5"
    node_sizes = [sizes.get(n, 300) for n in G.nodes()] if sizes else 400
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#b0b0b0", alpha=0.35, width=0.8)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
                           linewidths=0.5, edgecolors="black")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7)
    ax.set_title(title or name, fontsize=13)
    ax.axis("off")
    return pos

def main():
    ties, attrs = load_data()

    # ===== Stage 1: 构建三层网络 =====
    # friend: 有序 0/1/2，>=1 视为朋友（有向提名）
    # social/task: 连续权重，>0 视为存在（对称记录，按无向处理以反映"互动关系"）
    g_friend = build_layer(ties, attrs, "friend_tie", directed=True, threshold=1)
    g_social = build_layer(ties, attrs, "social_tie", directed=False, threshold=None)
    g_task = build_layer(ties, attrs, "task_tie", directed=False, threshold=None)

    # 值网络阈值敏感性检查（Stage 1 报告）
    # 口径：与建图一致，去自环 + 无向唯一边（对称双向只计一条）
    # "边数(>0)" = 建图层采用的实际存在边；其余为不同阈值下的有效边数
    threshold_report = []
    for col in ["social_tie", "task_tie"]:
        row = {"layer": col}
        sub_all = ties[(ties[col] > 0) & (ties["ego"] != ties["alter"])]
        base = set()
        for _, r in sub_all.iterrows():
            a, b = int(r["ego"]), int(r["alter"])
            base.add((min(a, b), max(a, b)))
        row["edges_gt0"] = len(base)
        for th in [1.0, 1.5, 2.0]:
            sub = ties[(ties[col] >= th) & (ties["ego"] != ties["alter"])]
            unique_edges = set()
            for _, r in sub.iterrows():
                a, b = int(r["ego"]), int(r["alter"])
                unique_edges.add((min(a, b), max(a, b)))
            row[f"t>={th}"] = len(unique_edges)
        threshold_report.append(row)
    thr_df = pd.DataFrame(threshold_report)

    layers = {"friend": g_friend, "social": g_social, "task": g_task}

    # ===== Stage 2: 结构指标 =====
    metrics_rows = [layer_metrics(G, name) for name, G in layers.items()]
    metrics_df = pd.DataFrame(metrics_rows)

    # ===== Stage 3: 中心性 =====
    cent_dfs = [centrality_df(G, name) for name, G in layers.items()]
    cent_all = pd.concat(cent_dfs, ignore_index=True)
    # 合并属性
    cent_all = cent_all.merge(attrs.rename(columns={"ids": "node"}), on="node", how="left")

    # ===== Stage 4: 多层分析 =====
    pair_names = [("friend", "social"), ("friend", "task"), ("social", "task")]
    node_ov = [{"pair": f"{a}-{b}",
                "node_jaccard": node_overlap(layers[a], layers[b])[0],
                "overlap_rate_" + a: node_overlap(layers[a], layers[b])[1],
                "overlap_rate_" + b: node_overlap(layers[a], layers[b])[2]}
               for a, b in pair_names]
    node_ov_df = pd.DataFrame(node_ov)
    edge_ov = [{"pair": f"{a}-{b}",
                "edge_jaccard": edge_overlap(layers[a], layers[b])[0],
                "shared_edges": edge_overlap(layers[a], layers[b])[1],
                "edges_"+a: edge_overlap(layers[a], layers[b])[2],
                "edges_"+b: edge_overlap(layers[a], layers[b])[3]}
               for a, b in pair_names]
    edge_ov_df = pd.DataFrame(edge_ov)
    # 方向性重叠：任务边多大比例同时是友谊边
    dir_overlap = {}
    for a, b in pair_names:
        ea = edge_set(layers[a]); eb = edge_set(layers[b])
        dir_overlap[f"{a}→{b}"] = round(len(ea & eb) / len(ea), 4) if ea else 0

    # 跨层中心性相关（Spearman，公共节点）
    corr_rows = []
    common_nodes = set(g_friend.nodes()) & set(g_social.nodes()) & set(g_task.nodes())
    if len(common_nodes) >= 5:
        # 用"层内总度"作为各层中心性代理
        deg_f = dict(g_friend.degree()); deg_s = dict(g_social.degree()); deg_t = dict(g_task.degree())
        common = sorted(common_nodes)
        for (a, b), (dv, dw) in [(("friend","social"),(deg_f,deg_s)),
                                  (("friend","task"),(deg_f,deg_t)),
                                  (("social","task"),(deg_s,deg_t))]:
            x = [dv[i] for i in common]; y = [dw[i] for i in common]
            rho, p = stats.spearmanr(x, y)
            corr_rows.append({"pair": f"{a}-{b}", "rho": round(rho, 4), "p": p,
                              "common_nodes": len(common)})
    corr_df = pd.DataFrame(corr_rows)

    # 参与系数 PC 与嵌入得分
    all_nodes = sorted(set().union(*[set(G.nodes()) for G in layers.values()]))
    embed_rows = []
    for node in all_nodes:
        pc = participation_coefficient(layers, node)
        emb = embedding_score(layers, node)
        lcnt = sum(1 for G in layers.values() if node in G and G.degree(node) > 0)
        tdeg = sum(G.degree(node) for G in layers.values() if node in G)
        embed_rows.append({"node": node, "layer_count": lcnt, "total_degree": tdeg,
                           "participation_coefficient": pc, "embedding_score": emb})
    embed_df = pd.DataFrame(embed_rows)
    # 合并属性
    embed_df = embed_df.merge(attrs.rename(columns={"ids": "node"}), on="node", how="left")

    # 社区检测（聚合网络）
    agg = nx.Graph()
    for G in layers.values():
        agg.add_nodes_from(G.nodes())
        for a, b in edge_set(G):
            agg.add_edge(a, b)
    comm = nx.community.louvain_communities(agg, seed=42, resolution=1.0)
    comm_df = pd.DataFrame([{"node": n, "community": i}
                            for i, c in enumerate(comm) for n in c])
    comm_df = comm_df.merge(attrs.rename(columns={"ids": "node"}), on="node", how="left")
    modularity = nx.community.modularity(agg, comm)

    # ===== 属性统计分析 =====
    # 以 friend 层入度为例，做性别/年级的组间比较
    friend_cent = cent_all[cent_all["layer"] == "friend"].set_index("node")
    stat_rows = []
    for attr in ["gender", "grade"]:
        groups = sorted(friend_cent[attr].dropna().unique())
        if len(groups) == 2:
            g0 = friend_cent[friend_cent[attr] == groups[0]]["degree"]
            g1 = friend_cent[friend_cent[attr] == groups[1]]["degree"]
            tstat, pval = stats.ttest_ind(g0, g1, equal_var=False)
            # Cohen's d
            sp = np.sqrt((np.var(g0, ddof=1) + np.var(g1, ddof=1)) / 2)
            cohens_d = (g1.mean() - g0.mean()) / sp if sp > 0 else 0
            stat_rows.append({"attribute": attr, "group_1": str(groups[0]),
                              "mean_1": round(g0.mean(), 3), "group_2": str(groups[1]),
                              "mean_2": round(g1.mean(), 3),
                              "t": round(tstat, 3), "p": round(pval, 4),
                              "cohens_d": round(cohens_d, 3)})
    stat_df = pd.DataFrame(stat_rows)

    # ===== 输出 CSV =====
    thr_df.to_csv(os.path.join(OUT, "tables", "threshold_sensitivity.csv"), index=False)
    metrics_df.to_csv(os.path.join(OUT, "tables", "layer_metrics.csv"), index=False)
    cent_all.to_csv(os.path.join(OUT, "tables", "centrality_all.csv"), index=False)
    node_ov_df.to_csv(os.path.join(OUT, "tables", "node_overlap.csv"), index=False)
    edge_ov_df.to_csv(os.path.join(OUT, "tables", "edge_overlap.csv"), index=False)
    corr_df.to_csv(os.path.join(OUT, "tables", "degree_correlation.csv"), index=False)
    embed_df.to_csv(os.path.join(OUT, "tables", "embedding.csv"), index=False)
    comm_df.to_csv(os.path.join(OUT, "tables", "communities.csv"), index=False)
    stat_df.to_csv(os.path.join(OUT, "tables", "group_differences.csv"), index=False)

    # ===== 可视化 =====
    # 1. 三层并列网络（共享布局，性别着色，度定大小）
    base_pos = nx.spring_layout(agg, seed=42, k=1.3)
    gender_col = {"male": "#E63946", "female": "#1D3557"}
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, (name, G) in zip(axes, layers.items()):
        colors = {n: gender_col.get(G.nodes[n].get("gender", ""), "#ccc") for n in G.nodes()}
        deg = dict(G.degree())
        sizes = {n: 100 + deg[n] * 90 for n in G.nodes()}
        plot_network(G, name, attrs, pos=base_pos, ax=ax, colors=colors, sizes=sizes)
    handles = [Line2D([0],[0], marker='o', color='w', markerfacecolor=gender_col[k], markersize=10, label=k) for k in gender_col]
    fig.legend(handles=handles, loc='upper right', title="性别", ncol=2)
    fig.suptitle("class182 三层关系网络（同一布局，性别着色，节点大小=度）", fontsize=14)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "multilayer_panel.png"), bbox_inches="tight"); plt.close()

    # 2. 社区检测
    colors_comm = plt.cm.tab10(np.linspace(0, 1, len(comm)))
    comm_color = {}
    for i, c in enumerate(comm):
        for n in c:
            comm_color[n] = matplotlib.colors.to_hex(colors_comm[i])
    fig, ax = plt.subplots(figsize=(8, 6))
    plot_network(agg, "聚合网络", attrs, pos=base_pos, ax=ax, colors=comm_color,
                 sizes={n: 100 + dict(agg.degree())[n] * 60 for n in agg.nodes()})
    ax.set_title(f"聚合网络社区检测（Louvain，模块度 Q={modularity:.3f}）")
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "community_detection.png"), bbox_inches="tight"); plt.close()

    # 3. 度分布
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, G in layers.items():
        degs = [d for _, d in G.degree()]
        ax.hist(degs, bins=range(0, max(degs)+2), alpha=0.5, label=name)
    ax.set_xlabel("度"); ax.set_ylabel("频数"); ax.set_title("三层网络度分布")
    ax.legend(); plt.tight_layout(); plt.savefig(os.path.join(FIG, "degree_distribution.png"), bbox_inches="tight"); plt.close()

    # 4. 中心性热图/条形图
    friend_top = friend_cent.sort_values("degree", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(friend_top.index.astype(str), friend_top["degree"],
           color=[gender_col.get(friend_top.loc[i, "gender"], "#ccc") for i in friend_top.index])
    ax.set_xlabel("学生"); ax.set_ylabel("友谊度中心性"); ax.set_title("友谊层度中心性 Top10（按性别着色）")
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "friend_degree_top10.png"), bbox_inches="tight"); plt.close()

    # 5. 嵌入得分
    top_embed = embed_df.sort_values("embedding_score", ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top_embed["node"].astype(str), top_embed["embedding_score"],
            color=[gender_col.get(g, "#ccc") for g in top_embed["gender"]])
    ax.set_xlabel("嵌入得分 S(i) = 层数 x (1+ln(1+度))"); ax.set_ylabel("学生")
    ax.set_title("多层嵌入得分 Top12（按性别着色）"); ax.invert_yaxis()
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "embedding_score.png"), bbox_inches="tight"); plt.close()

    print("=== 分析完成 ===")
    print(metrics_df.to_string(index=False))

    # 保存所有结果供报告使用
    results = {
        "metrics_df": metrics_df, "cent_all": cent_all, "node_ov_df": node_ov_df,
        "edge_ov_df": edge_ov_df, "corr_df": corr_df, "embed_df": embed_df,
        "comm_df": comm_df, "stat_df": stat_df, "dir_overlap": dir_overlap,
        "modularity": modularity, "n_communities": len(comm), "thr_df": thr_df,
    }
    return results

if __name__ == "__main__":
    main()
