"""BFS crawler that stays within one domain, respects robots.txt, deduplicates URLs."""

import csv
from collections import deque
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from returns.io import impure_safe

from .cache import PageCache
from .normalize import is_html_content_type, normalize_url, same_domain, to_absolute
from .robots import PoliteDelay, RobotsChecker


@dataclass
class CrawlConfig:
    start_url: str
    max_pages: int = 500
    delay: float = 1.0
    user_agent: str = "agnostic-pagerank"
    cache_dir: str = ".crawl_cache"
    skip_non_html: bool = True


@dataclass
class CrawlResult:
    edges: list[tuple[str, str]]
    pages: list[str]


class WebCrawler:
    def __init__(self, config: CrawlConfig):
        self.config = config
        self.base_netloc = urlparse(config.start_url).netloc
        self.robots = RobotsChecker(config.user_agent)
        self.delay = PoliteDelay(config.delay)
        self.cache = PageCache(config.cache_dir)

    @impure_safe
    def fetch(self, url: str) -> tuple[str, str] | None:
        # returns (content_type, content)
        headers = {"User-Agent": self.config.user_agent}
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        return resp.headers.get("Content-Type", ""), resp.text

    def crawl(self) -> CrawlResult:
        start = normalize_url(self.config.start_url)
        visited: set[str] = set()
        queue: deque[str] = deque([start])
        edges: list[tuple[str, str]] = []
        pages: list[str] = []

        while queue and len(visited) < self.config.max_pages:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            pages.append(current)

            # check robots
            if not self.robots.allowed(current).unwrap():
                continue
            self.delay.wait().unwrap()

            # try cache first
            cached = self.cache.get(current).unwrap()
            if cached is not None:
                content = cached
                content_type = "text/html"
            else:
                try:
                    fetched = self.fetch(current)
                    if fetched is None:
                        continue
                    content_type, content = fetched
                    if self.config.skip_non_html and not is_html_content_type(
                        content_type
                    ):
                        continue
                    self.cache.set(current, content).unwrap()
                except Exception:
                    continue

            soup = BeautifulSoup(content, "html.parser")
            for tag in soup.find_all("a", href=True):
                href = tag["href"]
                absolute = to_absolute(current, href)
                if absolute is None:
                    continue
                normalized = normalize_url(absolute)
                if not same_domain(normalized, self.base_netloc):
                    continue
                if normalized in visited:
                    edges.append((current, normalized))
                    continue
                edges.append((current, normalized))
                if normalized not in visited and len(visited) < self.config.max_pages:
                    queue.append(normalized)

        return CrawlResult(edges=edges, pages=pages)

    def export_csv(self, path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["source", "target"])
            for source, target in self.crawl().edges:
                writer.writerow([source, target])
