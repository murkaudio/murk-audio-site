#!/usr/bin/env python3
"""
Absolute Path: /Users/jameswilliams/murk-runners/fix_press_alignment.py
Core Function: Structural Row Shift, Header Insertion, Word-Wrap, Bold, and Row Freeze
"""

import sys
import warnings
import gspread
from google.oauth2.service_account import Credentials

# Suppress environmental library warning clutter
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def fix_press_tab_alignment():
    print("[ENGINE] Initializing cell shifting operations on 'Press_Intel' tab...")
    
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
        ws = sheet.worksheet("Press_Intel")
        sheet_id = ws._properties['sheetId']
    except Exception as e:
        print(f"[ERROR] Spreadsheet connection layer handshake failed: {e}")
        sys.exit(1)

    # 1. Structural Check: Verify if data sits on Row 1
    first_row = ws.row_values(1)
    headers = ["Date", "Article Title", "Source Link", "Status"]
    
    if first_row and first_row[0].startswith("June"):
        print("[ENGINE] Live scraped data detected on Row 1. Pushing data rows down...")
        ws.insert_row(headers, index=1)
    else:
        print("[ENGINE] Row 1 layout empty or already contains string indices. Enforcing headers...")
        if not first_row or first_row[0].lower() != "date":
            ws.insert_row(headers, index=1)

    # 2. Compile UI Layout Batch Mutations (Bold + Freeze + Word Wrap)
    requests = [
        # Mutation 1: Lock and Freeze Row 1
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
        # Mutation 2: Apply Text Transformations (Bold + Word Wrap) across A1:D1
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "bold": True
                        },
                        "wrapStrategy": "WRAP"
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.wrapStrategy"
            }
        }
    ]

    # 3. Commit Batch Array Live to Google Sheet
    try:
        sheet.batch_update({"requests": requests})
        print("[ENGINE] Success. Row 1 frozen, headings bolded, and word-wrap properties active.")
        print("[PRESS_FORMAT_SUCCESS]")
    except Exception as e:
        print(f"[ERROR] Batch layout update execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_press_tab_alignment()
