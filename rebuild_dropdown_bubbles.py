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

#!/usr/bin/env python3
"""
rebuild_dropdown_bubbles.py
The Murk Audio LLC — Project_Portfolio RAG Dropdown Chip Rebuilder
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
        
        # Extract internal grid ID to map destination coordinates
        grid_id = ws._properties['sheetId']

        # Build structural API update payload for modern dropdown chips
        body = {
            "requests": [
                {
                    "setDataValidation": {
                        "range": {
                            "sheetId": grid_id,
                            "startRowIndex": 1,      # Rows 2 down (bypassing header)
                            "endRowIndex": 100,      # Pad safety range
                            "startColumnIndex": 3,   # Column D (0-indexed)
                            "endColumnIndex": 4
                        },
                        "rule": {
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [
                                    {"userEnteredValue": "🟢 Green"},
                                    {"userEnteredValue": "🟡 Yellow"},
                                    {"userEnteredValue": "🔴 Red"}
                                ]
                            },
                            "showCustomUi": True,    # Forces modern pill/bubble style rendering
                            "strict": True
                        }
                    }
                }
            ]
        }
        
        sheet.batch_update(body)
        print("\n==> 🟢 DROPDOWN CHIPS REPAIRED: Bubbles successfully re-applied to Column D!")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
