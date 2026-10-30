"""Compute the dense ground-truth PageRank for the toy graph.

Builds the column-stochastic transition matrix M from the edge list, forms
G = d*M + (1-d)/n * J, solves with numpy.linalg.eig, and writes the
normalized rank vector to tests/fixtures/toy_graph_ranks.json.
"""

import json
from pathlib import Path

import numpy as np

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"


def main() -> None:
    spec = json.loads((FIXTURES / "toy_graph.json").read_text())
    nodes: list[str] = spec["nodes"]
    edges: list[list[str]] = spec["edges"]
    d: float = spec["damping"]
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}

    adjacency = np.zeros((n, n))
    for source, target, weight in edges:
        adjacency[index[target], index[source]] += weight

    out_weight = adjacency.sum(axis=0)
    if np.any(out_weight == 0):
        raise ValueError("toy graph must have no dangling nodes")
    m = adjacency / out_weight

    j = np.ones((n, n)) / n
    g = d * m + (1 - d) * j

    eigenvalues, eigenvectors = np.linalg.eig(g)
    principal = eigenvectors[:, int(np.argmin(np.abs(eigenvalues - 1.0)))].real
    ranks = principal / principal.sum()

    result = {node: float(ranks[i]) for node, i in index.items()}
    (FIXTURES / "toy_graph_ranks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
