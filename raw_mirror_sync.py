#!/usr/bin/env python3
"""
raw_mirror_sync.py
The Murk Audio LLC — Pure 1:1 Claude File Mirror
Session: June 11, 2026
"""
import os, sys, csv, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

LOCAL_CSV = os.path.expanduser("~/Downloads/TheMurk_AIR_GrantsPipeline_Audit_v6_11.xlsx - AIR_Grants_Pipeline.csv")
if not os.path.exists(LOCAL_CSV):
    LOCAL_CSV = "TheMurk_AIR_GrantsPipeline_Audit_v6_11.xlsx - AIR_Grants_Pipeline.csv"

def main():
    print("=" * 75); print("🛡️ STARLIGHT CORE — EXECUTING RAW 1:1 CLAUDE MIRROR SYNC")
    print("=" * 75)
    
    if not os.path.exists(SF):
        print("❌ Auth Error: service_account.json missing."); sys.exit(1)
    if not os.path.exists(LOCAL_CSV):
        print("❌ Data Error: Source CSV file target not found."); sys.exit(1)

    try:
        with open(LOCAL_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            all_rows = list(reader)
        print(f"    📂 Source Loaded: Read {len(all_rows)} structural rows from CSV.")
        
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        print("    🗑️ Wiping live sheet cells to make space for raw mirror...")
        ws.clear()
        
        print(f"    🚀 Uploading pure 1:1 database mirror array...")
        ws.append_rows(all_rows, value_input_option='USER_ENTERED')
        
        print("-" * 75)
        print("🟢 SUCCESS: Worksheet is now a 1:1 mirror of the Claude audit document.")
        print("=" * 75)
        
    except Exception as e:
        print(f"❌ Core Execution Fault: {e}"); sys.exit(1)

if __name__ == "__main__":
    main()
