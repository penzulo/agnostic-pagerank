"""URL normalization and domain checks for web crawling."""

from urllib.parse import urljoin, urlparse, urlunparse

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "ref",
}


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    # filter tracking params
    params = []
    if parsed.query:
        for part in parsed.query.split("&"):
            if not part:
                continue
            key = part.split("=", 1)[0] if "=" in part else part
            if key in TRACKING_PARAMS:
                continue
            params.append(part)
    new_query = "&".join(params)
    # remove trailing slash except for root path
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    if path == "":
        path = "/"
    normalized = urlunparse(
        (parsed.scheme, parsed.netloc, path, parsed.params, new_query, "")
    )
    return normalized


def same_domain(url: str, base_netloc: str) -> bool:
    return urlparse(url).netloc == base_netloc


def is_html_content_type(content_type: str | None) -> bool:
    if not content_type:
        return True
    ct = content_type.lower()
    if "text/html" in ct:
        return True
    return "application/xhtml" in ct


def to_absolute(base_url: str, href: str) -> str | None:
    try:
        joined = urljoin(base_url, href)
        parsed = urlparse(joined)
        if parsed.scheme not in ("http", "https"):
            return None
        return joined
    except Exception:
        return None
