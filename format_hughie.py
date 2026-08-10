#!/usr/bin/env python3
"""
Absolute Path: /Users/jameswilliams/murk-runners/format_hughie.py
Core Function: UI Recalibration for 'Hughie_Marketing' Worksheet Tab
Remediation: Decoupled formatting mutations from sort validations to prevent premature script exits
"""

import sys
import warnings
import gspread
from google.oauth2.service_account import Credentials

# Suppress environmental library warning clutter
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def recalibrate_hughie_sheet():
    print("[ENGINE] Initializing hardened sheet recalibration script...")
    
    # 1. Secure Connection Context
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    service_account_path = "/Users/jameswilliams/murk-runners/service_account.json"
    master_sheet_id = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
    
    try:
        creds = Credentials.from_service_account_file(service_account_path, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(master_sheet_id)
        ws = sheet.worksheet("Hughie_Marketing")
        sheet_id = ws._properties['sheetId']
        print("[ENGINE] Connection successfully verified for worksheet tab.")
    except Exception as e:
        print(f"[ERROR] Failed to establish spreadsheet handshake: {e}")
        sys.exit(1)

    # 2. Ingest Sheet Data Geometry
    all_rows = ws.get_all_values()
    total_rows = len(all_rows)

    # 3. Base UI Structure Requests Array (Always Executed)
    requests = [
        # Mutation Vector 1: Freeze Top Row (Row 1)
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        },
        # Mutation Vector 2: Apply Bold Typography Transformation to Headers Range (A1:F1)
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 6
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold"
            }
        }
    ]

    # 4. Conditional Data Range Insertion Gate
    if total_rows > 1:
        print(f"[ENGINE] Active data records detected ({total_rows - 1} entries). Injecting sortRange spec...")
        requests.append({
            "sortRange": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": total_rows,
                    "startColumnIndex": 0,
                    "endColumnIndex": 6
                },
                "sortSpecs": [
                    {
                        "dimensionIndex": 0,  # Column A: Date
                        "sortOrder": "DESCENDING"
                    }
                ]
            }
        })
    else:
        print("[ENGINE] Zero data records present to organize. Skipping sorting layer but preserving UI updates.")

    # 5. Commit Request Payloads Live to Grid
    try:
        sheet.batch_update({"requests": requests})
        print("[ENGINE] Success. Spreadsheet UI modifications committed cleanly.")
        print("[MARKETING_FORMAT_SUCCESS]")
    except Exception as e:
        print(f"[ERROR] Batch layout update execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    recalibrate_hughie_sheet()
