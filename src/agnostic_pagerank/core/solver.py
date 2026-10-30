"""Power-iteration PageRank solver over a SciPy sparse transition matrix."""

from dataclasses import dataclass, field

import numpy as np
from returns.result import Failure, Result, Success
from scipy import sparse

from .errors import SolverError
from .graph import Graph


@dataclass(frozen=True)
class PageRankConfig:
    damping: float = 0.85
    tolerance: float = 1e-8
    max_iterations: int = 100
    personalization: tuple[float, ...] | None = None


@dataclass
class PageRankResult:
    scores: np.ndarray
    ranked: list[tuple[str, float]]
    iterations: int
    history: list[float] = field(default_factory=list)
    converged: bool = True


def _validate_config(config: PageRankConfig, n: int) -> Result[None, SolverError]:
    if not 0 < config.damping < 1:
        return Failure(SolverError.INVALID_DAMPING)
    if config.tolerance <= 0:
        return Failure(SolverError.INVALID_TOLERANCE)
    if config.max_iterations < 1:
        return Failure(SolverError.INVALID_MAX_ITERATIONS)
    if config.personalization is not None:
        p = np.asarray(config.personalization, dtype=float)
        if p.shape != (n,) or np.any(p < 0) or abs(p.sum() - 1.0) > 1e-9:
            return Failure(SolverError.INVALID_PERSONALIZATION)
    return Success(None)


def transition_matrix(graph: Graph) -> sparse.csr_matrix:
    """Column-normalized transition matrix.

    M[i, j] is the probability of moving j -> i. Dangling columns (nodes
    with no outgoing edges) are redistributed uniformly over all nodes.
    """
    n = len(graph)
    index = graph.index
    if graph.edges:
        sources = [index[s] for s, _, _ in graph.edges]
        targets = [index[t] for _, t, _ in graph.edges]
        weights = [w for _, _, w in graph.edges]
        adjacency = sparse.csr_matrix(
            (weights, (targets, sources)), shape=(n, n), dtype=float
        )
    else:
        adjacency = sparse.csr_matrix((n, n), dtype=float)

    out_weight = np.asarray(adjacency.sum(axis=0)).ravel()
    dangling = out_weight == 0.0

    inv = np.zeros(n)
    inv[~dangling] = 1.0 / out_weight[~dangling]
    m = adjacency @ sparse.diags(inv)
    m = m.tolil()
    for j in np.flatnonzero(dangling):
        m[:, j] = 1.0 / n
    return m.tocsr()


def solve_pagerank(
    graph: Graph, config: PageRankConfig | None = None
) -> Result[PageRankResult, SolverError]:
    config = config or PageRankConfig()
    checked = graph.validate().bind(lambda g: _validate_config(config, len(g)))
    if isinstance(checked, Failure):
        return checked

    n = len(graph)
    m = transition_matrix(graph)
    if config.personalization is None:
        teleport = np.full(n, 1.0 / n)
    else:
        teleport = np.asarray(config.personalization, dtype=float)

    r = teleport.copy()
    history: list[float] = []
    converged = False
    iterations = 0
    for _ in range(config.max_iterations):
        iterations += 1
        r_new = config.damping * (m @ r) + (1 - config.damping) * teleport
        delta = float(np.abs(r_new - r).sum())
        history.append(delta)
        r = r_new
        if delta < config.tolerance:
            converged = True
            break

    r = r / r.sum()
    ranked = sorted(
        ((node, float(r[graph.index[node]])) for node in graph.nodes),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return Success(
        PageRankResult(
            scores=r,
            ranked=ranked,
            iterations=iterations,
            history=history,
            converged=converged,
        )
    )
