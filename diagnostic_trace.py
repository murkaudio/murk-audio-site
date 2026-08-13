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
import sys
import traceback
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1243rjP1_vu59lDKscuwyy5f8aPFDUOAgYGoLSIwEyc"
SA_PATH = os.path.expanduser("~/murk-runners/service_account.json")

print("[Diagnostic] Initializing raw connection track...")
try:
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(SA_PATH, scopes=scopes)
    gc = gspread.authorize(creds)
    
    print(f"[Diagnostic] Testing connection to Spreadsheet ID: {SHEET_ID}")
    spreadsheet = gc.open_by_key(SHEET_ID)
    print("[Diagnostic] Success! Spreadsheet file located.")
    
    print("[Diagnostic] Testing connection to tab: Sheet1")
    ws = spreadsheet.sheet1
    print("[Diagnostic] Success! Sheet1 tab targeted cleanly.")
    
except Exception as e:
    print("\n🚨 CRITICAL CONNECTION FAULT DETECTED 🚨")
    print("-" * 60)
    traceback.print_exc()
    print("-" * 60)
