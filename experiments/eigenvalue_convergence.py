"""Explain convergence rate in terms of the second-largest eigenvalue."""

import json
from pathlib import Path

import numpy as np

from agnostic_pagerank.core import Graph, PageRankConfig, solve_pagerank

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"


def main() -> None:
    spec = json.loads((FIXTURES / "toy_graph.json").read_text())
    nodes, edges = spec["nodes"], [tuple(e) for e in spec["edges"]]
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}

    A = np.zeros((n, n))
    for s, t, w in edges:
        A[index[t], index[s]] += w
    out = A.sum(axis=0)
    M = np.divide(A, out, where=out != 0)
    d = 0.85
    G = d * M + (1 - d) * np.ones((n, n)) / n
    evals = np.linalg.eigvals(G)
    evals_sorted = sorted(evals, key=lambda x: abs(x), reverse=True)
    print("Eigenvalues (by magnitude):", [(complex(e).real, complex(e).imag, abs(e)) for e in evals_sorted])
    print(f"|λ2| = {abs(evals_sorted[1]):.6f}, d = {d}, |λ2| <= d? {abs(evals_sorted[1]) <= d + 1e-10}")

    result = solve_pagerank(
        Graph(nodes=nodes, edges=edges), PageRankConfig(damping=d)
    ).unwrap()
    print(f"Converged in {result.iterations} iterations")


if __name__ == "__main__":
    main()
