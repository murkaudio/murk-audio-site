import os
import re
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# System Infrastructure Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4'

def get_next_asset_id(sheet):
    """Parses Column A of Social_Vault to dynamically increment the master MKT-XXX tracking sequence."""
    try:
        col_a = sheet.col_values(1)
        ids = [int(re.search(r'MKT-(\d+)', x).group(1)) for x in col_a if re.search(r'MKT-(\d+)', x)]
        return max(ids) + 1 if ids else 1
    except Exception as e:
        print(f"[-] ID sequence scanner fallback triggered: {e}")
        return 5

def generate_noir_copy_package():
    """Generates the structured multi-line marketing copy package strings."""
    # Using explicit \\n escaping to safely bundle multi-line strings into a single row vector
    x_bluesky_copy = (
        "🔴 [GOVERNANCE] PENDING REVIEW\\n\\n"
        "The static on the line is growing thicker. A cold wind blowing through the circuits of a town that forgot how to care. "
        "Don't look into the shadows unless you're ready for what's looking back. 📻 #DeadSignal #NoirFiction"
    )
    return x_bluesky_copy

def main():
    print("[SYSTEM] Executing Runner Hughie Social Vault Integration Loop...")
    timestamp_now = datetime.now().strftime('%Y-%m-%d')
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[-] Fatal Error: Gspread credential file '{SERVICE_ACCOUNT_FILE}' missing.")
        return

    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        print(f"[-] API connection failed: {e}")
        return

    # Substring verification match to bypass zero-width character layout errors
    vault_sheet = next((s for s in sh.worksheets() if "Social_Vault" in s.title), None)
    if not vault_sheet:
        print("[-] Target worksheet 'Social_Vault' could not be resolved.")
        return

    # Compile copy text package elements
    copy_payload_escaped = generate_noir_copy_package()
    next_asset_index = get_next_asset_id(vault_sheet)
    asset_id = f"MKT-{next_asset_index:03d}"
    
    # Schema Column Mapping:
    # Asset_ID | Linked_Task_ID | Campaign_Target | Platform_Destination | Air_Date_Line | Asset_Status | Copy_Package_Text | Distribution_Link
    row_payload = [[
        asset_id,               # Column A
        "",                     # Column B (Unlinked to direct production tasks)
        "Dead Signal Launch",   # Column C
        "X / Bluesky",          # Column D
        timestamp_now,          # Column E
        "Drafted",              # Column F (Enforcing PI v6.20 review constraints)
        copy_payload_escaped,   # Column G (Pruned multi-line string text)
        ""                      # Column H (Pre-publication asset link spacer)
    ]]

    try:
        vault_sheet.append_rows(row_payload, value_input_option='USER_ENTERED')
        print(f"[+] Content Success: Social media copy package locked into Social_Vault under handle {asset_id}.")
    except Exception as e:
        print(f"[-] Social_Vault entry append operation failed: {e}")

if __name__ == '__main__':
    main()
