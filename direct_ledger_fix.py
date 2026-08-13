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
import gspread
from google.oauth2.service_account import Credentials

print("[ENGINE] Initializing direct ledger override...")

# Credentials & Core Sheet Mapping
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("/Users/jameswilliams/murk-runners/service_account.json", scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key("1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc")

# Target 1: Enforce hard scrub on Sheet1 (Row 6)
try:
    ws1 = sheet.worksheet("Sheet1")
    row_6 = ws1.row_values(6)
    
    if len(row_6) >= 2 and "ashley" in row_6[1].lower():
        print("[FOUND] Targeted 'ashley' entry on Sheet1 Row 6. Committing scrub...")
        
        # Overwrite Status (Col C / 3)
        ws1.update_cell(6, 3, "Open (Blocked - Grounding Fix Req)")
        
        # Overwrite Log Narrative (Col D / 4)
        purged_narrative = "[PURGED] Reverted due to severe generic template hallucination (CA vs OR jurisdiction drift, fake BMI/ASCAP music licensing). Pipeline blocked pending Soldier Boy prompt fix."
        ws1.update_cell(6, 4, purged_narrative)
        print("[SUCCESS] Sheet1 Row 6 successfully sanitized.")
    else:
        print("[WARN] Row 6 content did not match 'ashley'. Scanning sheet sequentially...")
        for idx, row in enumerate(ws1.get_all_values(), start=1):
            if len(row) >= 2 and row[0] == "2026-06-12" and row[1].lower() == "ashley":
                ws1.update_cell(idx, 3, "Open (Blocked - Grounding Fix Req)")
                ws1.update_cell(idx, 4, "[PURGED] Severe template drift rollback.")
                print(f"[SUCCESS] Dynamic match fixed row {idx} on Sheet1.")
                break
except Exception as e:
    print(f"[ERROR] Sheet1 direct update failed: {e}")

# Target 2: Sync and reset corresponding item on Task_Queue tab
try:
    wstq = sheet.worksheet("Task_Queue")
    headers = [h.lower().strip() for h in wstq.row_values(1)]
    
    if "status" in headers:
        status_col = headers.index("status") + 1
        tq_records = wstq.get_all_values()
        
        for idx, row in enumerate(tq_records, start=1):
            combined_row_text = " ".join(row).lower()
            if "2026-06-12" in combined_row_text and ("ashley" in combined_row_text or "soldier" in combined_row_text):
                wstq.update_cell(idx, status_col, "Open (Blocked)")
                print(f"[SUCCESS] Task_Queue row {idx} status reset to 'Open (Blocked)'.")
                break
    else:
        print("[WARN] Could not resolve 'Status' column on Task_Queue tab headers.")
except Exception as e:
    print(f"[NOTE] Task_Queue sync skipped or unmapped: {e}")

print("[ENGINE] Ledger correction run finalized.")
