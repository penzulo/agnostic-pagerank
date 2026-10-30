"""Phase 5 tests: SNAP loader + validation against networkx on a sampled subgraph.

We don't require downloading full 280k/875k datasets in CI; we create small
synthetic SNAP-format edge lists and verify correctness. If real SNAP data
exists under data/ it can be used for scaling experiments.
"""

import time

import networkx as nx
import pytest
from returns.result import Failure, Success

from agnostic_pagerank.adapters.snap import SnapError, load_snap_edge_list
from agnostic_pagerank.core import PageRankConfig, solve_pagerank


def test_load_snap_edge_list(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("# comment\n1 2\n2 3\n3 1\n")
    result = load_snap_edge_list(p)
    assert isinstance(result, Success)
    graph = result.unwrap()
    assert "1" in graph.nodes and "3" in graph.nodes
    assert len(graph.edges) == 3


def test_load_snap_missing_file(tmp_path):
    result = load_snap_edge_list(tmp_path / "nope.txt")
    assert isinstance(result, Failure)
    assert result.failure() is SnapError.FILE_NOT_FOUND


def test_load_snap_empty(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("# only comments\n")
    result = load_snap_edge_list(p)
    assert isinstance(result, Failure)
    assert result.failure() is SnapError.EMPTY_FILE


def test_solver_on_small_snap_matches_networkx(tmp_path):
    # small directed graph
    p = tmp_path / "graph.txt"
    p.write_text("0 1\n1 2\n2 0\n0 2\n")
    graph = load_snap_edge_list(p).unwrap()
    result = solve_pagerank(graph, PageRankConfig(damping=0.85, tolerance=1e-9))
    assert isinstance(result, Success)
    ours = dict(result.unwrap().ranked)

    g = nx.DiGraph()
    g.add_edges_from([(0, 1), (1, 2), (2, 0), (0, 2)])
    nxr = nx.pagerank(g, alpha=0.85)
    for node in ["0", "1", "2"]:
        assert ours[node] == pytest.approx(nxr[int(node)], abs=1e-6)


def test_runtime_recorded_for_small_graph(tmp_path):
    p = tmp_path / "g2.txt"
    lines = []
    for i in range(50):
        lines.append(f"{i} {(i + 1) % 50}")
    p.write_text("\n".join(lines))
    graph = load_snap_edge_list(p).unwrap()
    start = time.time()
    result = solve_pagerank(graph).unwrap()
    elapsed = time.time() - start
    assert result.iterations >= 1
    assert elapsed >= 0
