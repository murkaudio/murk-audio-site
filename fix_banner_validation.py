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
fix_banner_validation.py
The Murk Audio LLC — Comprehensive Validation Sweep
Session: June 11, 2026
"""
import os
import sys
import gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

RAW_VERDICTS = ["KEEP", "KILL", "SUBMITTED", "CONDITIONAL", "PARK"]

def main():
    print("=" * 75)
    print("🛡️ STARLIGHT UI REFACTOR — GLOBAL VALIDATION SWEEP (ROWS 1-3 FIX)")
    print("=" * 75)
    
    if not os.path.exists(SF):
        print("❌ System Error: Service account credentials missing."); sys.exit(1)
        
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        
        try:
            ws = sheet.worksheet("AIR_Grants_Pipeline")
        except gspread.exceptions.WorksheetNotFound:
            ws = sheet.worksheet("AIR_Grants")
            
        sheet_id = int(ws.id)
        total_rows = ws.row_count
        print(f"    📂 Targeting Sheet: '{ws.title}' | Sweeping {total_rows} rows...")

        requests_payload = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": total_rows,
                        "startColumnIndex": 4,
                        "endColumnIndex": 5
                    },
                    "cell": {},
                    "fields": "dataValidation"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 4,
                        "startColumnIndex": 3,
                        "endColumnIndex": 4
                    },
                    "cell": {},
                    "fields": "dataValidation"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 4,
                        "endRowIndex": total_rows,
                        "startColumnIndex": 3,
                        "endColumnIndex": 4
                    },
                    "cell": {
                        "dataValidation": {
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [{"userEnteredValue": opt} for opt in RAW_VERDICTS]
                            },
                            "showCustomUi": True,
                            "strict": True
                        }
                    },
                    "fields": "dataValidation"
                }
            }
        ]

        print("    🚀 Transmitting global validation payload to API endpoint...")
        sheet.batch_update({"requests": requests_payload})
        
        print("-" * 75)
        print("🟢 SUCCESS: Rows 1, 2, and 3 are pristine. Data dropdowns isolated to active leads.")
        print("=" * 75)
        
    except Exception as e:
        print(f"❌ Execution Fault: {e}"); sys.exit(1)

if __name__ == "__main__":
    main()
