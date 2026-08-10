#!/usr/bin/env python3
import os, sys, time, datetime, requests, gspread
from bs4 import BeautifulSoup

SERVICE_ACCOUNT = os.path.expanduser("~/murk-runners/service_account.json")
SPREADSHEET_ID  = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"
STAGING_TAB     = "Staging_Grants"
PORTFOLIO_TAB   = "\u2060Project_Portfolio"
LOG_DIR         = os.path.expanduser("~/murk-runners/logs")
TODAY           = datetime.date.today().isoformat()

MURK_KEYWORDS = ["audio","podcast","radio","sound","media","storytelling","digital","immersive","spatial","fiction","drama","narrative","veteran","disabled","disability","oregon","portland","pacific northwest","arts","culture","creative","independent","film","individual artist","fiscal sponsor","nonprofit"]

KNOWN_KILLS = ["hayama","paul g. allen","marie lamfrom","autzen","mcm fund","miller foundation","gottlieb","anonymous was a woman","hivers","patriot boot camp","bunker labs","pollination project","google for startups","microsoft for startups","loghaven","boots to business"]

CURATED_SOURCES = [
    # Federal
    ("Grants.gov NEA/NEH","https://apply07.grants.gov/grantsws/rest/opportunities/search/?oppStatuses=forecasted%2Cposted&agencies=NEA%2CNEH&rows=25&sortBy=openDate%7Cdesc","grants_gov"),
    ("Grants.gov Audio Drama","https://apply07.grants.gov/grantsws/rest/opportunities/search/?oppStatuses=forecasted%2Cposted&keyword=audio+drama&rows=25&sortBy=openDate%7Cdesc","grants_gov"),
    ("Grants.gov Podcast","https://apply07.grants.gov/grantsws/rest/opportunities/search/?oppStatuses=forecasted%2Cposted&keyword=podcast&rows=25&sortBy=openDate%7Cdesc","grants_gov"),
    ("Grants.gov Veteran Arts","https://apply07.grants.gov/grantsws/rest/opportunities/search/?oppStatuses=forecasted%2Cposted&keyword=veteran+arts&rows=25&sortBy=openDate%7Cdesc","grants_gov"),
    # Oregon Regional
    ("Oregon Arts Commission","https://www.oregonartscommission.org/grants","html"),
    ("OCF Creative Heights","https://oregoncf.org/grants-and-scholarships/grants/creative-heights","html"),
    ("OCF Community Grants","https://oregoncf.org/grants-and-scholarships/grants/community-grant-program","html"),
    ("RACC Portland","https://racc.org/grants-services/project-grants/","html"),
    ("Multnomah County Cultural Coalition","https://www.multco.us/multnomah-county/community-cultural-coalition","html"),
    # PNW Regional
    ("Artist Trust GAP Washington","https://artisttrust.org/grants/grants-for-artist-projects/","html"),
    ("Artist Trust TWGF Fellowship","https://artisttrust.org/grants/twgf/","html"),
    ("Seattle smART Ventures","https://www.seattle.gov/arts/programs/grants/smart-ventures","html"),
    # National Arts
    ("NEH Media Projects","https://www.neh.gov/program/media-projects","html"),
    ("NEA Media Arts","https://www.arts.gov/grants/grants-for-arts-projects/media-arts","html"),
    # NEA Creative Writing REMOVED — dead URL arts.gov/grants/literature returns 404
    # Correct URL is arts.gov/grants/literature/creative-writing-fellowships but program
    # is between cycles — re-add when next cycle opens
    ("Foundation for Contemporary Arts","https://www.foundationforcontemporaryarts.org/grants/emergency-grants/","html"),
    ("Awesome Foundation Portland","https://www.awesomefoundation.org/en/chapters/portland","html"),
    ("Awesome Foundation Seattle","https://www.awesomefoundation.org/en/chapters/seattle","html"),
    ("Creative Capital Open Call","https://creative-capital.org/creative-capital-award/","html"),
    ("NYFA Grants","https://www.nyfa.org/grants/","html"),
    ("Sundance Institute","https://www.sundance.org/apply/","html"),
    ("John Templeton Foundation Podcast","https://www.templeton.org/funding-areas/podcast-grants","html"),
    # Audio / Podcast / Drama Specific
    ("PodGround","https://www.podground.com/grants","html"),
    ("Audio Verse Awards","https://www.audioverse.org/english/content/awards.html","html"),
    ("Austin Film Festival Podcast","https://austinfilmfestival.com/submit/podcast-competition/","html"),
    ("Tribeca Podcasts","https://tribecafilm.com/programs/podcast","html"),
    ("MORNINGFYI People Fund","https://morning.fyi/people-fund","html"),
    ("Literary Arts Fund","https://literaryartsfund.submittable.com/submit","html"),
    ("Fund for Investigative Journalism","https://investigate.submittable.com/submit","html"),
    # Disability Arts
    ("Inevitable Foundation","https://www.inevitable.foundation/elevate","html"),
    ("Apothetae Playwriting Fellowship","https://thelarktheatre.org/apothetae","html"),
    # Veteran
    ("Second Service Foundation","https://www.secondservicefoundation.org/mec","html"),
    ("Warrior Rising","https://www.warriorrising.org/apply","html"),
    ("StreetShares Foundation","https://streetsharesfoundation.com/programs/","html"),
    # Tadlock REMOVED — requires 2-100 W-2 employees; Murk is sole-member LLC, hard disqualifier
    # Seattle CityArtist REMOVED — requires Seattle residency; James is Portland-based
    # NEA Media Arts REMOVED — bot-blocks scraper (rate limit 403)
    # Submittable REMOVED — auth wall returns homepage only
    # Residencies
    ("MacDowell","https://www.macdowell.org/apply","html"),
    ("James Castle House","https://jamescastlehouse.org/residency","html"),
    ("PLAYA Summer Lake","https://playasummerlake.org/residency/","html"),
    ("Yaddo Residency","https://www.yaddo.org/apply/","html"),
    ("Ucross Residency","https://ucrossfoundation.submittable.com/submit","html"),
    # Discovery / Aggregators
    ("Collins Foundation","https://www.collinsfoundation.org/apply/","html"),
    ("All Hear Audio Opportunities","https://allhear.substack.com","html"),
    ("Colossal Monthly Opportunities","https://www.thisiscolossal.com/opportunities/","html"),
    ("PEN America Fellowships","https://pen.org/programs/","html"),
]

