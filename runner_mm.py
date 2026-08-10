import os
import sys
from datetime import date
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials

ROLE_NAME = "mm"
SYSTEM_PROMPT = "You are MM — Business Manager and Legal Compliance Officer for The Murk Audio LLC. Your job is to monitor cash runway metrics, grant budgeting caps, and federal/state filing timelines. Keep your assessment high-density, risk-aware, and focused on regulatory safety layers."
USER_INPUT = "Execute your daily check-in and summarize active files."

# 🛰️ SYSTEM-WIDE ENVIRONMENT KEY SECURITY LAYER
if "GEMINI_API_KEY" not in os.environ:
    for p in ["~/.zshrc", "~/.bash_profile", "~/.profile", "~/murk-runners/.env"]:
        path = os.path.expanduser(p)
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    if "GEMINI_API_KEY" in line and "=" in line:
                        val = line.split("=", 1)[1].strip()
                        val = val.replace("export", "").strip()
                        val = val.strip("'").strip('"')
                        os.environ["GEMINI_API_KEY"] = val
                        break

SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SA_PATH = os.path.expanduser("~/murk-runners/service_account.json")

def run_agent():
    today_str = date.today().isoformat()
    print(f"[{ROLE_NAME.upper()}] Initializing background pass for {today_str}...")
    
    if "GEMINI_API_KEY" not in os.environ or not os.environ["GEMINI_API_KEY"]:
        print(f"[{ROLE_NAME.upper()}] Critical Error: GEMINI_API_KEY variable is missing or empty.")
        return
        
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)
    
    try:
        response = model.generate_content(USER_INPUT)
        notes_output = response.text.strip()
        status_flag = "Complete"
    except Exception as e:
        notes_output = f"Gemini API Execution Failure: {str(e)}"
        status_flag = "Alert"

    try:
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(SA_PATH, scopes=scopes)
        gc = gspread.authorize(creds)
        ws = gc.open_by_key(SHEET_ID).sheet1
        ws.append_row([today_str, ROLE_NAME, status_flag, notes_output])
        print(f"[{ROLE_NAME.upper()}] DONE")
    except Exception as e:
        print(f"[{ROLE_NAME.upper()}] Google Sheets Logging Failure: {e}")

if __name__ == "__main__":
    run_agent()
