"""Plot convergence (error vs iteration) for damping = 0.5, 0.7, 0.85, 0.95."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agnostic_pagerank.core import Graph, PageRankConfig, solve_pagerank

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"


def main() -> None:
    spec = json.loads((FIXTURES / "toy_graph.json").read_text())
    nodes, edges = spec["nodes"], [tuple(e) for e in spec["edges"]]
    graph = Graph(nodes=nodes, edges=edges)

    plt.figure(figsize=(8, 5))
    for d in [0.5, 0.7, 0.85, 0.95]:
        result = solve_pagerank(
            graph, PageRankConfig(damping=d, tolerance=1e-12)
        ).unwrap()
        plt.semilogy(
            range(1, len(result.history) + 1), result.history, label=f"d={d}"
        )
    plt.xlabel("Iteration")
    plt.ylabel(r"$\|r^{(k+1)} - r^{(k)}\|_1$")
    plt.title("Convergence vs Damping Factor")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("experiments/convergence_damping.png", dpi=150)
    plt.close()
    print("saved experiments/convergence_damping.png")


if __name__ == "__main__":
    main()
