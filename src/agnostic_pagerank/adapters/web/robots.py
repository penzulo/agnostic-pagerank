"""Robots.txt checking and polite crawling delays."""

import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from returns.io import impure_safe


class RobotsChecker:
    def __init__(self, user_agent: str = "agnostic-pagerank"):
        self.user_agent = user_agent
        self._parsers: dict[str, RobotFileParser] = {}

    @impure_safe
    def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        if base not in self._parsers:
            rp = RobotFileParser()
            rp.set_url(base)
            try:
                rp.read()
            except Exception:
                # if can't read robots.txt, be conservative but allow? typically allow if can't fetch
                rp = RobotFileParser()
            self._parsers[base] = rp
        return self._parsers[base].can_fetch(self.user_agent, url)


class PoliteDelay:
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self._last: float | None = None

    @impure_safe
    def wait(self) -> None:
        now = time.time()
        if self._last is not None:
            sleep_time = self.delay - (now - self._last)
            if sleep_time > 0:
                time.sleep(sleep_time)
        self._last = time.time()
        return None
