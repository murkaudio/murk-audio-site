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

import os
import gspread
from google.oauth2.service_account import Credentials

# 🔐 1. Authentication and Sheet Initialization
SERVICE_ACCOUNT_FILE = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"

def apply_global_updates():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[-] Fatal Error: Gspread credential file missing at {SERVICE_ACCOUNT_FILE}")
        return

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    
    print(f"[+] Connected to Google API. Accessing primary tab...")
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.get_worksheet(0)
    sheet_id = sheet.id
    
    # Dynamically find the exact total rows current in the spreadsheet
    max_rows = sheet.row_count
    print(f"[+] Spreadsheet scale verified: {max_rows} total rows found.")

    # 🧼 2. Clean up any existing "In Process" data entries to prevent validation conflicts
    print("[+] Scanning Column D for obsolete 'In Process' text strings...")
    column_d_values = sheet.col_values(4) # Column D is the 4th column
    
    cells_to_update = []
    for row_num, val in enumerate(column_d_values, start=1):
        if val.strip() == "In Process":
            cells_to_update.append(gspread.cell.Cell(row=row_num, col=4, value="In Progress"))
            
    if cells_to_update:
        print(f"[+] Found {len(cells_to_update)} entries with 'In Process'. Migrating to 'In Progress'...")
        sheet.update_cells(cells_to_update, value_input_option='USER_ENTERED')
        print("[✔] Cell data migration complete.")
    else:
        print("[-] No conflicting 'In Process' text strings found in the data rows.")

    print(f"[+] Applying strict rules from row 2 down to the global boundary row {max_rows}...")

    # 🛠️ 3. Structure the Data Validation Requests covering all rows
    validation_request = {
        "requests": [
            # Dropdown Menu on Column D with "In Progress"
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,          # Row 2 (0-indexed)
                        "endRowIndex": max_rows,     # Dynamic total sheet depth
                        "startColumnIndex": 3,       # Column D (0-indexed: A=0, B=1, C=2, D=3)
                        "endColumnIndex": 4
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [
                                {"userEnteredValue": "In Progress"},
                                {"userEnteredValue": "Complete"},
                                {"userEnteredValue": "Killed"},
                                {"userEnteredValue": "Backlog"},
                                {"userEnteredValue": "Parked"}
                            ]
                        },
                        "showCustomUi": True,
                        "strict": False
                    }
                }
            },
            # Calendar Picker on Column F
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": max_rows,
                        "startColumnIndex": 5,       # Column F (0-indexed: E=4, F=5)
                        "endColumnIndex": 6
                    },
                    "rule": {
                        "condition": {
                            "type": "DATE_IS_VALID"
                        },
                        "showCustomUi": True,
                        "strict": False
                    }
                }
            }
        ]
    }

    print("[+] Transmitting global batch validation configurations to Google Drive...")
    spreadsheet.batch_update(validation_request)
    print(f"[✔] Global update successful! Column D dropdowns and Column F calendar validation fully mapped across all {max_rows} rows.")

if __name__ == "__main__":
    apply_global_updates()
