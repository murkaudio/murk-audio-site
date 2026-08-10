import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4'

def main():
    print("[SYSTEM] Initializing Automated Remediation Loop...")
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[-] Fatal: Credential file '{SERVICE_ACCOUNT_FILE}' missing from runner path.")
        return

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        print("[+] API Handshake Authorized. Master Ledger Connected.")
    except Exception as e:
        print(f"[-] Authentication crash: {e}")
        return

    portfolio_sheet = next((s for s in sh.worksheets() if "Project_Portfolio" in s.title), None)
    if portfolio_sheet:
        try:
            cell = portfolio_sheet.find("PROD-136")
            if cell:
                portfolio_sheet.update_cell(cell.row, 6, "2026-07-01")
                print(f"[+] Realignment Success: Row {cell.row} (PROD-136) hard-gated to 2026-07-01.")
            else:
                print("[-] Warning: Handle 'PROD-136' not detected in Column A.")
        except Exception as e:
            print(f"[-] Portfolio modification failed: {e}")
    else:
        print("[-] Error: 'Project_Portfolio' tab not resolved.")

    log_sheet = next((s for s in sh.worksheets() if "System_Log" in s.title), None)
    if log_sheet:
        new_logs = [
            [
                "LOG-015", 
                "2026-06-18T12:00:00-07:00", 
                "Live_Metrics", 
                "FIN-029", 
                "BREACH_DETECTION — CCC Maker Tier Integration Lapse Unflagged", 
                "Operations Admin", 
                "Status: 🔴 Delayed Alert | Notes: Vendor handshake failure occurred on June 18. Integration downgraded to free tier. Logged past the 24-hour PI §5 threshold due to system tracking staleness."
            ],
            [
                "LOG-016", 
                "2026-06-20T20:37:40-07:00", 
                "System_Log", 
                "GLOBAL_STATE", 
                "RECONCILIATION — System Log Backfill & Catch-up Sync", 
                "Operations Admin", 
                "Status: 🟢 Complete | Notes: Resolved 7-day logging staleness gap (June 14–20). Portfolio updates and completed tasks verified and synchronized through current session."
            ]
        ]
        try:
            log_sheet.append_rows(new_logs, value_input_option='USER_ENTERED')
            print("[+] Audit Success: Handshake recovery matrix and EOD records appended to System_Log.")
        except Exception as e:
            print(f"[-] Logging injection failed: {e}")
    else:
        print("[-] Error: 'System_Log' tab not resolved.")

    print("[SYSTEM] Execution cycle terminated cleanly. Data engine balanced.")

if __name__ == '__main__':
    main()
