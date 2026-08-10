import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time

def fetch_grant_directory_html(url: str, timeout: int = 10) -> Optional[str]:
    """
    Safely fetch HTML from a target grant directory URL.
    Returns None on failure rather than raising, so the caller can skip
    this source and continue processing others.
    """
    headers = {
        "User-Agent": "MurkAudioGrantResearch/1.0 (admin@murk.audio)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[-] Fetch failed for {url}: {e}")
        return None

def extract_text_or_default(soup_element, selector: str, default: str = "") -> str:
    """
    Pulls text from a CSS selector, returns a default instead of raising
    if the element isn't found. Strips whitespace.
    """
    found = soup_element.select_one(selector)
    return found.get_text(strip=True) if found else default

def parse_grant_listing(card_html, selectors: Dict[str, str]) -> Dict[str, str]:
    """
    Parses a single grant 'card' block into the structured dict format.
    `selectors` maps field name -> CSS selector, customized per target site.
    """
    return {
        "title": extract_text_or_default(card_html, selectors.get("title", ""), default="Untitled Opportunity"),
        "description": extract_text_or_default(card_html, selectors.get("description", "")),
        "eligibility": extract_text_or_default(card_html, selectors.get("eligibility", "")),
        "deadline": extract_text_or_default(card_html, selectors.get("deadline", "")),
        "source_url": card_html.get("data-source-url", "")
    }

def run_external_grants_sweep(
    target_url: str,
    listing_selector: str,
    field_selectors: Dict[str, str],
    rate_limit_seconds: float = 1.0
) -> List[Dict[str, str]]:
    """
    Fetches a grant directory page and returns a list of structured
    opportunity dicts matching the validation pipeline's expected schema.
    """
    html = fetch_grant_directory_html(target_url)
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(listing_selector)

    if not cards:
        print(f"[-] No listing cards matched selector '{listing_selector}' at {target_url}. "
              f"Selector may be stale (site redesign) — flag for manual review.")
        return []

    results = []
    for card in cards:
        try:
            parsed = parse_grant_listing(card, field_selectors)
            if not parsed["title"] or parsed["title"] == "Untitled Opportunity":
                continue
            results.append(parsed)
        except Exception as e:
            print(f"[-] Failed to parse one card: {e}")
            continue

    time.sleep(rate_limit_seconds)
    return results

if __name__ == "__main__":
    racc_selectors = {
        "title": ".grant-card__title",
        "description": ".grant-card__description",
        "eligibility": ".grant-card__eligibility",
        "deadline": ".grant-card__deadline",
    }
    opportunities = run_external_grants_sweep(
        target_url="https://racc.org/grants",  
        listing_selector=".grant-card",
        field_selectors=racc_selectors,
    )
    print(f"Found {len(opportunities)} opportunities")
