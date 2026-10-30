"""SNAP adapter public API."""

from .errors import SnapError
from .loader import load_snap_edge_list

__all__ = ["SnapError", "load_snap_edge_list"]
