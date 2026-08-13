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
import os, json
from datetime import date
from dotenv import load_dotenv
from google import genai
import gspread
from google.oauth2.service_account import Credentials

load_dotenv(dotenv_path=os.path.expanduser("~/murk-runners/.env"))

SYSTEM_PROMPT = """You are Starlight, Grants runner for The Murk Audio LLC.
Every night return ONLY a JSON object with exactly these fields:
- role: "Starlight"
- date: today's date in YYYY-MM-DD format
- status: one of "Complete" or "Alert"
- notes: check for grant deadlines within 10 days (internal deadline = public minus 10 days). If none, write "Pipeline clear."
No preamble. JSON only."""

SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SA_PATH = os.path.expanduser("~/murk-runners/service_account.json")

def main():
    print(f"[Starlight] Starting — {date.today().isoformat()}")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Today is {date.today().isoformat()}. Execute your task.",
        config=genai.types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    raw = response.text.strip().replace("```json","").replace("```","").strip()
    payload = json.loads(raw)
    print(f"[Starlight] Gemini response: {payload}")
    creds = Credentials.from_service_account_file(SA_PATH, scopes=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"])
    gc = gspread.authorize(creds)
    ws = gc.open_by_key(SHEET_ID).sheet1
    ws.append_row([payload["date"], payload["role"], payload["status"], payload["notes"]])
    print(f"[Starlight] Row written to Google Sheet")
    print(f"[Starlight] DONE")

if __name__ == "__main__":
    main()
