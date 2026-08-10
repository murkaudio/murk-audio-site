import os
import gspread
from google.oauth2.service_account import Credentials

# 🔐 1. Authentication and Sheet Initialization
SERVICE_ACCOUNT_FILE = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"

def apply_conditional_formatting():
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
    
    # 📑 2. Find the Status Column Location Dynamically
    headers = sheet.row_values(1)
    try:
        status_col_idx = next(i for i, h in enumerate(headers, 1) if any(kw in h.lower() for kw in ["status", "verdict", "scope"]))
    except StopIteration:
        print("[-] Mapping Failure: Could not locate a Status or Scope column in your header row.")
        return

    col_letter = chr(64 + status_col_idx)
    print(f"[+] Scope Status column located at Column {col_letter} (Index: {status_col_idx})")

    # 🔍 3. Read Sheet Metadata to Safely Clear Pre-existing Rules
    meta = spreadsheet.fetch_sheet_metadata()
    num_existing_rules = 0
    for s in meta.get('sheets', []):
        if s['properties']['sheetId'] == sheet_id:
            num_existing_rules = len(s.get('conditionalFormats', []))
            break

    print(f"[+] Found {num_existing_rules} existing conditional rules on tab. Compiling clear sequence...")

    requests = []
    # Always delete index 0 sequentially, as the index list automatically shifts down with each pop
    for _ in range(num_existing_rules):
        requests.append({
            "deleteConditionalFormatRule": {
                "sheetId": sheet_id,
                "index": 0
            }
        })

    # 🎨 4. Define the Target Matrix (Rows 2 to 5000, Columns A to Z)
    grid_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,      # Row 2 (0-indexed)
        "endRowIndex": 5000,     # Safety cap boundary
        "startColumnIndex": 0,   # Column A
        "endColumnIndex": 26     # Column Z
    }

    # Append new formatting rules to the batch request list
    requests.extend([
        # Complete Rule (Dark Green Background / White Bold Text)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [grid_range],
                    "booleanRule": {
                        "condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": f'=${col_letter}2="Complete"'}]},
                        "format": {
                            "backgroundColor": {"red": 0.118, "green": 0.275, "blue": 0.125},
                            "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
                        }
                    }
                },
                "index": 0
            }
        },
        # Killed or Kill Rule (Dark Red Background / White Bold Text)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [grid_range],
                    "booleanRule": {
                        "condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": f'=OR(LOWER(${col_letter}2)="kill", LOWER(${col_letter}2)="killed")'}]},
                        "format": {
                            "backgroundColor": {"red": 0.486, "green": 0.102, "blue": 0.102},
                            "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
                        }
                    }
                },
                "index": 1
            }
        },
        # In Progress Rule (Light Green Background / Black Text)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [grid_range],
                    "booleanRule": {
                        "condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": f'=${col_letter}2="In Progress"'}]},
                        "format": {
                            "backgroundColor": {"red": 0.886, "green": 0.941, "blue": 0.851},
                            "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                        }
                    }
                },
                "index": 2
            }
        },
        # Backlog Rule (Light Blue Background / Black Text)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [grid_range],
                    "booleanRule": {
                        "condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": f'=${col_letter}2="Backlog"'}]},
                        "format": {
                            "backgroundColor": {"red": 0.867, "green": 0.922, "blue": 0.969},
                            "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                        }
                    }
                },
                "index": 3
            }
        },
        # Parked Rule (Soft Pink Background / Black Text)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [grid_range],
                    "booleanRule": {
                        "condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": f'=OR(LOWER(${col_letter}2)="park", LOWER(${col_letter}2)="parked")'}]},
                        "format": {
                            "backgroundColor": {"red": 0.984, "green": 0.769, "blue": 0.824},
                            "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                        }
                    }
                },
                "index": 4
            }
        }
    ])

    print("[+] Transmission compiled. Executing sheet batch update rules...")
    spreadsheet.batch_update({"requests": requests})
    print("[✔] Row-level conditional formatting styles have been successfully integrated.")

if __name__ == "__main__":
    apply_conditional_formatting()
