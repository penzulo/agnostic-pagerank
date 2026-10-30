"""Disk cache for crawled pages."""

import hashlib
import json
from pathlib import Path

from returns.io import impure_safe


class PageCache:
    def __init__(self, cache_dir: str | Path = ".crawl_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, url: str) -> Path:
        h = hashlib.sha256(url.encode()).hexdigest()
        return self.cache_dir / f"{h}.json"

    @impure_safe
    def get(self, url: str) -> str | None:
        path = self._key(url)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return data.get("content")
        except Exception:
            return None

    @impure_safe
    def set(self, url: str, content: str) -> bool:
        path = self._key(url)
        try:
            path.write_text(json.dumps({"url": url, "content": content}))
            return True
        except Exception:
            return False
