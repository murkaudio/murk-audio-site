import os
import gspread
from google.oauth2.service_account import Credentials

# 🔐 1. Authentication and Sheet Initialization
SERVICE_ACCOUNT_FILE = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"

# Targets to switch to hard KILL status
KILL_TARGETS = {
    "PROD-294": "KILL | Invalid Data — DAV provides top-tier veteran benefits advocacy but does not administer small business or creative production grant capital.",
    "PROD-295": "KILL | Schema Match Failure — FCEF exclusively provides educational scholarships (GED to PhD). They do not fund commercial LLCs or media infrastructure.",
    "PROD-331": "KILL | Vehicle Match Failure — Hivers & Strivers is an equity-exchange angel investor network, strictly violating non-dilutive framework mandates."
}

# Targets to shift to dark/inactive PARK status due to 2026 chronological windows
PARK_TARGETS = {
    "PROD-265": "PARK | Closed Cycle Consolidation — LOI window passed Feb 2026. Consolidating workflow metrics and shifting track to match January 2027 cycle opening.",
    "PROD-269": "PARK | Closed Cycle — Current funding wave is closed. Next baseline LOI cycle initialization does not open until January 2027.",
    "PROD-271": "PARK | Closed Cycle — Portal verified dark. Core platform messaging confirms next active project grant window is entirely closed until Fall 2026.",
    "PROD-272": "PARK | Closed Cycle — FY26-27 cycle locked. Multi-axis short-circuit engaged until Fall 2026 operational windows reopen.",
    "PROD-288": "PARK | Inactive Cohort — June 15, 2026 cohort winners announced. Ingestion pipelines shifted to park status until next micro-grant wave drops."
}

def run_sheet_triage():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[-] Fatal Error: Gspread credential file missing at {SERVICE_ACCOUNT_FILE}")
        return

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    
    print(f"[+] Connected to Google API. Opening primary tab (index 0)...")
    # Using get_worksheet(0) ensures we pull the active first tab regardless of its name string
    sheet = gc.open_by_key(SPREADSHEET_ID).get_worksheet(0)
    
    # 📑 2. Map Column Headers Dynamically
    headers = sheet.row_values(1)
    
    try:
        id_col_idx = next(i for i, h in enumerate(headers, 1) if "id" in h.lower() or "prod" in h.lower())
        status_col_idx = next(i for i, h in enumerate(headers, 1) if "status" in h.lower() or "verdict" in h.lower())
        notes_col_idx = next(i for i, h in enumerate(headers, 1) if "note" in h.lower() or "context" in h.lower())
    except StopIteration:
        print("[-] Mapping Failure: Could not uniquely pinpoint required structural columns (ID, Status, or Notes) from your header row.")
        return

    print(f"[+] Layout mapped -> ID Col: {id_col_idx}, Status Col: {status_col_idx}, Notes Col: {notes_col_idx}")

    # 🚀 3. Fetch Data Matrix & Apply Changes
    all_rows = sheet.get_all_values()
    
    print("[+] Scanning rows for targeted corrections...")
    for row_num, row_data in enumerate(all_rows[1:], start=2):
        if len(row_data) < id_col_idx:
            continue
            
        task_id = row_data[id_col_idx - 1].strip()
        
        if task_id in KILL_TARGETS:
            sheet.update_cell(row_num, status_col_idx, "KILL")
            sheet.update_cell(row_num, notes_col_idx, KILL_TARGETS[task_id])
            print(f"[✔] Row {row_num}: Successfully updated {task_id} to hard KILL status.")
            
        elif task_id in PARK_TARGETS:
            sheet.update_cell(row_num, status_col_idx, "PARK")
            sheet.update_cell(row_num, notes_col_idx, PARK_TARGETS[task_id])
            print(f"[✔] Row {row_num}: Successfully shifted {task_id} to PARK status.")

    print("\n[+] Bulk data ledger triage pass complete.")

if __name__ == "__main__":
    run_sheet_triage()
