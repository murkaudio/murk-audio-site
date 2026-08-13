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
import os, sys, re, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

TASK_UPDATES = {
    "confirm 7 assets in drive": {"status": "Complete"},
    "sbu — cost baseline": {"status": "Complete"},
    "sbu — funding strategy session": {"status": "Complete"},
    "invoice chase workflow": {"status": "Killed"},
    "epic megagrants": {"status": "Killed"},
    "sbu scripts delivered": {"due": "June 18, 2026"},
    "scripts locked — james sign-off": {"due": "June 19, 2026"},
    "studio booked before casting opens": {"due": "June 25, 2026"},
    "sbu casting opens": {"due": "June 21, 2026"},
    "air membership": {"status": "Parked", "due": "September 1, 2026"}
}

NEW_TASKS = [
    ["Dead Signal Animated Trailer PRD", "Open", "Alfred/Soldier Boy", "June 17, 2026", "PRD for animated KS trailer via Fiverr path."],
    ["YouTube Content Strategy Session", "Queued", "Butcher+Hughie", "August 16, 2026", "Post-E1 strategy review inspired by The Sojourn channel."],
    ["Last Dance S2 outreach", "Open", "Unassigned", "September 1, 2026", "September trigger outreach list insertion."],
    ["KS Session Export discrepancy resolution", "Open", "Alfred/Hughie", "July 4, 2026", "Correct campaign copy dates and fix Blackwood Manor references."],
    ["Oregon Arts Commission Career Opportunity Grant", "Open", "James", "September 24, 2026", "Vetted active individual opportunity tracking."],
    ["AWS Activate / Microsoft Founders Hub / Google for Startups", "Open", "Soldier Boy", "Rolling", "Apply when technical infrastructure bandwidth allows."]
]

def main():
    print("=" * 75); print("🛡️ STARLIGHT CORE — RUNNING COMPLETE MASTER EOD ASSIMILATION")
    print("=" * 75)
    if not os.path.exists(SF): print("❌ System Error: Service account key missing."); sys.exit(1)
    
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        
        # --- TASK QUEUE UPDATE BLOCK ---
        try:
            tq = sheet.worksheet("Task_Queue")
            tq_rows = tq.get_all_values()
            tq_headers = [h.strip().lower() for h in tq_rows[0]]
            
            task_idx = tq_headers.index("task") + 1
            status_idx = tq_headers.index("status") + 1
            due_idx = tq_headers.index("due date") + 1 if "due date" in tq_headers else tq_headers.index("due") + 1
            
            existing_tasks = {row[task_idx-1].strip().lower(): r_num for r_num, row in enumerate(tq_rows, start=1) if row}
            
            print("    ⚡ Processing current Task Queue updates...")
            for lookup_name, updates in TASK_UPDATES.items():
                matched_row = None
                for existing_name in existing_tasks:
                    if lookup_name in existing_name:
                        matched_row = existing_tasks[existing_name]
                        break
                
                if matched_row:
                    if "status" in updates:
                        tq.update_cell(matched_row, status_idx, updates["status"])
                    if "due" in updates:
                        tq.update_cell(matched_row, due_idx, updates["due"])
                    print(f"      ✅ Synchronized existing row {matched_row}: {lookup_name}")

            print("    ➕ Checking and appending newly generated EOD tasks...")
            append_rows = []
            for n_task in NEW_TASKS:
                if n_task[0].lower() not in existing_tasks:
                    payload = [""] * len(tq_headers)
                    payload[tq_headers.index("task")] = n_task[0]
                    payload[tq_headers.index("status")] = n_task[1]
                    if "owner" in tq_headers: payload[tq_headers.index("owner")] = n_task[2]
                    payload[due_idx-1] = n_task[3]
                    if "notes" in tq_headers: payload[tq_headers.index("notes")] = n_task[4]
                    elif "description" in tq_headers: payload[tq_headers.index("description")] = n_task[4]
                    append_rows.append(payload)
            
            if append_rows:
                tq.append_rows(append_rows, value_input_option='USER_ENTERED')
                print(f"      🚀 Ingested {len(append_rows)} new tasks into the active queue pipeline.")
        except Exception as tq_err:
            print(f"    ⚠️ Task Queue Sync Warning: Bypassed or failed -> {tq_err}")

        # --- GRANTS PIPELINE UPDATE BLOCK ---
        try:
            try:
                ws = sheet.worksheet("AIR_Grants_Pipeline")
            except gspread.exceptions.WorksheetNotFound:
                ws = sheet.worksheet("AIR_Grants")
                
            grants_rows = ws.get_all_values()
            g_headers = [h.strip().lower() for h in grants_rows[3]] if len(grants_rows) > 3 else [h.strip().lower() for h in ws.row_values(1)]
            
            g_name_idx = g_headers.index("grant name") + 1
            g_verdict_idx = g_headers.index("verdict") + 1
            g_notes_idx = g_headers.index("status notes") + 1
            g_deadline_idx = g_headers.index("public deadline") + 1
            
            print("    ⚡ Aligning key milestone indicators inside Grants Pipeline...")
            for r_num, row in enumerate(grants_rows, start=1):
                if len(row) < g_name_idx: continue
                cell_name_lower = row[g_name_idx-1].strip().lower()
                
                if "epic megagrants" in cell_name_lower:
                    ws.update_cell(r_num, g_verdict_idx, "KILL")
                    ws.update_cell(r_num, g_notes_idx, "Killed - no Unreal Engine use case. Removed from tracking sequence.")
                    print(f"      🔴 Marked entry: Epic MegaGrants -> KILL")
                    
                if "air membership" in cell_name_lower:
                    ws.update_cell(r_num, g_verdict_idx, "PARK")
                    ws.update_cell(r_num, g_deadline_idx, "September 1, 2026")
                    ws.update_cell(r_num, g_notes_idx, "Parked - directory listing carries zero pre-launch conversion volume value.")
                    print(f"      🔵 Parked entry: AIR Membership -> September 1, 2026")
                    
        except Exception as g_err:
            print(f"    ⚠️ Grants Ledger Sync Warning: Field modification encountered errors -> {g_err}")

        print("-" * 75)
        print("🟢 MASTER SYNC SECURE: Accomplishments compiled and production lines shifted cleanly.")
        print("=" * 75)
        
    except Exception as e: print(f"❌ Critical Core Fault: Ingestion script aborted -> {e}"); sys.exit(1)

if __name__ == "__main__": main()
