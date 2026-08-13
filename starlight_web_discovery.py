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

#!/usr/bin/env python3
"""
starlight_web_discovery.py
The Murk Audio LLC — Starlight Autonomous AI Agent Web Harvester (Syntax Patched)
Session: June 11, 2026
"""

import os
import sys
import json
import re
import time
import requests
import gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

# Structural System Configuration
SERVICE_ACCOUNT_PATH = os.path.expanduser("~/murk-runners/service_account.json")
SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_api_key():
    """Reads environment space, scanning ~/.zshrc backwards to enforce the newest key access."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    zshrc_path = os.path.expanduser("~/.zshrc")
    if os.path.exists(zshrc_path):
        with open(zshrc_path, "r") as f:
            lines = f.readlines()
        for line in reversed(lines):
            match = re.search(r'export\s+(?:GEMINI|GOOGLE)_API_KEY=["\']?([^"\']+)["\']?', line)
            if match:
                return match.group(1)
    return None

def calculate_safety_gate(date_str):
    """Parses crawled deadline variations and applies a standard 10-day safety buffer cushion."""
    try:
        cleaned_date = date_str.strip()
        for fmt in ('%B %d, %Y', '%m/%d/%Y', '%b %d, %Y', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(cleaned_date, fmt)
                return (dt - timedelta(days=10)).strftime('%-m/%-d/%Y')
            except ValueError:
                continue
        return "10 days prior to deadline"
    except Exception:
        return "10 days prior to deadline"

def main():
    print("=" * 70)
    print("🚀 STARLIGHT AUTONOMOUS AGENTIC DISCOVERY ENGINE — SEARCH INITIALIZATION")
    print("=" * 70)

    api_key = get_api_key()
    if not api_key:
        print("❌ Authentication Error: GEMINI_API_KEY could not be resolved from env.")
        sys.exit(1)

    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"❌ Configuration Error: Master service account token missing: {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)

    try:
        # Connect to worksheet and pull current records to feed exclusion mapping
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
        sheet = gspread.authorize(creds).open_by_key(SHEET_ID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        raw_names = ws.col_values(1)
        existing_names_set = {n.strip().lower() for n in raw_names if n.strip()}
        existing_names_list = ", ".join([f"'{n}'" for n in raw_names[1:] if n.strip()])
        print(f"  ——> Database Sync: Excluded {len(existing_names_set) - 1} existing tracks from research target window.")

        # Framing deep context agent instructions with explicit structural formatting directives
        prompt = f"""
        Search the live open web using Google Search to discover active grant opportunities, fellowships, media funds, or foundational endowments available in 2026.
        
        TARGET PROTOCOLS:
        - Must accept applications from independent audio production, fiction podcasts, audio drama, or digital narrative episodic media.
        - Must explicitly permit corporate entity applicants (like an LLC) or be open to creative teams without individual non-profit status.
        - Focus on National (US), Regional Pacific Northwest (Oregon/Washington), or open Global programs.
        
        CRITICAL REJECTION FILTERS:
        - Do NOT return generic book-author, poetry, or standard screenwriting grants unless they explicitly list audio/podcasting streams.
        - Do NOT return any of these specific grants, as they are ALREADY tracked in our database: [{existing_names_list}].
        
        OUTPUT FORMAT REQUIREMENTS:
        You must format your response strictly as a valid JSON array of objects. Wrap the data block cleanly in a markdown code fence block like this:
        ```json
        [
          {{
            "name": "Official Name",
            "funder": "Organization Name",
            "geo": "National or Regional",
            "entity_fit": "Yes",
            "status": "Open",
            "deadline": "August 15, 2026"
          }}
        ]
        ```
        Ensure fields align exactly with those structural keys. Do not omit deadlines.
        """

        print("  ——> Dispatching Starlight RAG Scout to Google Search Grounding networks...")
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + api_key
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "temperature": 0.2
            }
        }

        # Fault-Tolerant Network Loop with Exponential Backoff
        res_data = {}
        max_retries = 3
        delay = 10
        
        for attempt in range(max_retries):
            res = requests.post(url, headers=headers, json=payload, timeout=90)
            res_data = res.json()
            
            # Catch transient 503 server unavailability issues and retry
            if res.status_code == 503 or ('error' in res_data and res_data['error'].get('code') == 503):
                print(f"  ⚠️ Server capacity busy (503). Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2
                continue
            break

        if 'candidates' not in res_data:
            print("\n❌ API REJECTION: The endpoint returned a permanent execution fault.")
            print("=" * 70)
            print(json.dumps(res_data, indent=2))
            print("=" * 70)
            sys.exit(1)
        
        # Extract response text stream and sanitize markdown arrays safely via regex mapping
        raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
        
        json_match = re.search(r'\[\s*\{.*\}\s*\]', raw_text, re.DOTALL)
        if not json_match:
            print("❌ Parsing Failure: The model output could not be processed into an array.")
            print("-" * 70)
            print(raw_text)
            print("-" * 70)
            sys.exit(1)
            
        leads = json.loads(json_match.group(0))
        print(f"  ——> Target extraction successful. Analyzing {len(leads)} fresh candidate rows...")

        added_count = 0
        for lead in leads:
            name = lead.get('name', '').strip()
            if not name or name.lower() in existing_names_set:
                continue
                
            public_deadline = lead.get('deadline', 'Rolling')
            safety_gate = calculate_safety_gate(public_deadline)
            
            row_payload = [
                name,
                lead.get('funder', 'Unknown Source'),
                lead.get('geo', 'National'),
                lead.get('entity_fit', 'Yes'),
                lead.get('status', 'Open'),
                public_deadline,
                safety_gate
            ]
            
            ws.append_row(row_payload, value_input_option='USER_ENTERED')
            print(f"  |++ INGESTED UNMAPPED PROSPECT: '{name}' -> Buffer Internal Deadline: {safety_gate}")
            added_count += 1

        print("-" * 70)
        print(f"✅ SUCCESSFUL HARVEST: {added_count} brand-new LLC arts grant streams written to database!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Critical Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
