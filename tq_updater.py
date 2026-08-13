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
import re
import traceback
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SA_PATH = os.path.expanduser("~/murk-runners/service_account.json")
INPUT_FILE = os.path.expanduser("~/murk-runners/tq_changes.md")

if not os.path.exists(INPUT_FILE):
    print(f"[ERROR] Changes file not found at {INPUT_FILE}. Run TQUPDATE in Claude first.")
    sys.exit(1)

print("[UPDATER] Connecting to Google Workspace Ledger...")
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(SA_PATH, scopes=scopes)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet("Task_Queue")
    
    # Fetch all current rows to map existing tasks
    all_matrix = worksheet.get_all_values()
    headers = all_matrix[0]
    existing_tasks = {all_matrix[i][0].strip().lower(): i + 1 for i in range(1, len(all_matrix)) if all_matrix[i]}

    print("[UPDATER] Parsing staging updates from local markdown payload...")
    with open(INPUT_FILE, "r") as f:
        lines = f.readlines()

    updates_count = 0
    appends_count = 0

    for line in lines:
        if not line.startswith("|") or "Task" in line or "---" in line:
            continue  # Skip headers and prose boundaries
            
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 8:
            continue
            
        # Column Layout Mapping: Task (0), Owner (1), Due (2), Status (3), Start (4), Mid (5), Project (6), Pillar (7)
        task_name = cells[0]
        task_key = task_name.strip().lower()
        
        # Build payload vector skipping Column G (index 7 in 1-based sheets sizing)
        row_payload = {
            1: cells[0], # A: Task
            2: cells[1], # B: Owner
            3: cells[2], # C: Due
            4: cells[3], # D: Status
            5: cells[4], # E: Start Date
            6: cells[5], # F: Mid-Point
            8: cells[6], # H: Project
            9: cells[7]  # I: Pillar
        }

        if task_key in existing_tasks:
            row_idx = existing_tasks[task_key]
            # Update matching row cells
            for col_idx, val in row_payload.items():
                worksheet.update_cell(row_idx, col_idx, val)
            print(f"[UPDATE] Synchronized existing task cells: '{task_name}' at row {row_idx}")
            updates_count += 1
        else:
            # Append completely fresh row
            new_row = [cells[0], cells[1], cells[2], cells[3], cells[4], cells[5], "", cells[6], cells[7]]
            worksheet.append_row(new_row, value_input_option="USER_ENTERED")
            print(f"[APPEND] Added fresh transaction row to ledger: '{task_name}'")
            appends_count += 1

    # Wipe staging file upon successful loop execution to clear state
    os.remove(INPUT_FILE)
    print(f"\n[COMPLETED] TQ Synchronization Run Done. {updates_count} updated, {appends_count} appended. Staging cache cleared.")

except Exception as e:
    print(f"[CRITICAL] Operational Update Failure: {e}")
    traceback.print_exc()
    sys.exit(1)
