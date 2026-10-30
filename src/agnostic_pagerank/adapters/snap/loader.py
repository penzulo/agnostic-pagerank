"""Load SNAP-style edge lists into a Graph."""

from pathlib import Path

from returns.result import Failure, Result, Success

from agnostic_pagerank.core import Graph

from .errors import SnapError


def load_snap_edge_list(path: str | Path) -> Result[Graph, SnapError]:
    path = Path(path)
    if not path.exists():
        return Failure(SnapError.FILE_NOT_FOUND)
    try:
        lines = path.read_text().splitlines()
    except Exception:
        return Failure(SnapError.PARSE_ERROR)

    edges = []
    nodes_set = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            source = parts[0]
            target = parts[1]
        except Exception:
            continue
        # SNAP uses integer node ids; keep as strings for Graph
        edges.append((str(source), str(target), 1.0))
        nodes_set.add(str(source))
        nodes_set.add(str(target))
    if not edges:
        return Failure(SnapError.EMPTY_FILE)
    nodes = sorted(nodes_set)
    return Success(Graph(nodes=nodes, edges=edges))
