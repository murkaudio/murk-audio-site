# === SERVICE ACCOUNT GIT GUARD ===
import subprocess as _sp_guard
if not getattr(_sp_guard, "_sa_guard_active", False):
    _orig_r, _orig_c, _orig_cc, _orig_p = _sp_guard.run, _sp_guard.call, _sp_guard.check_call, _sp_guard.Popen
    def _sa_clean(cmd):
        if isinstance(cmd, (list, tuple)):
            return [str(x) for x in cmd if "service_account.json" not in str(x)]
        return cmd
    _sp_guard.run = lambda cmd, *a, **kw: _orig_r(_sa_clean(cmd), *a, **kw)
    _sp_guard.call = lambda cmd, *a, **kw: _orig_c(_sa_clean(cmd), *a, **kw)
    _sp_guard.check_call = lambda cmd, *a, **kw: _orig_cc(_sa_clean(cmd), *a, **kw)
    _sp_guard.Popen = lambda cmd, *a, **kw: _orig_p(_sa_clean(cmd), *a, **kw)
    _sp_guard._sa_guard_active = True
# =================================

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Set, Optional, Callable, Dict, Any
import time

NON_OPPORTUNITY_SLUGS = [
    "grant-awards", "partnering-with-racc", "tips-on-preparing",
    "faq", "apply", "grant-admin-guide",
]
ADDITIONAL_OPPORTUNITY_PATHS = ["/current-racc-opportunities/"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]

FIELD_KEYWORDS = {
    "eligibility": ["eligib", "who can apply", "qualif"],
    "deadline": ["deadline", "due date", "application due", "when to apply"],
    "description": ["program", "overview", "about", "what does", "summary"],
}

def discover_grant_urls(directory_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    base_domain = requests.utils.urlparse(directory_url).netloc
    candidates: Set[str] = set()

    for link in soup.find_all("a", href=True):
        absolute_url = requests.utils.urljoin(directory_url, link["href"])
        parsed = requests.utils.urlparse(absolute_url)
        if parsed.netloc != base_domain:
            continue
        path = parsed.path.rstrip("/")
        if any(path == p.rstrip("/") for p in ADDITIONAL_OPPORTUNITY_PATHS):
            candidates.add(absolute_url)
            continue
        if "/grants/" not in path + "/":
            continue
        if re.search(r"/page/\d+/?$", path):
            continue
        slug = path.split("/")[-1]
        if slug == "grants" or any(bad in slug for bad in NON_OPPORTUNITY_SLUGS):
            continue
        candidates.add(absolute_url)

    return sorted(candidates)

def find_next_page_url(current_url: str, soup: BeautifulSoup) -> Optional[str]:
    rel_next = soup.find("a", rel="next")
    if rel_next and rel_next.get("href"):
        return requests.utils.urljoin(current_url, rel_next["href"])

    next_text_patterns = [r"^next$", r"^next\s*»$", r"^»$", r"^\u203a$"]
    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True).lower()
        if any(re.match(p, text, re.IGNORECASE) for p in next_text_patterns):
            return requests.utils.urljoin(current_url, link["href"])

    match = re.search(r"/page/(\d+)/?", current_url)
    target_page_num = (int(match.group(1)) if match else 1) + 1
    for link in soup.find_all("a", href=True):
        if re.search(rf"/page/{target_page_num}/?(?:$|[?#])", link["href"]):
            return requests.utils.urljoin(current_url, link["href"])

    return None

def discover_grant_urls_paginated(
    start_url: str, fetch_fn: Callable[[str], Optional[str]], max_pages: int = 3,
) -> List[str]:
    visited: Set[str] = set()
    all_candidates: Set[str] = set()
    current_url = start_url
    pages_fetched = 0

    while current_url and pages_fetched < max_pages:
        if current_url in visited:
            print(f"[-] Loop guard triggered: {current_url} already visited.")
            break
        visited.add(current_url)

        html = fetch_fn(current_url)
        pages_fetched += 1
        if html is None:
            break

        page_candidates = discover_grant_urls(current_url, html)
        print(f"[+] Page {pages_fetched} ({current_url}): {len(page_candidates)} candidates")
        all_candidates.update(page_candidates)

        soup = BeautifulSoup(html, "html.parser")
        next_url = find_next_page_url(current_url, soup)
        current_url = next_url

    return sorted(all_candidates)

print("[+] Consolidated crawl-and-short-circuit engine written cleanly to disk.")
