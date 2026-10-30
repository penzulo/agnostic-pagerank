"""Solver smoke tests against the Phase 1 ground-truth fixture."""

import json
from pathlib import Path

import pytest
from returns.result import Failure, Success

from agnostic_pagerank.core import (
    Graph,
    PageRankConfig,
    SolverError,
    solve_pagerank,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _toy_graph(edges=None) -> Graph:
    spec = json.loads((FIXTURES / "toy_graph.json").read_text())
    return Graph(
        nodes=spec["nodes"],
        edges=edges if edges is not None else [tuple(e) for e in spec["edges"]],
    )


def test_matches_dense_ground_truth():
    expected = json.loads((FIXTURES / "toy_graph_ranks.json").read_text())
    result = solve_pagerank(_toy_graph())
    assert isinstance(result, Success)
    scores = dict(result.unwrap().ranked)
    for node, value in expected.items():
        assert scores[node] == pytest.approx(value, abs=1e-6)


def test_ranks_sum_to_one():
    result = solve_pagerank(_toy_graph()).unwrap()
    assert sum(score for _, score in result.ranked) == pytest.approx(1.0)


def test_edge_order_invariant():
    spec = json.loads((FIXTURES / "toy_graph.json").read_text())
    edges = [tuple(e) for e in spec["edges"]]
    forward = solve_pagerank(_toy_graph(edges)).unwrap().scores
    reverse = solve_pagerank(_toy_graph(edges[::-1])).unwrap().scores
    assert forward == pytest.approx(reverse)


def test_dangling_node_redistributes_uniformly():
    graph = Graph(nodes=["A", "B", "C"], edges=[("A", "B", 1.0), ("B", "A", 1.0)])
    result = solve_pagerank(graph).unwrap()
    assert result.converged
    assert sum(score for _, score in result.ranked) == pytest.approx(1.0)


def test_empty_graph_fails():
    result = solve_pagerank(Graph(nodes=[]))
    assert isinstance(result, Failure)
    assert result.failure() is SolverError.EMPTY_GRAPH


def test_invalid_damping_fails():
    result = solve_pagerank(_toy_graph(), PageRankConfig(damping=1.5))
    assert isinstance(result, Failure)
    assert result.failure() is SolverError.INVALID_DAMPING


def test_history_shrinks():
    result = solve_pagerank(_toy_graph()).unwrap()
    assert result.converged
    assert result.history[-1] < result.history[0]
    assert result.iterations == len(result.history)