HEADERS = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def connect_sheet():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT)
    return gc.open_by_key(SPREADSHEET_ID)

def ensure_staging_tab(sheet):
    titles = [ws.title for ws in sheet.worksheets()]
    if STAGING_TAB not in titles:
        ws = sheet.add_worksheet(title=STAGING_TAB, rows=500, cols=10)
        ws.append_row(["Grant_Name","Funder","Deadline","Source_URL","Geography","Award_Range","Notes","Scrape_Date","Dupe_Status","Marie_Flag"], value_input_option="RAW")
        print("  Created Staging_Grants tab.")
    return sheet.worksheet(STAGING_TAB)

def get_portfolio_names(sheet):
    try:
        ws = sheet.worksheet(PORTFOLIO_TAB)
        records = ws.get_all_values()
        names = set()
        for row in records[1:]:
            if len(row) > 2:
                names.add(row[1].lower().strip())
                names.add(row[2].lower().strip())
        return names
    except Exception as e:
        print(f"  Warning portfolio fetch: {e}")
        return set()

def get_staging_names(ws):
    try:
        records = ws.get_all_values()
        return set(row[0].lower().strip() for row in records[1:] if row)
    except:
        return set()

def is_qualified(name, notes, funder=""):
    text = f"{name} {notes} {funder}".lower()
    for kill in KNOWN_KILLS:
        if kill in text:
            return False, f"KNOWN_KILL:{kill}"
    for kw in MURK_KEYWORDS:
        if kw.lower() in text:
            return True, f"KEYWORD:{kw}"
    return False, "NO_MATCH"

def is_dupe(name, portfolio_names, staging_names):
    n = name.lower().strip()
    for existing in portfolio_names:
        n_words = set(n.split())
        e_words = set(existing.split())
        if len(n_words) > 0 and len(n_words & e_words) / len(n_words) >= 0.6:
            return True
    return n in staging_names

def scrape_grants_gov(url, source_name):
    candidates = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        for opp in data.get("oppHits", []):
            candidates.append({
                "name": opp.get("title","").strip(),
                "funder": opp.get("agencyName","").strip(),
                "deadline": opp.get("closeDate","TBD"),
                "url": f"https://www.grants.gov/search-results-detail/{opp.get('id','')}",
                "award": str(opp.get("awardCeiling","TBD")),
                "notes": (opp.get("synopsis","") or "")[:200],
                "geo": "National"
            })
    except Exception as e:
        print(f"  Warning grants.gov: {e}")
    return candidates

def scrape_html(url, source_name):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["nav","footer","script","style","header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return [{"name":f"[RAW] {source_name}","funder":source_name,"deadline":"VERIFY","url":url,"award":"VERIFY","notes":text[:400],"geo":"VERIFY"}]
    except Exception as e:
        print(f"  Warning html ({source_name}): {e}")
        return []

def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    print("="*60)
    print(f"MARIE SCRAPER — {TODAY} — RUN START")
    print("="*60)
    try:
        sheet = connect_sheet()
        print("  Connected: Murk Ops")
    except Exception as e:
        print(f"  FAILED: {e}"); sys.exit(1)

    staging_ws = ensure_staging_tab(sheet)
    portfolio_names = get_portfolio_names(sheet)
    staging_names = get_staging_names(staging_ws)
    print(f"  Portfolio: {len(portfolio_names)} | Staging: {len(staging_names)}")

    staging_ws.append_row(["---",f"SCRAPE RUN: {TODAY}","---","---","---","---","---",TODAY,"---","UNVERIFIED"], value_input_option="RAW")

    print("\nScraping...")
    all_candidates = []
    for source_name, url, scrape_type in CURATED_SOURCES:
        print(f"  {source_name}")
        if scrape_type == "grants_gov":
            results = scrape_grants_gov(url, source_name)
        else:
            results = scrape_html(url, source_name)
        all_candidates.extend(results)
        time.sleep(2)

    print(f"\n  Raw candidates: {len(all_candidates)}")
    written = killed = dupes = 0

    for c in all_candidates:
        if is_dupe(c["name"], portfolio_names, staging_names):
            dupes += 1
            continue
        qualified, reason = is_qualified(c["name"], c["notes"], c["funder"])
        if not qualified:
            killed += 1
            continue
        staging_ws.append_row([
            c["name"], c["funder"], c["deadline"], c["url"],
            c.get("geo","VERIFY"), c.get("award","VERIFY"),
            c["notes"][:300], TODAY, "NEEDS_REVIEW", reason
        ], value_input_option="RAW")
        staging_names.add(c["name"].lower().strip())
        print(f"  STAGED: {c['name'][:55]}")
        written += 1
        time.sleep(0.5)

    print("\n"+"="*60)
    print(f"DONE — Written: {written} | Dupes: {dupes} | Killed: {killed}")
    print("="*60)

if __name__ == "__main__":
    main()
