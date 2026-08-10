#!/usr/bin/env python3
"""
format_sheet1.py
The Murk Audio LLC — Sheet1 Header Insertion & Word-Wrap Optimization
Session: June 11, 2026
"""

import os
import sys
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_PATH = os.path.expanduser("~/murk-runners/service_account.json")
SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def main():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"❌ Service account not found: {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
        sheet = gspread.authorize(creds).open_by_key(SHEET_ID)
        ws = sheet.worksheet("Sheet1")
        grid_id = ws._properties['sheetId']

        # 1. Check if header row already exists to avoid double-insertion
        first_cell = ws.cell(1, 1).value
        if first_cell == "Date":
            print("  ℹ️  Header row already present. Proceeding to style formatting.")
        else:
            headers = ['Date', 'Runner / Role', 'Status', 'Log Narrative / Output']
            ws.insert_row(headers, index=1, value_input_option='USER_ENTERED')
            print("  ✅ Appropriated structural headers inserted at Row 1.")

        # 2. Freeze the top header line
        ws.freeze(rows=1)
        print("  ✅ Top line row frozen successfully.")

        # 3. Apply Batch Formatting: Bold Row 1 + Global Word-Wrap
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": grid_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 4
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True}
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold"
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": grid_id,
                            "startRowIndex": 0,
                            "endRowIndex": 500,  # Full structural pad depth
                            "startColumnIndex": 0,
                            "endColumnIndex": 10
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "wrapStrategy": "WRAP"
                            }
                        },
                        "fields": "userEnteredFormat.wrapStrategy"
                    }
                }
            ]
        }
        
        sheet.batch_update(body)
        print("  ✅ Row 1 bolded and global word-wrap applied to all cells.")
        print("\n==> 🟢 FORMATTING COMPLETE: Sheet1 is completely optimized and wrapped!")

    except Exception as e:
        print(f"❌ Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
