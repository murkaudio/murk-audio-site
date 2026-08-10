#!/usr/bin/env python3
"""
fix_portfolio_header.py
The Murk Audio LLC — Project_Portfolio Column D Header Repair Hotfix
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
        
        # Overwrite the #REF! string in cell D1 (Row 1, Column 4)
        ws.update_cell(1, 4, "RAG Status")
        print("\n✅ CELL D1 REPAIRED: Header fixed to 'RAG Status' successfully!")
        
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
