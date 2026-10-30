"""SNAP edge-list loader errors."""

from enum import Enum, auto


class SnapError(Enum):
    FILE_NOT_FOUND = auto()
    PARSE_ERROR = auto()
    EMPTY_FILE = auto()
