"""Adapter tests for URL normalization and basic crawler behavior."""

from agnostic_pagerank.adapters.web import CrawlConfig, WebCrawler, normalize_url
from agnostic_pagerank.adapters.web.normalize import is_html_content_type, same_domain


def test_normalize_strips_fragment_and_tracking_and_slash():
    url = "https://example.com/docs/page/?utm_source=test&x=1#section/"
    out = normalize_url(url)
    assert "utm_source" not in out
    assert "#" not in out
    assert out == "https://example.com/docs/page?x=1"


def test_same_domain():
    assert same_domain("https://example.com/foo", "example.com")
    assert not same_domain("https://other.com/foo", "example.com")


def test_is_html_content_type():
    assert is_html_content_type("text/html; charset=utf-8")
    assert is_html_content_type("application/xhtml+xml")
    assert is_html_content_type(None)


def test_crawler_respects_max_pages():
    # just ensure config is wired
    cfg = CrawlConfig(start_url="https://example.com", max_pages=10)
    crawler = WebCrawler(cfg)
    assert crawler.config.max_pages == 10
