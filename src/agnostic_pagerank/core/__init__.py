"""Core solver: graph abstraction, transition matrix, power iteration."""

from .errors import SolverError
from .graph import Edge, Graph
from .solver import PageRankConfig, PageRankResult, solve_pagerank, transition_matrix

__all__ = [
    "Edge",
    "Graph",
    "PageRankConfig",
    "PageRankResult",
    "SolverError",
    "solve_pagerank",
    "transition_matrix",
]
