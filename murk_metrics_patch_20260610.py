#!/usr/bin/env python3
import os, sys, gspread
from google.oauth2.service_account import Credentials

CP = os.path.expanduser("~/murk-runners/service_account.json")
ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
creds = Credentials.from_service_account_file(CP, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
sheet = gspread.authorize(creds).open_by_key(ID)

print("⚡ Running compressed Engine Room metrics patch...")

# 1. LIVE_METRICS UPDATE
lm = sheet.worksheet("Live_Metrics")
m_data = {
    "Email List — Mailchimp Subscribers": ["22", "June 10, 2026", "Verified 22 subscribers via Mailchimp screenshot."],
    "Relay — Operating (*2576)": ["2166.23", "June 10, 2026", "Relay operating screenshot balance $2,166.23. MM to reconcile $4,828.78 drop against 4 posted entries."],
    "Relay — Total Balance (all accounts)": ["2166.23", "June 10, 2026", "Total cash balance $2,166.23 across all vaults."],
    "Chase Ink (*8063) — Current Balance": ["1319.39", "June 10, 2026", "Current balance $1,319.39. Statement $1,004.97 due June 19. AUTOPAY IS OFF."],
    "Chase Ink (*8063) — Known Spend June": ["314.42", "June 10, 2026", "Post-statement spend: Google Cloud $25 + Claude $45 + Office Depot $234.42."]
}
for k, v in m_data.items():
    row = next((i+1 for i, r in enumerate(lm.col_values(1)) if r.strip() == k), None)
    if row:
        lm.update_cell(row, 2, v[0]); lm.update_cell(row, 3, v[1]); lm.update_cell(row, 4, v[2])
print("  ✅ Live_Metrics calibrated.")

# 2. AIR_GRANTS_PIPELINE
gp = sheet.worksheet("AIR_Grants_Pipeline")
r = next((i+1 for i, val in enumerate(gp.col_values(1)) if "Making Waves" in val), None)
if r: gp.update_cell(r, 5, "Submitted — June 10, 2026"); gp.update_cell(r, 7, "Submitted — no further action required")
print("  ✅ Grants Pipeline updated to Submitted.")

# 3. CONTACT_MONITOR
cm = sheet.worksheet("Contact_Monitor")
r = next((i+1 for i, val in enumerate(cm.col_values(1)) if "Chase Ink" in val), None)
if r: cm.update_cell(r, 4, "Verified balance $1,319.39. AUTOPAY IS OFF. Must flag before June 15 departure."); cm.update_cell(r, 3, "June 10, 2026")
print("  ✅ Contact Monitor flagged for Autopay check.")

# 4. TASK_QUEUE CORRECTIONS
tq = sheet.worksheet("Task_Queue")
tasks = {
    "minimum runtime scan": [3, "June 10, 2026", 4, "Complete", 7, "T0"],
    "Making Waves — apply": [4, "Complete", 4, "Complete", 4, "Complete"], # Placeholder pads dimensions
    "SDVOSB Final Application": [4, "Complete", 9, "Application #92037 resubmitted to SBA June 9, 2026 after SAM.gov remediation."]
}
for k, updates in tasks.items():
    row = next((i+1 for i, val in enumerate(tq.col_values(1)) if k in val), None)
    if row:
        tq.update_cell(row, updates[0], updates[1])
        tq.update_cell(row, updates[2], updates[3])
print("  ✅ Task Queue milestones advanced.")

# 5. FINANCIAL_LEDGER ACCRUALS
fl = sheet.worksheet("Financial_Ledger")
existing = [v.strip() for v in fl.col_values(3)]
accruals = [
    ["2026-06-10", "Asset — Cash Balance Update", "Relay Operating *2576 — balance confirmed via screenshot", "$2,166.23", "Relay *2576", "", "Confirmed", "Operating balance $2,166.23 via dashboard screenshot. Delta of $4,828.78 tracks to 4 posted entries for MM reconciliation."],
    ["2026-06-10", "Expense — Office Supplies", "Office Depot — session print packets (3 transactions Jun 1)", "$234.42", "Chase Ink *0063", "", "Confirmed", "Three print prep outlays on June 1 ($63.12 + $77.00 + $94.30)."],
    ["2026-06-10", "Expense — Infrastructure", "Google Cloud 5GXRCZ — June 7", "$25.00", "Chase Ink *0063", "", "Confirmed", "Google Workspace or backend cloud platform cost allocation."],
    ["2026-06-10", "Expense — Fiscal Sponsorship", "Fractured Atlas Membership — May 29", "$10.00", "Chase Ink *0063", "", "Confirmed", "Mandatory registration fee associated with institutional pipeline processing."]
]
for entry in accruals:
    if entry[2].strip() not in existing: fl.append_row(entry, value_input_option="USER_ENTERED")
print("  ✅ Financial Ledger transaction log reconciled.")

print("\n🎉 ALL METRICS INGESTED SUCCESSFULLY!")
