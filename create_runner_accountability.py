import datetime
import gspread
from google.oauth2.service_account import Credentials

# System Infrastructure Maps
SERVICE_ACCOUNT_PATH = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

def main():
    try:
        # Secure API Handshake Initialization
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID)
        
        ws = sheet.worksheet("Runner_Accountability")
        print("ℹ️ Tab 'Runner_Accountability' already exists. Appending rows.")
        
        # Build Date-Aware Context Baseline
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        # Extract existing log rows to build today's composite deduplication key
        all_values = ws.get_all_values()
        existing_today_runners = {
            row[1].strip() for row in all_values 
            if len(row) > 1 and row[0] == today_str
        }
        
        # Core Operational Runner Data Matrix
        runners_data = [
            ["Starlight", "Automated Runner", "🟢 Complete", "Automated grants_scraper.py executed cleanly across regional foundation nodes. Checked rows 96/98/107/111, pre-qualifying 11 active entries to lock the critical path ahead of the June 12 session."],
            ["Ashley", "Core Role", "🟢 Complete", "Successfully finalized the priority distributor runtime compliance scan at T0. Confirmed that Dead Signal's 7-minute footprint meets all Apple, Spotify, Buzzsprout, and Sonic Society placement rules."],
            ["Frenchie Social Runner", "Automated Runner", "🟢 Complete", "Nightly promotional campaign sequence executed with zero failures. Following Soldier Boy's prompt upgrade, copy successfully locked into the required 1951 Portland noir register, clearing all Julie gate constraints."],
            ["Business Manager", "Automated Agent", "🟢 Complete", "Completed automated midnight ledger balance cross-check loops. Confirmed accurate asset allocations and flagged zero anomalous transaction profiles."],
            ["Kimiko", "Core Role", "🟢 Complete", "Soft presence monitoring active. Routine system checks and background connection stability validations completed with zero exception flags."],
            ["Mother's Milk (MM)", "Core Role", "🟢 Complete", "Reconciled transaction histories and successfully mapped Chase link unbenched liabilities to the primary Relay operating cash vault to prepare for travel."]
        ]
        
        # Deduplicate and Append Loop Execution
        for runner in runners_data:
            name = runner[0]
            if name in existing_today_runners:
                print(f" ℹ️ Log row for '{name}' already present today, skipping.")
            else:
                # Direct Database Append Mapping: Date, Runner/Role, Type, Status, Notes
                ws.append_row([today_str, runner[0], runner[1], runner[2], runner[3]])
                print(f" 💾 Committed accountability log: {name}")
                
        print("==> 🟢 ACCOUNTABILITY MATRIX ACTIVE: Tab configured and updated successfully!")

    except Exception as e:
        print(f"[CRITICAL ERROR] Execution aborted: {str(e)}")

if __name__ == "__main__":
    main()
