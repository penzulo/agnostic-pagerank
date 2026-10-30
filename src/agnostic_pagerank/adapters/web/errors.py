"""Web adapter error states. IO failures returned as values via IOResult."""

from enum import Enum, auto


class WebError(Enum):
    NETWORK_ERROR = auto()
    ROBOTS_DISALLOWED = auto()
    INVALID_URL = auto()
    NON_HTML = auto()
    PARSE_ERROR = auto()
    CACHE_ERROR = auto()
    HTTP_ERROR = auto()
    PAGE_CAP_REACHED = auto()
