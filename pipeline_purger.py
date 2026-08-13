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
pipeline_purger.py
The Murk Audio LLC — Zero-Trust Ledger Purge & Schema Upgrade
Session: June 11, 2026
"""
import os, sys, gspread
from google.oauth2.service_account import Credentials

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

KILLED_TARGETS = {
    "audio in color", "agog open call", "podcasting seriously fund",
    "nextup creative audio", "racc", "oregon arts commission",
    "mid atlantic arts", "film independent podcast"
}

def main():
    print("=" * 75); print("🛡️ STARLIGHT AUDIT ENGINE — PURGING HALLUCINATIONS")
    print("=" * 75)
    if not os.path.exists(SF): print("❌ Token missing."); sys.exit(1)
    try:
        sheet = gspread.authorize(Credentials.from_service_account_file(SF, scopes=SCOPES)).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        # 1. LIVE HEADER PRE-CHECK
        headers = [h.strip() for h in ws.row_values(1)]
        headers_lower = [h.lower() for h in headers]
        
        url_col_name = "Source URL Verification"
        if url_col_name.lower() not in headers_lower:
            ws.update_cell(1, len(headers) + 1, url_col_name)
            headers.append(url_col_name); headers_lower.append(url_col_name.lower())
            print(f"    ➕ Schema Upgrade: Appended '{url_col_name}' column.")

        name_idx = headers_lower.index("grant name") if "grant name" in headers_lower else 0

        # 2. DATA LAYER PURGE
        rows = ws.get_all_values()
        purge_count = 0
        for idx in range(len(rows) - 1, 0, -1):
            g_name = rows[idx][name_idx].strip().lower()
            if any(kill in g_name for kill in KILLED_TARGETS):
                ws.delete_rows(idx + 1)
                print(f"    🗑️ Purged invalid entry row {idx + 1}: '{rows[idx][name_idx]}'")
                purge_count += 1

        print("-" * 75); print(f"🟢 AUDIT COMPLETE: Wiped {purge_count} rows. Ledger is pristine."); print("=" * 75)
    except Exception as e: print(f"❌ Fault: {e}"); sys.exit(1)

if __name__ == "__main__": main()
