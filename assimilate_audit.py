#!/usr/bin/env python3
import os, sys, json, re, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

AUDIT_RULES = {
    "emerging native arts": {"status": "Killed — performing arts exclusion", "deadline": "June 18, 2026"},
    "evolution grant": {"status": "Killed — fine arts focus / no AI", "deadline": "June 19, 2026"},
    "media projects development": {"status": "Killed — LLC ineligible", "deadline": "June 25, 2026"},
    "media projects production": {"status": "Killed — LLC ineligible", "deadline": "June 25, 2026"},
    "light work artist residency": {"status": "Killed — photography focus", "deadline": "June 30, 2026"},
    "playa art/sci": {"status": "Killed — no environmental fit", "deadline": "June 30, 2026"},
    "wassaic project": {"status": "Parked — revisit 2027", "deadline": "July 1, 2026"},
    "grants for arts projects - media arts": {"status": "Killed — LLC ineligible", "deadline": "July 9, 2026"},
    "loghaven artist residency": {"status": "Parked — revisit 2027", "deadline": "July 15, 2026"},
    "yaddo music": {"status": "Parked — revisit 2027", "deadline": "July 1, 2026", "rename": "Yaddo Residency"},
    "macdowell fellowship": {"status": "Parked — apply September 2026", "deadline": "September 10, 2026"},
    "sundance institute audio": {"status": "Killed — does not exist", "deadline": "None"},
    "individual artist fellowship": {"status": "Open", "deadline": "October 2, 2026"},
    "portland arts project": {"status": "Open", "deadline": "October 16, 2026"},
    "community cultural grants": {"status": "Open", "deadline": "November 1, 2026"},
    "paul allen family foundation": {"status": "Qualified", "deadline": "November 15, 2026"},
    "creative heights initiative": {"status": "Open", "deadline": "February 12, 2027"},
    "creative capital open call": {"status": "Open", "deadline": "April 2, 2027"},
    "musicoregon echo fund": {"status": "Verify eligibility", "deadline": "September 5, 2026"},
    "friends of ifcc": {"status": "Verify details", "deadline": "September 12, 2026"},
    "awesome foundation portland": {"status": "Submitted — awaiting decision", "deadline": "Rolling monthly"},
    "making waves": {"status": "Submitted — June 10, 2026", "deadline": "June 30, 2026"},
    "air storyfund": {"status": "Conditional", "deadline": "Rolling"},
    "warrior rising": {"status": "Open", "deadline": "Rolling Entry"},
    "vip small business": {"status": "Open", "deadline": "Rolling Intake"},
    "bunker labs": {"status": "Open", "deadline": "Rolling Cohorts"},
    "sba sdvosb": {"status": "Open", "deadline": "Continuous Sourcing"},
    "va vr&e": {"status": "Open", "deadline": "Continuous Sourcing"},
    "audible podcast development": {"status": "Killed — window passed", "deadline": "Window passed"},
    "sundance documentary fund": {"status": "Killed — film only", "deadline": "Passed"},
    "podground creator micro-grant": {"status": "Killed — unverified", "deadline": "Rolling Cycles"},
    "third coast audio festival": {"status": "Verify cycle", "deadline": "Varies by Cycle"}
}

def main():
    print("=" * 75); print("🛡️ STARLIGHT AUDIT ASSIMILATION — LEDGER LOCK PROMPT")
    print("=" * 75)
    if not os.path.exists(SF): print("❌ System Error: Service account key missing."); sys.exit(1)
    
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        headers = [h.strip().lower() for h in ws.row_values(1)]
        print(f"    📊 Live Header Pre-Check: Discovered columns {headers}")
        
        name_idx = headers.index("grant name") + 1
        status_idx = headers.index("status") + 1
        deadline_idx = headers.index("public deadline") + 1
        
        rows = ws.get_all_values()
        updates_count = 0
        
        for row_num, row_data in enumerate(rows[1:], start=2):
            if not row_data or len(row_data) < name_idx:
                continue
                
            current_name = row_data[name_idx - 1].strip()
            current_name_lower = current_name.lower()
            
            for rule_key, rules in AUDIT_RULES.items():
                if rule_key in current_name_lower:
                    if "rename" in rules:
                        ws.update_cell(row_num, name_idx, rules["rename"])
                        print(f"    ✏️ Renamed row {row_num}: '{current_name}' ➔ '{rules['rename']}'")
                    
                    ws.update_cell(row_num, status_idx, rules["status"])
                    ws.update_cell(row_num, deadline_idx, rules["deadline"])
                    print(f"    ✅ Updated row {row_num} [{current_name}]: Status='{rules['status']}', Deadline='{rules['deadline']}'")
                    updates_count += 1
                    break
                    
        print("-" * 75); print(f"🟢 DATA ASSIMILATION COMPLETE: Synchronized {updates_count} spreadsheet cells."); print("=" * 75)
    except Exception as e: print(f"❌ Execution Fault: {e}"); sys.exit(1)

if __name__ == "__main__": main()
