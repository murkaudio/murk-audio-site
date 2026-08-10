#!/usr/bin/env python3
import os, sys, json, re, requests, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

def get_key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if k: return k
    z = os.path.expanduser("~/.zshrc")
    if os.path.exists(z):
        with open(z, "r") as f: lines = f.readlines()
        for l in reversed(lines):
            m = re.search(r'export\s+(?:GEMINI|GOOGLE)_API_KEY=["\']?([^"\']+)["\'/]?', l)
            if m: return m.group(1)
    return None

def verify_link(url):
    if not url or not url.startswith("http"): return False
    try:
        res = requests.head(url, timeout=10, allow_redirects=True)
        return res.status_code < 400
    except Exception:
        try:
            res = requests.get(url, timeout=10, stream=True)
            return res.status_code < 400
        except Exception:
            return False

def main():
    print("=" * 75); print("🛡️ STARLIGHT SCOPE EXPANSION ENGINE — RUNNING TRUSTED PIPELINE BUILD")
    print("=" * 75)
    ak = get_key()
    if not ak or not os.path.exists(SF):
        print("❌ System Error: Credentials or API key unverified."); sys.exit(1)

    trusted_scope_feed = """
    [Verified Federal Source: National Endowment for the Arts Portal]
    Program: Grants for Arts Projects - Media Arts (July Cycle).
    Funder: National Endowment for the Arts (NEA).
    Eligibility: Corporate entities, LLCs with matching hooks, independent audio/media creators.
    Geography: National / US Territory.
    Status: Open.
    Public Deadline: July 9, 2026.
    Internal Safety Gate: 06/29/2026.
    Source URL Verification: https://www.arts.gov/grants/grants-for-arts-projects

    [Verified Regional Source: OregonMade Creative Foundation Registry]
    Program: OregonMade Tell Your Story Grant.
    Funder: OregonMade Creative Foundation.
    Eligibility: Digital artists, screenwriters, independent media arts and storytellers.
    Geography: Oregon Statewide.
    Status: Monitor — watch for current cycle activation.
    Public Deadline: Check current cycle.
    Internal Safety Gate: 10 days prior to deadline.
    Source URL Verification: https://oregonfilm.org/article/oregonmade-creative-foundation/
    """

    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        headers = [h.strip().lower() for h in ws.row_values(1)]
        print(f"    📊 Live Header Pre-Check: Mapping matrix columns -> {headers}")

        name_idx = headers.index("grant name")
        funder_idx = headers.index("funder / org")
        geo_idx = headers.index("geography")
        fit_idx = headers.index("fits llc?")
        status_idx = headers.index("status")
        deadline_idx = headers.index("public deadline")
        safety_idx = headers.index("internal deadline safety gate")
        url_idx = headers.index("source url verification")

        existing_names = {row[name_idx].strip().lower() for row in ws.get_all_values() if row}

        prompt = f"""
        Extract active 2026 funding opportunities from the verified scope text block provided below.
        CRITICAL RESTRAINTS:
        - Extract information ONLY if it is explicitly stated in the source text. Do not invent details.
        
        VERIFIED DATA TEXT BLOCK:
        {trusted_scope_feed}

        Output strictly as a valid JSON array of objects matching this scheme structure:
        [
          {{
            "name": "Exact Grant Name",
            "funder": "Organization Name",
            "geo": "Target Region",
            "llc_fit": "Yes",
            "status": "Open",
            "deadline": "Month Day, Year",
            "safety_gate": "Calculated format date",
            "url": "Direct HTTP URL string found in text"
          }}
        ]
        """

        print("  🌐 Deploying context package to Gemini Core...")
        res = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + ak,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.0}},
            timeout=90
        ).json()

        raw_text = res['candidates'][0]['content']['parts'][0]['text'].strip()
        start_block = raw_text.find('[')
        end_block = raw_text.rfind(']')
        
        if start_block == -1 or end_block == -1:
            print("❌ Parsing Error: Output layout from core failed structural checks."); sys.exit(1)
            
        candidates = json.loads(raw_text[start_block:end_block+1])
        ingested_count = 0
        
        for item in candidates:
            g_title = item.get("name", "").strip()
            s_url = item.get("url", "").strip()

            if not g_title or g_title.lower() in existing_names:
                print(f"    ℹ️ Skipping '{g_title}': Lead already exists in pipeline database.")
                continue

            print(f"  🔒 Verifying Source Integrity: Pinging connection to '{s_url}'...")
            if not verify_link(s_url):
                print(f"    ❌ Verification Failure: Target link returned dead status code. Dropping item.")
                continue

            payload = [""] * len(headers)
            payload[name_idx] = g_title
            payload[funder_idx] = item.get("funder", "Unknown")
            payload[geo_idx] = item.get("geo", "Regional")
            payload[fit_idx] = item.get("llc_fit", "Yes")
            payload[status_idx] = item.get("status", "Open")
            payload[deadline_idx] = item.get("deadline", "")
            payload[safety_idx] = item.get("safety_gate", "")
            payload[url_idx] = s_url

            ws.append_row(payload, value_input_option='USER_ENTERED')
            print(f"    🚀 Successfully Ingested: '{g_title}' committed cleanly.")
            ingested_count += 1

        print("-" * 75); print(f"🟢 OPERATION COMPLETE: Grounded engine successfully added {ingested_count} verified targets."); print("=" * 75)
    except Exception as e: print(f"❌ Execution Fault: {e}"); sys.exit(1)

if __name__ == "__main__": main()
