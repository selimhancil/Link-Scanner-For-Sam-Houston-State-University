"""
crawler.py: Core module for crawling university websites and detecting broken links.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Generator, List, Optional, Set, Tuple
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup
import requests

# Realistic browser User-Agent header to avoid firewall blocks
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# File extensions to ignore for crawling to conserve bandwidth and time
IGNORED_EXTENSIONS = (
    ".pdf", ".zip", ".tar", ".gz", ".rar", ".exe", ".dmg",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".css", ".js"
)

# Social media and bot-protected domains that produce false-positive errors
SOCIAL_DOMAINS = {
    "facebook.com", "fb.com", "fb.me",
    "instagram.com", "instagr.am",
    "twitter.com", "x.com", "t.co",
    "linkedin.com", "lnkd.in",
    "youtube.com", "youtu.be",
    "tiktok.com",
    "pinterest.com",
    "whatsapp.com", "wa.me",
    "telegram.org", "t.me",
    "spotify.com",
    "play.google.com", "apps.apple.com"
}


@dataclass
class BrokenLink:
    target_url: str
    status_code: Optional[int]
    error_reason: str
    is_internal: bool
    link_text: str
    first_found_on: str
    total_occurrences: int = 1
    referring_pages: List[str] = field(default_factory=list)


def normalize_url(base_url: str, link: str) -> Optional[str]:
    """
    Converts relative links to absolute URLs and strips fragment (#anchor) identifiers.
    Discards non-HTTP(S) schemes (mailto, tel, javascript, etc.).
    """
    if not link or not isinstance(link, str):
        return None

    link = link.strip()
    if not link or link.startswith(("#", "javascript:", "mailto:", "tel:", "data:", "whatsapp:")):
        return None

    try:
        absolute_url = urljoin(base_url, link)
        clean_url, _ = urldefrag(absolute_url)
        parsed = urlparse(clean_url)

        if parsed.scheme in ("http", "https"):
            return clean_url
    except Exception:
        return None

    return None


def get_base_domain(url: str) -> str:
    """Returns the base domain/netloc of a given URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if ":" in domain:
        domain = domain.split(":")[0]
    return domain


def is_social_domain(url: str) -> bool:
    """Checks whether the URL belongs to a known social network or bot-restricted platform."""
    domain = get_base_domain(url)
    for s in SOCIAL_DOMAINS:
        if domain == s or domain.endswith("." + s):
            return True
    return False


def is_same_domain(base_url: str, target_url: str, allow_subdomains: bool = True) -> bool:
    """
    Checks if target_url belongs to the same domain as base_url.
    If allow_subdomains=True, 'cs.univ.edu' and 'univ.edu' are considered matching.
    """
    base_netloc = get_base_domain(base_url)
    target_netloc = get_base_domain(target_url)

    if not target_netloc:
        return False

    if target_netloc == base_netloc:
        return True

    if allow_subdomains:
        if target_netloc.endswith("." + base_netloc):
            return True

    return False


def is_truly_broken(
    status_code: Optional[int],
    error_reason: Optional[str],
    is_internal: bool
) -> bool:
    """
    Determines if a link is genuinely broken:
    - 404 (Not Found) or 410 (Gone): Definitively broken.
    - 5xx (Server Error): Definitively broken.
    - External 401 (Unauthorized), 403 (Forbidden), 429 (Rate Limit):
      NOT broken links; these are bot/firewall protections or auth walls.
    - Network/DNS connection failures: Truly broken / unreachable.
    - Internal 4xx codes: Always flagged for administrative review.
    """
    if status_code in (404, 410):
        return True

    if status_code and 500 <= status_code <= 599:
        return True

    # External bot blocks (403, 401, 429) are NOT broken links
    if not is_internal and status_code in (401, 403, 429):
        return False

    # Connection failures (unreachable host)
    if error_reason in ("Connection Failed", "DNS Error", "Connection Timeout"):
        return True

    # Internal 400+ errors are relevant for site health
    if is_internal and status_code and status_code >= 400:
        return True

    return False


def check_link(
    url: str,
    session: requests.Session,
    timeout: int = 5
) -> Tuple[Optional[int], Optional[str]]:
    """
    Queries the status of a single URL.
    Attempts a lightweight HEAD request first. If HEAD fails or returns 4xx,
    it falls back to a streaming GET request to prevent false positives.
    Returns: (status_code, error_message)
    """
    try:
        response = session.head(url, timeout=timeout, allow_redirects=True)

        # Some servers reject HEAD requests with 400, 403, 404, or 405 but work with GET
        if response.status_code in (400, 403, 404, 405):
            response = session.get(url, timeout=timeout, stream=True, allow_redirects=True)

        if response.status_code == 404:
            return 404, "404 Not Found"
        elif response.status_code == 410:
            return 410, "410 Gone"
        elif response.status_code >= 500:
            return response.status_code, f"Server Error (HTTP {response.status_code})"
        elif response.status_code >= 400:
            return response.status_code, f"HTTP {response.status_code}"

        return response.status_code, None

    except requests.exceptions.SSLError:
        return None, "SSL Certificate Error"
    except requests.exceptions.ConnectionError:
        return None, "Connection Failed"
    except requests.exceptions.Timeout:
        return None, "Connection Timeout"
    except requests.exceptions.RequestException as e:
        return None, f"Request Error ({type(e).__name__})"


def extract_links_from_html(html_content: str, page_url: str) -> List[Tuple[str, str]]:
    """
    Extracts all <a> tags and anchor text from HTML content.
    Returns: List[(normalized_url, link_text)]
    """
    soup = BeautifulSoup(html_content, "html.parser")
    links: List[Tuple[str, str]] = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        normalized = normalize_url(page_url, href)
        if normalized:
            link_text = a_tag.get_text(strip=True) or "[No Anchor Text]"
            if len(link_text) > 60:
                link_text = link_text[:57] + "..."
            links.append((normalized, link_text))

    return links


def crawl_website(
    start_url: str,
    max_pages: int = 30,
    timeout: int = 5,
    allow_subdomains: bool = True,
    ignore_social: bool = True,
    scope: str = "all"  # 'all' or 'internal_only'
) -> Generator[Dict, None, List[BrokenLink]]:
    """
    Crawls website using BFS and yields events for real-time progress.
    De-duplicates broken links and filters bot-protected false positives.
    """
    visited_pages: Set[str] = set()
    checked_links_cache: Dict[str, Tuple[Optional[int], Optional[str]]] = {}
    broken_links_map: Dict[str, BrokenLink] = {}

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    clean_start = normalize_url(start_url, start_url)
    if not clean_start:
        yield {"type": "ERROR", "message": "Invalid starting URL. Ensure it starts with http:// or https://"}
        return []

    queue = deque([clean_start])
    visited_pages.add(clean_start)
    pages_scanned = 0

    yield {
        "type": "INIT",
        "start_url": clean_start,
        "max_pages": max_pages
    }

    while queue and pages_scanned < max_pages:
        current_page = queue.popleft()
        pages_scanned += 1

        yield {
            "type": "PAGE_START",
            "current_page": current_page,
            "pages_scanned": pages_scanned,
            "queue_size": len(queue),
            "broken_count": len(broken_links_map),
            "checked_count": len(checked_links_cache)
        }

        # Fetch page HTML
        try:
            resp = session.get(current_page, timeout=timeout)
            content_type = resp.headers.get("Content-Type", "")
            if resp.status_code >= 400 or "text/html" not in content_type:
                continue
            html_content = resp.text
        except Exception as e:
            yield {
                "type": "PAGE_FETCH_ERROR",
                "page": current_page,
                "error": str(e)
            }
            continue

        # Extract links
        extracted = extract_links_from_html(html_content, current_page)

        for target_url, link_text in extracted:
            is_internal = is_same_domain(clean_start, target_url, allow_subdomains)

            # Skip external links if internal scope selected
            if scope == "internal_only" and not is_internal:
                continue

            # Skip social platforms if filter enabled
            if ignore_social and is_social_domain(target_url):
                continue

            # Check cache
            if target_url in checked_links_cache:
                status_code, error_reason = checked_links_cache[target_url]
            else:
                status_code, error_reason = check_link(target_url, session, timeout=timeout)
                checked_links_cache[target_url] = (status_code, error_reason)

            # Validate if truly broken
            if is_truly_broken(status_code, error_reason, is_internal):
                if target_url in broken_links_map:
                    existing = broken_links_map[target_url]
                    existing.total_occurrences += 1
                    if current_page not in existing.referring_pages:
                        existing.referring_pages.append(current_page)
                else:
                    new_broken = BrokenLink(
                        target_url=target_url,
                        status_code=status_code,
                        error_reason=error_reason or f"HTTP {status_code}",
                        is_internal=is_internal,
                        link_text=link_text,
                        first_found_on=current_page,
                        total_occurrences=1,
                        referring_pages=[current_page]
                    )
                    broken_links_map[target_url] = new_broken
                    yield {
                        "type": "BROKEN_LINK",
                        "broken": new_broken,
                        "broken_count": len(broken_links_map)
                    }

            # Add internal pages to crawl queue
            if (
                is_internal
                and target_url not in visited_pages
                and not target_url.lower().endswith(IGNORED_EXTENSIONS)
            ):
                visited_pages.add(target_url)
                queue.append(target_url)

    yield {
        "type": "COMPLETED",
        "total_scanned_pages": pages_scanned,
        "total_checked_links": len(checked_links_cache),
        "total_broken_links": len(broken_links_map)
    }

    return list(broken_links_map.values())
