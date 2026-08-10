import os
import gspread
from google.oauth2.service_account import Credentials

# 🔐 1. Authentication and Sheet Initialization
SERVICE_ACCOUNT_FILE = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"

def clean_and_align_column_f():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[-] Fatal Error: Gspread credential file missing at {SERVICE_ACCOUNT_FILE}")
        return

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    
    print(f"[+] Connected to Google API. Accessing primary tab...")
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    sheet = spreadsheet.get_worksheet(0)
    sheet_id = sheet.id
    
    # 🧼 2. Fetch Data and Strip Text-Forcing Apostrophes from Column F (Index 5)
    all_rows = sheet.get_all_values()
    if not all_rows:
        print("[-] Sheet is empty.")
        return
        
    print("[+] Scanning Column F data for formatting corrections...")
    
    cleaned_values = []
    # Skip header row (index 0) and iterate through data matrix
    for row in all_rows[1:]:
        val = row[5].strip() if len(row) > 5 else ""
        
        # Remove literal and hidden string-forcing escape characters
        if val.startswith("'"):
            val = val[1:]
        val = val.replace("'", "")
        
        cleaned_values.append([val])
        
    end_row = len(all_rows)
    range_target = f"F2:F{end_row}"
    
    print(f"[+] Overwriting {range_target} with clean date string formats...")
    sheet.update(range_target, cleaned_values, value_input_option='USER_ENTERED')
    
    # 📐 3. Force Right-Alignment Rule on Column F Grid Box (Rows 2 to 5000)
    print("[+] Compiling alignment request. Shifting Column F alignment to RIGHT...")
    align_request = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,      # Row 2 down (preserves header style)
                        "endRowIndex": 5000,     # Safe execution boundary cap
                        "startColumnIndex": 5,   # Column F (0-indexed: A=0, B=1, C=2, D=3, E=4, F=5)
                        "endColumnIndex": 6
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "RIGHT"
                        }
                    },
                    "fields": "userEnteredFormat.horizontalAlignment"
                  }
            }
        ]
    }
    
    spreadsheet.batch_update(align_request)
    print("[✔] Column F is now completely stripped of string headers and snapped right.")

if __name__ == "__main__":
    clean_and_align_column_f()
