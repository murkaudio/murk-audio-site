#!/usr/bin/env python3
"""
Absolute Path: /Users/jameswilliams/murk-runners/fix_hughie_alignment.py
Core Function: Insert Schema Headers at Row 1, Shift Live Data to Row 2, Freeze & Format
"""

import sys
import warnings
import gspread
from google.oauth2.service_account import Credentials

# Suppress environmental library warning clutter
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def fix_headers_and_shift_grid():
    print("[ENGINE] Committing low-level row shift on 'Hughie_Marketing' tab...")
    
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
    except Exception as e:
        print(f"[ERROR] Spreadsheet connection handshake failed: {e}")
        sys.exit(1)

    # 1. Structural Audit: Detect Data vs Header state
    first_row = ws.row_values(1)
    headers = ["Date", "Category", "Finding", "Source", "Action Required", "Narrative"]
    
    if first_row and first_row[0].startswith("202"):
        print("[ENGINE] Found live data on Row 1. Shifting row down and inserting schema headers...")
        ws.insert_row(headers, index=1)
    else:
        print("[ENGINE] Row 1 is empty or already contains non-date strings. Overwriting with clean headers...")
        if not first_row or first_row[0].lower() != "date":
            ws.insert_row(headers, index=1)

    # 2. Recalibrate Grid Geometry Post-Shift
    total_rows = len(ws.get_all_values())
    print(f"[ENGINE] Grid geometry locked at {total_rows} rows. Compiling UI batch mutations...")

    # 3. Assemble Unified UI Formatting Payload
    requests = [
        # Request 1: Freeze Row 1
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
        # Request 2: Apply Bold Typography to Range A1:F1
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

    # Request 3: Apply Chronological Range Sort (Z-A) safely on data block (Rows 2+)
    if total_rows > 1:
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

    # 4. Push Structural Layout to Google Servers
    try:
        sheet.batch_update({"requests": requests})
        print("[ENGINE] Success. Row alignment, cell styles, and sort indexing completed.")
        print("[GRID_REALIGNMENT_SUCCESS]")
    except Exception as e:
        print(f"[ERROR] Batch layout update execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    first_row = fix_headers_and_shift_grid()
