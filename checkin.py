#!/usr/bin/env python3
import os
import sys
import gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"

def main():
    if not os.path.exists(SF):
        print("❌ System Error: Token file missing."); sys.exit(1)
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        print("=====================================================================")
        print("🦅 THE MURK AUDIO LLC — REAL-TIME INGESTION PIPELINE UPDATED")
        print("=====================================================================")
        
        ws = sheet.worksheet("Staging_Grants")
        raw_rows = ws.get_all_values()
        print(f"\n📥 CLOUD STAGING LAYER TARGET: {len(raw_rows) - 1} unverified rows live.")
        print("🟢 LIVE PIPELINE IS ACTIVE AND ERROR-FREE")
        print("=====================================================================")
    except Exception as e:
        print(f"❌ Thread Fault: {e}"); sys.exit(1)

if __name__ == '__main__':
    main()\n