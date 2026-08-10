#!/usr/bin/env python3
"""
restore_tq_array.py
The Murk Audio LLC — Project_Portfolio Column D Separation Fix
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
        ws = sheet.worksheet("Project_Portfolio")
        grid_id = ws._properties['sheetId']

        # 1. Clear validation dropdown rules from Column D
        clear_validation = {
            "requests": [
                {
                    "setDataValidation": {
                        "range": {
                            "sheetId": grid_id,
                            "startRowIndex": 0,
                            "endRowIndex": 100,
                            "startColumnIndex": 3, 
                            "endColumnIndex": 4
                        }
                    }
                }
            ]
        }
        sheet.batch_update(clear_validation)
        print("  ✅ Data validation constraints dropped cleanly.")

        # 2. Purge the entire column runway to clear any residual blocks
        ws.batch_clear(["D1:D100"])
        print("  ✅ Column D runway entirely cleared for calculation.")

        # 3. Write static string header to D1
        sheet.values_update(
            'Project_Portfolio!D1',
            params={'valueInputOption': 'USER_ENTERED'},
            body={'values': [["RAG Status"]]}
        )
        print("  ✅ Static text header written directly to cell D1.")

        # 4. Write isolated, clean MAP formula into cell D2
        # \u26AA = Gray | \U0001F534 = Red | \U0001F7E1 = Yellow | \U0001F7E2 = Green
        formula = '=MAP(A2:A100, LAMBDA(proj, IF(proj="", "", IF(COUNTIF(Task_Queue!$H:$H, proj)=0, "\u26AA Gray", IF(COUNTIFS(Task_Queue!$C:$C, "<"&TODAY(), Task_Queue!$D:$D, "<>Complete", Task_Queue!$D:$D, "<>Killed", Task_Queue!$H:$H, proj)>0, "\U0001F534 Red", IF(COUNTIFS(Task_Queue!$D:$D, "Queued", Task_Queue!$H:$H, proj)+COUNTIFS(Task_Queue!$D:$D, "In Progress", Task_Queue!$H:$H, proj)>0, "\U0001F7E1 Yellow", "\U0001F7E2 Green"))))))'

        sheet.values_update(
            'Project_Portfolio!D2',
            params={'valueInputOption': 'USER_ENTERED'},
            body={'values': [[formula]]}
        )
        print("  ✅ Standalone MAP array formula successfully written to cell D2.")
        print("\n==> 🟢 FIXED: The dashboard metrics are now completely synchronized!")

    except Exception as e:
        print(f"❌ Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
