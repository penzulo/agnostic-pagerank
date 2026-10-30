"""Plot iterations-to-converge vs graph size."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from agnostic_pagerank.core import Graph, PageRankConfig, solve_pagerank


def main() -> None:
    sizes = [10, 20, 50, 100, 200]
    iters = []
    for sz in sizes:
        g = nx.gnm_random_graph(sz, max(sz, sz * 3), directed=True, seed=42)
        nodes_g = [str(i) for i in range(sz)]
        edges_g = [(nodes_g[u], nodes_g[v], 1.0) for u, v in g.edges()]
        res = solve_pagerank(
            Graph(nodes_g, edges_g), PageRankConfig(damping=0.85, tolerance=1e-8)
        ).unwrap()
        iters.append(res.iterations)

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, iters, "o-", linewidth=2, markersize=8)
    plt.xlabel("Number of Nodes")
    plt.ylabel("Iterations to Converge")
    plt.title("Iterations vs Graph Size (d=0.85, tol=1e-8)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("experiments/iterations_vs_size.png", dpi=150)
    plt.close()
    print("saved experiments/iterations_vs_size.png")


if __name__ == "__main__":
    main()
