#!/usr/bin/env python3
"""
sync_cage_status.py
The Murk Audio LLC — Direct Infrastructure Architecture Alignment Patch
Session: June 11, 2026
"""

import os
import sys
import gspread
from google.oauth2.service_account import Credentials

# Core System Path Routing
SERVICE_ACCOUNT_PATH = os.path.expanduser("~/murk-runners/service_account.json")
SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def main():
    print("=" * 75)
    print("⚡ STARLIGHT WORKSPACE PATCH ENGINE — LEDGER REALIGNMENT RUN")
    print("=" * 75)

    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"❌ System Error: service_account.json missing at {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
        sheet = gspread.authorize(creds).open_by_key(SHEET_ID)

        # ---- PHASE 1: REPAIR AND ALIGN CONTACT_MONITOR TAB ----
        print("  🌐 Accessing Contact_Monitor tab...")
        cm = sheet.worksheet("Contact_Monitor")
        cm_rows = cm.get_all_values()
        
        # Safe-clean: Delete any previous malformed rows matching the layout mismatch
        for idx, row in enumerate(cm_rows):
            if len(row) > 1 and "cagereview@dla.mil" in row[1].lower() and "2026-" in row[0]:
                cm.delete_rows(idx + 1)
                print(f"    ✨ Cleaned malformed tracking layout at row index {idx + 1}.")
                break

        # Execute Live Header Mapping Pre-Check
        cm_headers = [h.strip().lower() for h in cm.row_values(1)]
        print(f"    📊 Live Header Pre-Check: Discovered columns {cm_headers}")

        # Target Content Values
        cm_data = {
            "contact": "CAGE",
            "email": "CAGEReview@dla.mil",
            "last contact date": "June 11, 2026",
            "last outcome": "Response sent. Articles of Organization attached. Awaiting CAGE processing.",
            "next trigger": "Monitor for reply, deadline June 16.",
            "status": "Active — awaiting CAGE processing",
            "narrative": "SDVOSB administrative requirement milestone gate"
        }

        # Build row array dynamically matching the live sheet columns exactly
        cm_payload = [""] * len(cm_headers)
        for col_name, val in cm_data.items():
            if col_name in cm_headers:
                cm_payload[cm_headers.index(col_name)] = val

        cm.append_row(cm_payload, value_input_option='USER_ENTERED')
        print("    ✅ Contact_Monitor entry correctly aligned and committed.")

        # ---- PHASE 2: DETECT, CREATE, AND ALIGN TASK_QUEUE RECORD ----
        print("  🌐 Accessing Task_Queue tab...")
        tq = sheet.worksheet("Task_Queue")
        tq_rows = tq.get_all_values()
        
        tq_headers = [h.strip().lower() for h in tq.row_values(1)]
        print(f"    📊 Live Header Pre-Check: Discovered columns {tq_headers}")

        # Target Content Values for Task Row
        tq_data = {
            "task": "CAGE reply — attach Articles of Org",
            "owner": "James",
            "due": "June 11, 2026",
            "status": "Done",
            "project": "Legal & Compliance",
            "t-day": "T0"
        }

        # Scan existing rows to see if a CAGE item is already there
        found_row_idx = None
        for idx, r in enumerate(tq_rows):
            if "cage" in " ".join(r).lower():
                found_row_idx = idx + 1
                break

        if found_row_idx:
            # If row exists, find the exact column index for Status and overwrite to Done
            if "status" in tq_headers:
                status_idx = tq_headers.index("status") + 1
                tq.update_cell(found_row_idx, status_idx, "Done")
                print(f"    ✅ Existing task found at row {found_row_idx}. Status column marked 'Done'.")
        else:
            # Build the new task row array dynamically matching sheet columns exactly
            tq_payload = [""] * len(tq_headers)
            for col_name, val in tq_data.items():
                if col_name in tq_headers:
                    tq_payload[tq_headers.index(col_name)] = val
            
            tq.append_row(tq_payload, value_input_option='USER_ENTERED')
            print("    ✅ New task row dynamically constructed, appended, and marked 'Done'.")

        print("-" * 75)
        print("🟢 LEDGER STABILIZATION COMPLETE: Dynamic alignment matches layout rules perfectly.")
        print("=" * 75)

    except Exception as e:
        print(f"❌ Execution Fault: Alignment failed -> {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
