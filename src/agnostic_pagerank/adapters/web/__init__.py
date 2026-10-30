"""Web adapter public API."""

from .cache import PageCache
from .crawler import CrawlConfig, CrawlResult, WebCrawler
from .errors import WebError
from .normalize import is_html_content_type, normalize_url, same_domain, to_absolute
from .robots import PoliteDelay, RobotsChecker

__all__ = [
    "CrawlConfig",
    "CrawlResult",
    "PageCache",
    "PoliteDelay",
    "RobotsChecker",
    "WebCrawler",
    "WebError",
    "is_html_content_type",
    "normalize_url",
    "same_domain",
    "to_absolute",
]
