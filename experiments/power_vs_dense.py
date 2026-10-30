"""Compare power iteration time vs dense eigendecomposition on growing graphs."""

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from agnostic_pagerank.core import Graph, PageRankConfig, solve_pagerank


def main() -> None:
    sizes = [5, 10, 15, 20, 25, 30]
    t_sparse = []
    t_dense = []
    for sz in sizes:
        g = nx.gnm_random_graph(sz, max(sz, sz * 2), directed=True, seed=123)
        nodes_g = [str(i) for i in range(sz)]
        edges_g = [(nodes_g[u], nodes_g[v], 1.0) for u, v in g.edges()]
        graph = Graph(nodes_g, edges_g)
        start = time.time()
        solve_pagerank(graph, PageRankConfig(damping=0.85, tolerance=1e-8)).unwrap()
        t_sparse.append(time.time() - start)

        start = time.time()
        A = np.zeros((sz, sz))
        idx = {n: i for i, n in enumerate(nodes_g)}
        for s, t, w in edges_g:
            A[idx[t], idx[s]] += w
        out = A.sum(axis=0)
        M = np.divide(A, out, where=out != 0)
        for j in range(sz):
            if out[j] == 0:
                M[:, j] = 1.0 / sz
        G = 0.85 * M + 0.15 * np.ones((sz, sz)) / sz
        np.linalg.eig(G)
        t_dense.append(time.time() - start)

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, t_sparse, "o-", label="Power Iteration (sparse)", linewidth=2)
    plt.plot(sizes, t_dense, "s-", label="Dense Eigendecomposition", linewidth=2)
    plt.xlabel("Number of Nodes")
    plt.ylabel("Runtime (seconds)")
    plt.title("Power Iteration vs Dense Eigendecomposition")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig("experiments/power_vs_dense.png", dpi=150)
    plt.close()
    print("saved experiments/power_vs_dense.png")


if __name__ == "__main__":
    main()
