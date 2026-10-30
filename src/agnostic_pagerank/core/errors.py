"""Error states for the core solver. Never raised — carried in Result values."""

from enum import Enum, auto


class SolverError(Enum):
    EMPTY_GRAPH = auto()
    INVALID_DAMPING = auto()
    INVALID_TOLERANCE = auto()
    INVALID_MAX_ITERATIONS = auto()
    UNKNOWN_NODE_IN_EDGE = auto()
    INVALID_WEIGHT = auto()
    INVALID_PERSONALIZATION = auto()
