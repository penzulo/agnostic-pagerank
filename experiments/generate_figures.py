import json
import time
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from agnostic_pagerank.core import Graph, PageRankConfig, solve_pagerank

FIG_DIR = Path('/home/penzulo/Dev/agnostic-pagerank/agnostic_pagerank_report_latex/report/figures')
FIG_DIR.mkdir(parents=True, exist_ok=True)

spec = json.loads(Path('/home/penzulo/Dev/agnostic-pagerank/tests/fixtures/toy_graph.json').read_text())
nodes = spec['nodes']
edges = [tuple(e) for e in spec['edges']]

# Convergence
plt.figure(figsize=(8, 5))
for d in [0.5, 0.7, 0.85, 0.95]:
    result = solve_pagerank(Graph(nodes=nodes, edges=edges), PageRankConfig(damping=d, tolerance=1e-12)).unwrap()
    plt.semilogy(range(1, len(result.history)+1), result.history, label=f'd={d}')
plt.xlabel('Iteration')
plt.ylabel(r'$L_1$ error')
plt.title('Convergence of Power Iteration for Different Damping Factors')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIG_DIR / 'convergence_damping.png', dpi=150)
plt.close()

# Iterations vs size
plt.figure(figsize=(8, 5))
sizes = [10, 20, 50, 100]
iters = []
for sz in sizes:
    g = nx.gnm_random_graph(sz, max(sz, sz*2), directed=True, seed=42)
    nodes_g = [str(i) for i in range(sz)]
    edges_g = [(nodes_g[u], nodes_g[v], 1.0) for u,v in g.edges()]
    res = solve_pagerank(Graph(nodes_g, edges_g), PageRankConfig(damping=0.85, tolerance=1e-8)).unwrap()
    iters.append(res.iterations)
plt.plot(sizes, iters, 'o-', linewidth=2, markersize=8)
plt.xlabel('Number of Nodes')
plt.ylabel('Iterations to Converge')
plt.title('Iterations vs Graph Size (d=0.85, tol=1e-8)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIG_DIR / 'iterations_vs_size.png', dpi=150)
plt.close()

# Runtime
plt.figure(figsize=(8, 5))
sizes = [5, 10, 15, 20, 25]
t_sparse = []
t_dense = []
for sz in sizes:
    g = nx.gnm_random_graph(sz, max(sz, sz*2), directed=True, seed=123)
    nodes_g = [str(i) for i in range(sz)]
    edges_g = [(nodes_g[u], nodes_g[v], 1.0) for u,v in g.edges()]
    graph = Graph(nodes_g, edges_g)
    start = time.time()
    solve_pagerank(graph, PageRankConfig(damping=0.85, tolerance=1e-8)).unwrap()
    t_sparse.append(time.time() - start)
    start = time.time()
    A = np.zeros((sz,sz))
    idx = {n:i for i,n in enumerate(nodes_g)}
    for s,t,w in edges_g:
        A[idx[t], idx[s]] += w
    out = A.sum(axis=0)
    M = np.divide(A, out, where=out!=0)
    for j in range(sz):
        if out[j] == 0:
            M[:,j] = 1.0/sz
    G = 0.85*M + 0.15*np.ones((sz,sz))/sz
    np.linalg.eig(G)
    t_dense.append(time.time() - start)
plt.plot(sizes, t_sparse, 'o-', label='Power Iteration (sparse)', linewidth=2)
plt.plot(sizes, t_dense, 's-', label='Dense Eigendecomposition', linewidth=2)
plt.xlabel('Number of Nodes')
plt.ylabel('Runtime (seconds)')
plt.title('Runtime Comparison: Power Iteration vs Dense Eig')
plt.legend()
plt.grid(True, alpha=0.3)
plt.yscale('log')
plt.tight_layout()
plt.savefig(FIG_DIR / 'runtime_power_vs_eig.png', dpi=150)
plt.close()

# Dangling
plt.figure(figsize=(10, 5))
g_dang = Graph(nodes=['A','B','C'], edges=[('A','B',1.0),('B','A',1.0)])
res_dang = solve_pagerank(g_dang).unwrap()
plt.bar(range(len(res_dang.ranked)), [s for _,s in res_dang.ranked], tick_label=[n for n,_ in res_dang.ranked])
plt.title('Dangling Node Handling (Node C has no outgoing edges - mass redistributed uniformly)')
plt.ylabel('PageRank Score')
plt.tight_layout()
plt.savefig(FIG_DIR / 'dangling_on_off.png', dpi=150)
plt.close()

# Top 20
plt.figure(figsize=(10, 6))
res_toy = solve_pagerank(Graph(nodes=nodes, edges=edges)).unwrap()
labels = [n for n,_ in res_toy.ranked]
scores = [s for _,s in res_toy.ranked]
plt.bar(labels, scores)
plt.title('Top Ranked Nodes')
plt.ylabel('PageRank Score')
plt.tight_layout()
plt.savefig(FIG_DIR / 'top20_bar.png', dpi=150)
plt.close()

# Subgraph
plt.figure(figsize=(12, 10))
G_vis = nx.DiGraph()
G_vis.add_nodes_from(nodes)
for s,t,w in edges:
    G_vis.add_edge(s,t)
pos = nx.spring_layout(G_vis, seed=42)
node_sizes = [res_toy.scores[[i for i,n in enumerate(nodes) if n==node][0]] * 15000 for node in G_vis.nodes()]
nx.draw(G_vis, pos, node_size=node_sizes, with_labels=True, 
        node_color='lightblue', arrows=True, arrowsize=20,
        font_size=14, font_weight='bold')
plt.title('Subgraph Visualization (node size proportional to PageRank)')
plt.tight_layout()
plt.savefig(FIG_DIR / 'subgraph_top50.png', dpi=150)
plt.close()

# CLI table
plt.figure(figsize=(8, 4))
plt.axis('tight')
plt.axis('off')
table_data = [['Rank', 'Node', 'Score']] + [[i+1, n, f'{s:.9f}'] for i,(n,s) in enumerate(res_toy.ranked)]
table = plt.table(cellText=table_data, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
plt.title('Top Ranked Nodes - CLI Output')
plt.savefig(FIG_DIR / 'cli_top_table.png', dpi=150, bbox_inches='tight')
plt.close()

# Toy edge list
plt.figure(figsize=(6, 4))
plt.axis('tight')
plt.axis('off')
edge_data = [['Source', 'Target', 'Weight']] + [[s,t,w] for s,t,w in edges]
table = plt.table(cellText=edge_data, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
plt.title('Toy Graph Edge List')
plt.savefig(FIG_DIR / 'toy_edgelist.png', dpi=150, bbox_inches='tight')
plt.close()

# Placeholders for others
for name in ['crawl_edges_csv.png', 'snap_edges.png']:
    plt.figure(figsize=(8, 4))
    plt.axis('tight')
    plt.axis('off')
    plt.text(0.5, 0.5, f'[{name.replace(".png","")}]\n(Generated during actual crawl/SNAP download)', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    plt.savefig(FIG_DIR / name, dpi=150, bbox_inches='tight')
    plt.close()

print('Done')
