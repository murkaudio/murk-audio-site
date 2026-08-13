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

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Set

NON_OPPORTUNITY_SLUGS = [
    "grant-awards", "partnering-with-racc", "tips-on-preparing",
    "faq", "apply", "grant-admin-guide",
]
ADDITIONAL_OPPORTUNITY_PATHS = ["/current-racc-opportunities/"]

def discover_grant_urls(directory_url: str, html: str) -> List[str]:
    """
    Parses a directory/hub page and extracts likely individual grant
    opportunity pages, excluding news posts, nav, archives, and off-domain links.
    """
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(directory_url).netloc
    candidates: Set[str] = set()

    for link in soup.find_all("a", href=True):
        absolute_url = urljoin(directory_url, link["href"])
        parsed = urlparse(absolute_url)

        if parsed.netloc != base_domain:
            continue  # Block off-domain links (socials, portals)

        path = parsed.path.rstrip("/")

        # Force include specified priority paths
        if any(path == p.rstrip("/") for p in ADDITIONAL_OPPORTUNITY_PATHS):
            candidates.add(absolute_url)
            continue

        if "/grants/" not in path + "/":
            continue

        slug = path.split("/")[-1]
        if slug == "grants" or any(bad in slug for bad in NON_OPPORTUNITY_SLUGS):
            continue

        candidates.add(absolute_url)

    return sorted(candidates)

print("[+] Discovery pipeline script written and locked.")
