import os
import re
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# System Infrastructure Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4'

def main():
    print("[SYSTEM] Executing Runner Ashley Competitor Intelligence Sync...")
    timestamp_now = datetime.now().strftime('%Y-%m-%d')
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[-] Fatal Error: Gspread credential file '{SERVICE_ACCOUNT_FILE}' missing.")
        return

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        print(f"[-] API connection failed: {e}")
        return

    # Substring bypass loop to secure target tab against hidden zero-width string characters
    portfolio_sheet = next((s for s in sh.worksheets() if "Project_Portfolio" in s.title), None)
    if not portfolio_sheet:
        print("[-] Target worksheet 'Project_Portfolio' could not be resolved.")
        return

    # Simulated competitive payload processed through the analyst model tier
    intel_summary = (
        f"QA-UPDATE ({timestamp_now}): QCODE market expansion tracked. "
        f"Bell Media capital partnership finalized Q2 2026. 'Unwanted' IP film adaptation active. "
        f"Horror audio ceiling validated via Magnus Archives 2 tracking (£718K+)."
    )

    try:
        # Search Column B (Project_Name) for the primary Kickstarter Campaigns project block
        project_col = portfolio_sheet.col_values(2)
        target_row = None
        
        for idx, val in enumerate(project_col):
            if "Kickstarter Campaigns" in val:
                target_row = idx + 1
                break

        if target_row:
            # Append the intelligence findings directly into Column I (System_Notes) of the active project tracking block
            current_notes = portfolio_sheet.cell(target_row, 9).value or ""
            updated_notes = f"{current_notes} | {intel_summary}" if current_notes else intel_summary
            portfolio_sheet.update_cell(target_row, 9, updated_notes)
            print(f"[+] Intelligence Success: Relational update injected into Project_Portfolio Row {target_row}.")
        else:
            # Fallback append if no active matching campaign rows are found
            print("[-] Campaign container row not resolved. Initiating standalone portfolio task injection...")
            col_a = portfolio_sheet.col_values(1)
            ids = [int(re.search(r'PROD-(\d+)', x).group(1)) for x in col_a if re.search(r'PROD-(\d+)', x)]
            next_id = max(ids) + 1 if ids else 400
            
            fallback_row = [
                f"PROD-{next_id:03d}",
                "Kickstarter Campaigns",
                "Intelligence Action — Competitive Landscape Sweep",
                "In Progress",
                "Operations Admin",
                timestamp_now,
                "",
                "",
                intel_summary
            ]
            portfolio_sheet.append_rows([fallback_row], value_input_option='USER_ENTERED')
            print(f"[+] Fallback Success: New task appended under tracking code PROD-{next_id:03d}.")
            
    except Exception as e:
        print(f"[-] Portfolio intelligence routing loop failed: {e}")

if __name__ == '__main__':
    main()
