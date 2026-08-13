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
murk_session_update_20260610.py
The Murk Audio LLC — Master Google Sheet Session Update
Session: June 10, 2026
Writes all session decisions to the master Google Sheet with correct schema maps.
"""

import os
import sys
import gspread
from google.oauth2.service_account import Credentials

# ── CONFIG ────────────────────────────────────────────────────────────────────
SERVICE_ACCOUNT_PATH = os.path.expanduser("~/murk-runners/service_account.json")
SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── AUTH ──────────────────────────────────────────────────────────────────────
def authenticate():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_or_create_tab(sheet, name):
    try:
        return sheet.worksheet(name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"  [WARN] Tab '{name}' not found — creating it.")
        return sheet.add_worksheet(title=name, rows=200, cols=20)

def find_row_by_value(ws, col_index, value):
    col = ws.col_values(col_index)
    for i, cell in enumerate(col):
        if cell.strip() == value.strip():
            return i + 1
    return None

def update_cell_by_task(ws, task_name, col_index, new_value, task_col=1):
    row = find_row_by_value(ws, task_col, task_name)
    if row:
        ws.update_cell(row, col_index, new_value)
        print(f"  ✅ Updated '{task_name}' col {col_index} → {new_value}")
    else:
        print(f"  ⚠️  Task not found in sheet: '{task_name}'")

def append_if_not_exists(ws, unique_col, unique_value, row_data):
    existing = ws.col_values(unique_col)
    if unique_value in existing:
        print(f"  ⏭️  Already exists, skipping: '{unique_value}'")
    else:
        ws.append_row(row_data, value_input_option="USER_ENTERED")
        print(f"  ✅ Appended: '{unique_value}'")

# ── TAB UPDATES ───────────────────────────────────────────────────────────────

def update_task_queue(sheet):
    print("\n📋 TASK_QUEUE")
    ws = get_or_create_tab(sheet, "Task_Queue")

    status_updates = [
        ("NQD / Snow Blood — reframe outreach angle before Week 1 follows", "Killed"),
        ("The White Vault — remove from active swap list or reclassify", "Killed"),
        ("MM financial documents — grants session prep", "Complete"),
        ("Soldier Boy — KS competitive intelligence scraper", "Complete"),
        ("AIR Grant Opportunities Directory — audit and surface qualifying grants", "Complete"),
        ("AIR Grant Opportunities Airtable — browse and pre-qual all audio fiction entries", "Complete"),
    ]
    for task, status in status_updates:
        update_cell_by_task(ws, task, 4, status)

    new_entries = [
        ["Ashley — fiction network / distributor minimum runtime scan", "Ashley", "June 17, 2026", "Queued", "June 10, 2026", "June 14, 2026", "", "Governance Framework", "Surfaced June 10 after Dead Signal EP1 landed at ~7 minutes. Need to confirm whether fiction networks (Sonic Society, Buzzsprout, Apple Podcasts, Spotify) have minimum episode length requirements that would affect Dead Signal placement or distribution eligibility. Any threshold above 7 minutes is a risk item requiring immediate escalation."],
        ["SBU remote recording minimum spec", "Soldier Boy", "June 21, 2026", "Queued", "June 10, 2026", "June 20, 2026", "", "Static Between Us — Production", "SBU is going remote-only due to no pre-KS budget. Actors submit home-recorded lines individually. A minimum home recording standard must be defined and published in the casting call so submissions are usable in post. Soldier Boy defines the spec covering mic standard, room treatment, file format, sample rate, and delivery method. Mid-point review moved to June 20 to accommodate James travel June 15-19."],
        ["Chase Ink — set up autopay from Relay *2576 before travel", "James", "June 14, 2026", "Queued", "June 10, 2026", "June 13, 2026", "", "Governance Framework", "James is out of country June 15-19. Chase Ink *0063 payment of $1,004.97 is due June 19. Autopay from Relay *2576 must be confirmed active before departure on June 15. MM to confirm Relay *2576 balance is sufficient by June 13. Calendar reminder created for June 14 at 9AM PT."],
        ["FA decision June 12 — activate AIR StoryFund pipeline entry or kill it", "James", "June 12, 2026", "Queued", "June 10, 2026", "June 12, 2026", "", "Fiscal Sponsorship Pipeline", "Fractured Atlas fiscal sponsorship decision expected June 12. If FA approves, the AIR StoryFund entry in Fiscal_Sponsorship_Pipeline is killed — no longer needed. If FA declines, AIR StoryFund activates immediately as the backup fiscal sponsor path. James confirms outcome and updates pipeline same session."],
        ["Monthly Micro-Grants — Making Waves — apply before June 30", "James", "June 20, 2026", "Queued", "June 10, 2026", "June 16, 2026", "", "Grants Pipeline", "Rolling monthly grant for independent podcasters from Content is Queen. July 2026 theme is Making Waves — strong fit for Dead Signal and The Murk brand story. Applications open June 16, public deadline June 30, internal deadline June 20 to give James time to review and submit after returning from travel. Disabled individuals strongly encouraged to apply — James qualifies. Starlight drafts application on June 16 when window opens."],
        ["Frenchie runner prompt — fix Dead Signal register to noir", "Soldier Boy", "June 10, 2026", "Queued", "June 10, 2026", "June 11, 2026", "", "Governance Framework", "Frenchie's nightly cowork runner is producing Dead Signal social copy in a sci-fi/cosmic horror register. Dead Signal is noir — Portland, 1951, rain, shadows, detective, hardboiled. Soldier Boy must update Frenchie's runner prompt tonight to explicitly lock the Dead Signal register as noir only. No sci-fi, no cosmic horror, no void/space/signal-from-space language. Julie gate language must be included in the prompt. Verify Social_Vault output register is correct on June 11 morning run."],
    ]
    for entry in new_entries:
        append_if_not_exists(ws, 1, entry[0], entry)

def update_air_grants_pipeline(sheet):
    print("\n🎯 AIR_GRANTS_PIPELINE")
    ws = get_or_create_tab(sheet, "AIR_Grants_Pipeline")
    
    headers = ws.row_values(1)
    if not headers or headers[0] != "Grant Name":
        ws.insert_row([
            "Grant Name", "Funder / Org", "Geography", "Fits LLC?", 
            "Status", "Public Deadline", "Internal Deadline Safety Gate"
        ], 1)
        print("  ✅ Header row verified and locked.")

    grants = [
        ["Oregon Arts Commission — Individual Artist Fellowship", "Oregon Arts Commission", "Oregon", "Yes", "Qualified", "August 1, 2026", "July 22, 2026"],
        ["RACC — Portland Arts Project Grant", "Regional Arts & Culture Council", "Portland, Oregon", "Yes", "Monitor — cycle closed", "Fall 2026", "TBD"],
        ["Miller Foundation — Arts & Culture", "Miller Foundation Oregon", "Oregon", "Conditional", "Pending", "Check current cycle", "10 days prior to deadline"],
        ["AIR StoryFund — Fiscal Sponsorship", "Association of Independents in Radio (AIR)", "National", "Yes", "Conditional", "Rolling", "June 13, 2026"],
        ["Monthly Micro-Grants — Making Waves (Content is Queen)", "Content is Queen", "Global", "Yes", "Qualified — fast track", "June 30, 2026", "June 20, 2026"],
        ["Audible Podcast Development Program", "Audible", "National", "Yes", "Monitor — watch for next cycle", "Window passed", "10 days prior to deadline"],
        ["Inevitable Foundation — Elevate for Podcasters", "Inevitable Foundation", "National", "Yes", "Monitor — watch for reactivation", "No 2026 cycle announced", "10 days prior to deadline"],
        ["Awesome Foundation Portland — submitted", "Awesome Foundation", "Portland, Oregon", "Yes", "Submitted — awaiting decision", "Rolling monthly", "Already submitted"],
        ["Podfund — startup and growth capital", "Podfund", "National", "Yes", "Parked — revisit October 2026", "Rolling", "Post-KS close"],
        ["AIR Localore / Finding America", "Association of Independents in Radio (AIR)", "National", "N/A", "Killed — program ended 2018", "N/A", "N/A"],
        ["Wave / Shorty Awards Elevate Creatives Fund", "Wave + Shorty Awards", "National", "Medium", "Killed — 2026 cycle not open", "N/A", "N/A"],
    ]
    for grant in grants:
        append_if_not_exists(ws, 1, grant[0], grant)

def update_fiscal_sponsorship_pipeline(sheet):
    print("\n💼 FISCAL_SPONSORSHIP_PIPELINE")
    ws = get_or_create_tab(sheet, "Fiscal_Sponsorship_Pipeline")
    headers = ws.row_values(1)
    if not headers or headers[0] != "Organization":
        ws.insert_row(["Organization", "Contact", "Status", "Next Action", "Next Action Date", "Narrative"], 1)

    entries = [
        ["Fractured Atlas", "fracturedatlas.org", "Decision expected June 12, 2026", "Monitor for decision email. If approved: update KS + Patreon framing. If declined: activate AIR StoryFund.", "June 12, 2026", "Fiscal sponsorship application submitted. Decision expected around June 12. If approved, Miller Foundation and other 501c3-gated grants become accessible. If declined, AIR StoryFund is the immediate backup path."],
        ["NW Documentary", "sam@nwdocumentary.org", "Active — meeting proposed week of June 22", "Monitor for Sam's confirmation of June 22 week meeting. James out of country prior week.", "June 22, 2026", "Sam Gaty at NW Documentary responded positively June 9. James proposed meeting week of June 22 (out of country prior week). Thread is active and in a good holding pattern. Zoom or in-person both acceptable per Sam. Replied from hello@murk.audio."],
        ["AIR StoryFund", "airmedia.org/fiscal-sponsorship", "Conditional — activate if Fractured Atlas declines June 12", "Await FA decision June 12. If FA declines, assess AIR membership cost and onboarding timeline immediately.", "June 13, 2026", "AIR StoryFund is the backup fiscal sponsorship path if Fractured Atlas declines. Requires AIR membership first (membership cost TBD). 10-15% admin fee on funds received. Audio drama qualifies under mission-driven independent audio. Added to pipeline June 10 as conditional entry."],
        ["NW Film Center", "nwfilm.org", "Monitor — formal inquiry assigned to MM", "MM to send formal fiscal sponsorship inquiry. Due June 11.", "June 11, 2026", "NW Film Center is a potential fiscal sponsor with arts and media focus in the Pacific Northwest. MM owns the formal inquiry. Task in TQ due June 11. No contact made yet."],
    ]
    for entry in entries:
        append_if_not_exists(ws, 1, entry[0], entry)

def update_contact_monitor(sheet):
    print("\n📡 CONTACT_MONITOR")
    ws = get_or_create_tab(sheet, "Contact_Monitor")
    headers = ws.row_values(1)
    if not headers or headers[0] != "Contact":
        ws.insert_row(["Contact", "Email", "Last Contact Date", "Last Outcome", "Next Trigger", "Status", "Narrative"], 1)

    entries = [
        ["Sam Gaty — NW Documentary", "sam@nwdocumentary.org", "June 10, 2026", "James replied proposing meeting week of June 22. Sam had offered Tue-Thu flexibility.", "Sam confirms or proposes specific date for week of June 22", "Active — holding", "Fiscal sponsorship outreach target. Sam responded positively June 9 after James's outreach. James replied June 10 proposing week of June 22 (out of country prior week). Thread is live. No further action needed until Sam confirms."],
        ["Eric Stolberg — Digital One", "eric@digone.com", "June 9, 2026", "Sound design session completed June 9. EP1 background and sound effects done. Eric holds all files at Digital One.", "Eric shares editing program with James. Next session tentative June 24.", "Active — post-session", "Primary sound designer for Dead Signal. Recording completed June 2. Sound design session June 9 — EP1 background and effects complete. Eric holds all files at Digital One and will share an editing program with James for remote edits during travel. Next session tentative June 24 for EP2 and EP3."],
        ["Chase Ink Business — *0063", "chase.com", "June 10, 2026", "Statement confirmed: $1,004.97 balance, $40 minimum, due June 19.", "Autopay setup confirmation before June 15 departure.", "Action required — June 14", "Chase Ink Business Cash card. June statement balance $1,004.97 due June 19. James is out of country June 15-19. Autopay from Relay *2576 must be set up before departure. Calendar reminder created June 14 9AM PT. MM to confirm Relay balance sufficient by June 13."],
        ["Sonic Society", "sonicsociety@gmail.com", "May 30, 2026", "Dead Signal confirmed for Season 22 opener. Follow-up needed August 1 to confirm delivery format.", "August 1, 2026 — confirm whether Jack wants one MP3 or three separate episode files.", "Monitor — August 1 trigger", "Dead Signal confirmed for Sonic Society Season 22 opener, projected September 2026. Three consecutive weekly broadcast slots likely. Follow up August 1 to clarify whether Jack wants one combined MP3 or three separate episode files for serialized broadcast."],
    ]
    for entry in entries:
        append_if_not_exists(ws, 1, entry[0], entry)

def update_project_portfolio(sheet):
    print("\n📁 PROJECT_PORTFOLIO")
    ws = get_or_create_tab(sheet, "Project_Portfolio")
    updates = [
        ("Dead Signal — Production", "🟢 Green", "Sound design begins June 23 (Eric). James edits due June 23. Trailer first in queue. EP1 runtime ~7 min — accepted as-is. No rerecord."),
        ("Static Between Us — Production", "🟡 Yellow", "Scripts lock June 12 (T-2). Casting opens June 22. Remote recording format confirmed. Soldier Boy spec due June 21. Studio booking deferred post-KS close."),
        ("Grants Pipeline", "🟡 Yellow", "June 12 grants session prepped. Starlight executing rows 96/98/107/111. AIR_Grants_Pipeline tab is now the single source of truth. 8 entries researched and pre-qualified June 10."),
        ("Fiscal Sponsorship Pipeline", "🟡 Yellow", "Fractured Atlas decision expected June 12. NW Documentary meeting week of June 22. AIR StoryFund added as conditional backup. NW Film Center inquiry due June 11 (MM)."),
        ("Kickstarter Campaigns", "🟢 Green", "KS launches July 4. Facebook Page due July 3 (Hughie). Self-pledge $2,500 July 4. KS competitive intelligence scraper confirmed complete."),
        ("Governance Framework", "🟢 Green", "Master Google Sheet confirmed as single source of truth June 10. All Notion references retired. New tabs created: Ashley_Intel, Fiscal_Sponsorship_Pipeline, Contact_Monitor, Financial_Ledger. Sheet ID confirmed."),
    ]
    headers = ws.row_values(1)
    rag_col, milestone_col = None, None
    if headers:
        for i, h in enumerate(headers):
            if "RAG" in h: rag_col = i + 1
            if "Milestone" in h or "Next" in h: milestone_col = i + 1

    for project, rag, milestone in updates:
        row = find_row_by_value(ws, 1, project)
        if row:
            if rag_col: ws.update_cell(row, rag_col, rag)
            if milestone_col: ws.update_cell(row, milestone_col, milestone)
            print(f"  ✅ Updated: {project}")

def update_state_log(sheet):
    print("\n📋 STATE_LOG")
    ws = get_or_create_tab(sheet, "State_Log")
    headers = ws.row_values(1)
    if not headers or headers[0] != "Date":
        ws.insert_row(["Date", "Location", "Top 3", "Session Accomplishments", "Behavioral Changes", "Carry / Next Steps"], 1)

    entry = [
        "2026-06-10", "Portland — Home Office",
        "1. Grants cluster assigned + pipeline built | 2. SBU remote recording confirmed + casting timeline locked | 3. Master Google Sheet governance rule locked",
        "Checkin complete. KS scraper closed. MM financial docs closed. Butcher session: Dead Signal EP1 runtime accepted ~7 min, 10-min floor locked for future productions. Production SOP v1.1 delivered. SBU casting timeline locked (opens June 22). Remote recording confirmed, Soldier Boy spec due June 21. Ashley runtime scan TQ entry written. Grants cluster fully assigned — Starlight executing rows 96/98/107/111. AIR_Grants_Pipeline shortlist built — 10+ entries researched and pre-qualified. RACC killed (cycle closed). AIR Localore killed (defunct). Wave/Shorty killed (2026 cycle not open). Awesome Foundation confirmed submitted May 29. Making Waves micro-grant added (opens June 16, internal deadline June 20). AIR StoryFund added as conditional fiscal sponsor backup. Chase autopay calendar event created June 14. Rows 100/106 killed/removed. Frenchie runner fix TQ entry written. Master Google Sheet governance rule locked — single source of truth. New tabs confirmed: Ashley_Intel, Fiscal_Sponsorship_Pipeline, Contact_Monitor, Financial_Ledger. Narrative rule locked for all tabs. Correct Sheet ID confirmed. PI v6.10 produced — all Notion references purged.",
        "1. Notion retired — master Google Sheet is single source of truth. 2. All TQ entries and pipeline rows require plain-language narrative description. 3. Sheet ID corrected in PI. 4. New tabs active: Ashley_Intel, Fiscal_Sponsorship_Pipeline, Contact_Monitor, Financial_Ledger. 5. SBU remote recording confirmed as pre-KS format. 6. Production SOP v1.1 locked — 10-min runtime floor, remote recording workflow. 7. Dead Signal EP1-3 runtime accepted as-is.",
        "June 11: SBU scripts final review + sign-off. Confirm Starlight grants runs in sheet. Frenchie runner fix verify. June 12: Grants session + FA decision. June 14: Chase autopay setup. June 16: Making Waves grant opens — Starlight drafts. June 20: James submits Making Waves. June 21: Soldier Boy remote spec due. June 22: SBU casting opens + NW Documentary meeting."
    ]
    append_if_not_exists(ws, 1, "2026-06-10", entry)

def update_ashley_intel(sheet):
    print("\n🔍 ASHLEY_INTEL")
    ws = get_or_create_tab(sheet, "Ashley_Intel")
    headers = ws.row_values(1)
    if not headers or headers[0] != "Date":
        ws.insert_row(["Date", "Category", "Finding", "Source", "Action Required", "Narrative"], 1)

    entries = [
        ["2026-06-10", "Runtime Risk", "Dead Signal EP1 landed at ~7 minutes against a 15-minute target. Fiction networks and distributors may have minimum episode length requirements.", "Session — Butcher creative brief June 10", "Run targeted scan on fiction network minimum runtime thresholds. Due June 17. Focus: Sonic Society, Buzzsprout, Apple Podcasts, Spotify. Flag any threshold above 7 minutes as risk item.", "Surfaced during Butcher session June 10. EP1 actual runtime ~7 minutes vs 15-minute target. If Sonic Society or major distribution platforms have a minimum episode length floor above 7 minutes, Dead Signal's placement or featured eligibility could be affected. Ashley to confirm or kill this risk before next Eric session June 24."],
        ["2026-06-10", "Remote Recording Standards", "SBU is adopting remote recording format. Indie audio drama community has established norms for home recording specs.", "Session — Butcher creative brief June 10", "Research what comparable indie audio drama productions specify for home recording. Inform Soldier Boy spec. Due June 17.", "SBU actors will submit home-recorded lines. Soldier Boy is building the minimum spec for the casting call. Ashley to surface what comparable productions (within the indie audio drama community) are requiring so the spec lands in the right range and doesn't exclude strong talent."]
    ]
    for entry in entries:
        append_if_not_exists(ws, 3, entry[2], entry)

def update_financial_ledger(sheet):
    print("\n💰 FINANCIAL_LEDGER")
    ws = get_or_create_tab(sheet, "Financial_Ledger")
    headers = ws.row_values(1)
    if not headers or headers[0] != "Date":
        ws.insert_row(["Date", "Type", "Description", "Amount", "Account", "Due Date", "Status", "Narrative"], 1)

    entries = [
        ["2026-06-10", "Liability — Payment Due", "Chase Ink Business Cash *0063 — June statement balance", "$1,004.97", "Chase Ink *0063 → Relay *2576", "June 19, 2026", "Pending — autopay setup required before June 15", "Chase Ink Business Cash statement confirmed June 10. Balance $1,004.97, minimum $40, due June 19. James is out of country June 15-19. Autopay from Relay *2576 must be set up before departure. Calendar reminder June 14 9AM PT. MM to confirm Relay *2576 balance sufficient by June 13."]
    ]
    for entry in entries:
        append_if_not_exists(ws, 3, entry[2], entry)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("MURK SESSION UPDATE — June 10, 2026")
    print("Master Google Sheet:", SHEET_ID)
    print("=" * 60)

    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"\n❌ Service account not found at: {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)

    print("\n🔐 Authenticating...")
    try:
        sheet = authenticate()
        print(f"  ✅ Connected to: {sheet.title}")
    except Exception as e:
        print(f"  ❌ Authentication failed: {e}")
        sys.exit(1)

    update_task_queue(sheet)
    update_air_grants_pipeline(sheet)
    update_fiscal_sponsorship_pipeline(sheet)
    update_contact_monitor(sheet)
    update_project_portfolio(sheet)
    update_state_log(sheet)
    update_ashley_intel(sheet)
    update_financial_ledger(sheet)

    print("\n" + "=" * 60)
    print("✅ SESSION UPDATE COMPLETE — June 10, 2026")
    print("All tabs written. Verify in Google Sheets.")
    print("=" * 60)

if __name__ == "__main__":
    main()
