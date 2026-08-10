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
