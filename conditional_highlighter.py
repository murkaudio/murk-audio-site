#!/usr/bin/env python3
import os, sys, json, re, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

def main():
    print("=" * 75); print("🛡️ CONDITIONAL FORMATTING ENGINE — INJECTING VISUAL MATRIX GUARDS")
    print("=" * 75)
    if not os.path.exists(SF): print("❌ System Error: Service account key missing."); sys.exit(1)
    
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        headers = [h.strip().lower() for h in ws.row_values(1)]
        print(f"    📊 Live Header Pre-Check: Located column coordinates -> {headers}")
        
        if "status" not in headers:
            print("❌ Structure Error: 'Status' column missing from target ledger."); sys.exit(1)
            
        status_col_idx = headers.index("status")
        col_letter = chr(65 + status_col_idx)
        
        sheet_id = ws.id
        total_rows = ws.row_count
        total_cols = ws.col_count
        
        target_formula = f'=${col_letter}2="Killed"'
        print(f"    ⚡ Formulating custom row-wide execution syntax: {target_formula}")
        
        formatting_request = {
            "requests": [
                {
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [
                                {
                                    "sheetId": sheet_id,
                                    "startRowIndex": 1,
                                    "endRowIndex": total_rows,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": total_cols
                                }
                            ],
                            "booleanRule": {
                                "condition": {
                                    "type": "CUSTOM_FORMULA",
                                    "values": [{"userEnteredValue": target_formula}]
                                },
                                "format": {
                                    "backgroundColor": {
                                        "red": 0.95,
                                        "green": 0.82,
                                        "blue": 0.82
                                    }
                                }
                            }
                        },
                        "index": 0
                    }
                }
            ]
        }
        
        print("    🚀 Transmitting conditional formatting payload to cloud instance...")
        sheet.batch_update(formatting_request)
        
        print("-" * 75)
        print("🟢 ENGINE OPERATIONAL: Row-wide red highlights locked to 'Killed' database tokens.")
        print("=" * 75)
        
    except Exception as e: print(f"❌ Formatting Injection Failed: {e}"); sys.exit(1)

if __name__ == "__main__": main()
