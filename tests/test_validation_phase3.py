"""More Phase 3 validation tests."""

import random

import networkx as nx
import pytest
from returns.result import Failure, Success

from agnostic_pagerank.core import Graph, PageRankConfig, SolverError, solve_pagerank


def test_matches_networkx_on_random_graphs():
    random.seed(12345)
    for _ in range(5):
        n = random.randint(5, 25)
        graph_nx = nx.gnm_random_graph(
            n, random.randint(n, 4 * n), directed=True, seed=random.randint(0, 10_000)
        )
        nodes = [f"N{i}" for i in range(n)]
        edges = []
        for u, v in graph_nx.edges():
            edges.append((nodes[u], nodes[v], 1.0))
        graph = Graph(nodes=nodes, edges=edges)
        result = solve_pagerank(graph, PageRankConfig(damping=0.85, tolerance=1e-9))
        assert isinstance(result, Success)
        ours = dict(result.unwrap().ranked)
        nx_ranks = nx.pagerank(graph_nx, alpha=0.85, weight=None)
        for i, node in enumerate(nodes):
            assert ours[node] == pytest.approx(nx_ranks[i], abs=1e-5)


def test_ranks_sum_to_one_dense_eig_all_cases():
    # already covered for toy; ensure no NaN/inf and sums to 1
    graph = Graph(nodes=["A", "B"], edges=[("A", "B", 1.0)])
    result = solve_pagerank(graph).unwrap()
    s = sum(score for _, score in result.ranked)
    assert s == pytest.approx(1.0)


def test_disconnected_components():
    graph = Graph(nodes=["A", "B", "C", "D"], edges=[("A", "B", 1.0)])
    result = solve_pagerank(graph).unwrap()
    assert result.converged
    assert sum(score for _, score in result.ranked) == pytest.approx(1.0)


def test_self_loops():
    graph = Graph(
        nodes=["A", "B"], edges=[("A", "B", 1.0), ("B", "B", 1.0), ("B", "A", 1.0)]
    )
    result = solve_pagerank(graph).unwrap()
    assert sum(score for _, score in result.ranked) == pytest.approx(1.0)


def test_single_node():
    graph = Graph(nodes=["X"], edges=[])
    result = solve_pagerank(graph).unwrap()
    assert len(result.ranked) == 1
    assert result.ranked[0][1] == pytest.approx(1.0)


def test_empty_graph_fails_phase3():
    result = solve_pagerank(Graph(nodes=[]))
    assert isinstance(result, Failure)
    assert result.failure() is SolverError.EMPTY_GRAPH


def test_edge_order_invariance_phase3():
    graph = Graph(
        nodes=["A", "B", "C"], edges=[("A", "B", 1.0), ("B", "C", 1.0), ("C", "A", 1.0)]
    )
    g1 = solve_pagerank(graph).unwrap().scores
    g2 = (
        solve_pagerank(
            Graph(
                nodes=["A", "B", "C"],
                edges=[("C", "A", 1.0), ("A", "B", 1.0), ("B", "C", 1.0)],
            )
        )
        .unwrap()
        .scores
    )
    assert g1 == pytest.approx(g2)
