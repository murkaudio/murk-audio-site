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

import os
import sys
from datetime import date
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials

ROLE_NAME = "butcher"
SYSTEM_PROMPT = "You are Butcher — Showrunner and Creative Director. Your job is to monitor audio production timelines, edit locks, and Foley recording bottlenecks. If a production asset is delayed, change your status cell string output to Flag or Alert."
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
