#!/usr/bin/env python3
import os, json
from datetime import date
from dotenv import load_dotenv
from google import genai
import gspread
from google.oauth2.service_account import Credentials

load_dotenv(dotenv_path=os.path.expanduser("~/murk-runners/.env"))

SYSTEM_PROMPT = """You are Firecracker, Drive Audit runner for The Murk Audio LLC. You run Fridays only.
Every Friday return ONLY a JSON object with exactly these fields:
- role: "Firecracker"
- date: today's date in YYYY-MM-DD format
- status: one of "Complete" or "Flag"
- notes: audit reminder — flag any non-conforming file names per TheMurk_FileNamingConvention_v1_20260507.md. If no issues known, write "Audit complete — no flags."
No preamble. JSON only."""

SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SA_PATH = os.path.expanduser("~/murk-runners/service_account.json")

def main():
    print(f"[Firecracker] Starting — {date.today().isoformat()}")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Today is {date.today().isoformat()}. Execute your task.",
        config=genai.types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
    )
    raw = response.text.strip().replace("```json","").replace("```","").strip()
    payload = json.loads(raw)
    print(f"[Firecracker] Gemini response: {payload}")
    creds = Credentials.from_service_account_file(SA_PATH, scopes=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"])
    gc = gspread.authorize(creds)
    ws = gc.open_by_key(SHEET_ID).sheet1
    ws.append_row([payload["date"], payload["role"], payload["status"], payload["notes"]])
    print(f"[Firecracker] Row written to Google Sheet")
    print(f"[Firecracker] DONE")

if __name__ == "__main__":
    main()
