import os
import gspread
from google.oauth2.service_account import Credentials

# 🔐 1. Authentication and Sheet Initialization
SERVICE_ACCOUNT_FILE = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"

def apply_ui_validations():
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

    print("[+] Compiling interface modifications for Columns D and F...")

    # 🛠️ 2. Structure the Data Validation Rules
    validation_request = {
        "requests": [
            # Action A: Establish Dropdown Menu on Column D with "In Progress" (Rows 2 to 5000, Index 3)
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,      # Row 2 down
                        "endRowIndex": 5000,
                        "startColumnIndex": 3,   # Column D (0-indexed: A=0, B=1, C=2, D=3)
                        "endColumnIndex": 4
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [
                                {"userEnteredValue": "In Progress"},
                                {"userEnteredValue": "Complete"},
                                {"userEnteredValue": "Killed"},
                                {"userEnteredValue": "Backlog"},
                                {"userEnteredValue": "Parked"}
                            ]
                        },
                        "showCustomUi": True,    # Displays the clean dropdown arrow
                        "strict": False
                    }
                }
            },
            # Action B: Establish Calendar Picker on Column F (Rows 2 to 5000, Index 5)
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": 5000,
                        "startColumnIndex": 5,   # Column F (0-indexed: E=4, F=5)
                        "endColumnIndex": 6
                    },
                    "rule": {
                        "condition": {
                            "type": "DATE_IS_VALID"
                        },
                        "showCustomUi": True,    # Triggers the calendar interface pop-up
                        "strict": False
                    }
                }
            }
        ]
    }

    print("[+] Transmitting batch payload updates to Google Drive...")
    spreadsheet.batch_update(validation_request)
    print("[✔] Interface updated: Dropdown list corrected to 'In Progress'.")

if __name__ == "__main__":
    apply_ui_validations()
