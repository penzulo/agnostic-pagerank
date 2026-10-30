"""Dataset-agnostic graph abstraction: nodes plus weighted directed edges."""

from dataclasses import dataclass, field

from returns.result import Failure, Result, Success

from .errors import SolverError

Edge = tuple[str, str, float]


@dataclass
class Graph:
    nodes: list[str]
    edges: list[Edge] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._index = {node: i for i, node in enumerate(self.nodes)}

    @property
    def index(self) -> dict[str, int]:
        return self._index

    def __len__(self) -> int:
        return len(self.nodes)

    def validate(self) -> Result[Graph, SolverError]:
        if not self.nodes:
            return Failure(SolverError.EMPTY_GRAPH)
        for source, target, weight in self.edges:
            if source not in self._index or target not in self._index:
                return Failure(SolverError.UNKNOWN_NODE_IN_EDGE)
            if weight < 0:
                return Failure(SolverError.INVALID_WEIGHT)
        return Success(self)
