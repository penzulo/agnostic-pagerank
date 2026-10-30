"""Ground-truth fixture: dense eig solution and networkx must agree."""

import json
from pathlib import Path

import networkx as nx
import numpy as np
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def spec():
    return json.loads((FIXTURES / "toy_graph.json").read_text())


@pytest.fixture(scope="module")
def expected():
    return json.loads((FIXTURES / "toy_graph_ranks.json").read_text())


def test_expected_fixture_sums_to_one(expected):
    assert sum(expected.values()) == pytest.approx(1.0)


def test_networkx_matches_fixture(spec, expected):
    graph = nx.DiGraph()
    graph.add_nodes_from(spec["nodes"])
    for source, target, weight in spec["edges"]:
        graph.add_edge(source, target, weight=weight)
    ranks = nx.pagerank(graph, alpha=spec["damping"], weight="weight", tol=1e-12)
    for node, value in expected.items():
        assert ranks[node] == pytest.approx(value, abs=1e-9)


def test_eig_matches_fixture(spec, expected):
    nodes = spec["nodes"]
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}
    adjacency = np.zeros((n, n))
    for source, target, weight in spec["edges"]:
        adjacency[index[target], index[source]] += weight
    m = adjacency / adjacency.sum(axis=0)
    g = spec["damping"] * m + (1 - spec["damping"]) * np.ones((n, n)) / n
    eigenvalues, eigenvectors = np.linalg.eig(g)
    principal = eigenvectors[:, int(np.argmin(np.abs(eigenvalues - 1.0)))].real
    ranks = principal / principal.sum()
    for node, value in expected.items():
        assert ranks[index[node]] == pytest.approx(value, abs=1e-9)
