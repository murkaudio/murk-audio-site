#!/usr/bin/env python3
"""
inject_dropdowns.py
The Murk Audio LLC — Interactive Dropdown Injection Validation
Session: June 11, 2026
"""
import os
import sys
import re
import gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

STATUS_OPTIONS = ["Open", "Submitted", "Conditional", "Parked", "Killed", "Verify"]

def main():
    print("=" * 75)
    print("🛡️ DROPDOWN INJECTION ENGINE — CONFIGURING CELL DATA VALIDATION")
    print("=" * 75)
    
    if not os.path.exists(SF):
        print("❌ System Error: Service Account credentials missing."); sys.exit(1)
        
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        headers = [h.strip().lower() for h in ws.row_values(1)]
        print(f"    📊 Live Header Pre-Check: Located columns -> {headers}")
        
        if "status" not in headers:
            print("❌ Structure Error: Target column 'Status' not found."); sys.exit(1)
            
        status_col_idx = headers.index("status")
        sheet_id = ws.id
        total_rows = ws.row_count
        
        print(f"    ⚡ Formulating validation parameters for range E2:E{total_rows}...")
        
        validation_request = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": total_rows,
                            "startColumnIndex": status_col_idx,
                            "endColumnIndex": status_col_idx + 1
                        },
                        "cell": {
                            "dataValidation": {
                                "condition": {
                                    "type": "ONE_OF_LIST",
                                    "values": [{"userEnteredValue": opt} for opt in STATUS_OPTIONS]
                                },
                                "showCustomUi": True,
                                "strict": True
                            }
                        },
                        "fields": "dataValidation"
                    }
                }
            ]
        }
        
        print("    🚀 Transmitting structural batch update payload to cloud instance...")
        sheet.batch_update(validation_request)
        
        print("-" * 75)
        print("🟢 ENGINE OPERATIONAL: Column E cell blocks converted to clean interactive dropdowns.")
        print("=" * 75)
        
    except Exception as e:
        print(f"❌ Validation Injection Failed: {e}"); sys.exit(1)

if __name__ == "__main__":
    main()
