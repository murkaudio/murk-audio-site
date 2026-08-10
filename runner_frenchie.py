import os
import re
import json
import time
import datetime
import requests
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_noir_social_post() -> str:
    if not GEMINI_API_KEY:
        return "Error: Missing Gemini API token authentication link."
    system_prompt = (
        "You are the Frenchie Social Marketing Engine (v2.0) for the audio fiction project 'Dead Signal'.\n"
        "Generate a highly compelling daily social media promotional post. You must strictly match this stylistic footprint:\n\n"
        "STYLE: 1951 Portland Noir. Rain-slicked cobblestones, neon signs bleeding through the evening fog, low-key shadows, smoky jazz bars, and hard-boiled mystery grit.\n"
        "PROJECT: 'Dead Signal' — a dark, serialized narrative audio thriller.\n"
        "TONE: Enigmatic, cinematic, tense, atmospheric.\n"
        "FORMATTING: Include a clear introductory prefix line, followed by fluid paragraph text utilizing carriage returns, and end with targeted clean hashtags.\n\n"
        "REQUIRED HASHTAGS: #DeadSignal #NoirFiction #AudioDrama #PortlandNoir\n\n"
        "Return ONLY the plain text copy block ready for immediate scheduling."
    )
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    try:
        res = requests.post(api_url, json={"contents": [{"parts": [{"text": system_prompt}]}], "generationConfig": {"temperature": 0.65}}, headers={"Content-Type": "application/json"}, timeout=20)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"[-] Gemini content generation fault: {e}")
    return "🔴 [GOVERNANCE] PENDING REVIEW\n\nThe signal pulses in the dark. Rain keeps hitting the glass. Listen close. #DeadSignal #NoirFiction"

def main():
    print("==================================================")
    print("⚡ RUNNING FRENCHIE SOCIAL ENGINE — LIVE VAULT SYNC")
    print("==================================================")
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("[-] Fatal: Google credentials array missing.")
        return
    gc = gspread.authorize(Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]))
    vault_sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("Social_Vault")
    all_rows = vault_sheet.get_all_values()
    headers = [h.strip().lower() for h in all_rows[0]]
    try:
        id_idx = headers.index("asset_id")
        task_idx = headers.index("linked_task_id")
        target_idx = headers.index("campaign_target")
        dest_idx = headers.index("platform_destination")
        date_idx = headers.index("air_date_line")
        status_idx = headers.index("asset_status")
        copy_idx = headers.index("copy_package_text")
    except ValueError as e:
        print(f"[-] Structural Layout Mismatch: Column mapping failed: {e}")
        return
    max_id_num = 0
    for row in all_rows[1:]:
        if len(row) > id_idx:
            match = re.search(r"MKT-(\d+)", str(row[id_idx]))
            if match:
                max_id_num = max(max_id_num, int(match.group(1)))
    next_asset_id = f"MKT-{str(max_id_num + 1).zfill(3)}"
    print(f"[+] Current scale verified. Compiling tracking matrix row for {next_asset_id}...")
    generated_copy = generate_noir_social_post()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    new_row = [""] * len(headers)
    new_row[id_idx] = next_asset_id
    new_row[task_idx] = "PROD-356"
    new_row[target_idx] = "Dead Signal Launch"
    new_row[dest_idx] = "X / Bluesky / Instagram"
    new_row[date_idx] = today_str
    new_row[status_idx] = "Pending Review"
    new_row[copy_idx] = f"🔴 [GOVERNANCE] PENDING REVIEW\n\n{generated_copy}"
    vault_sheet.append_row(new_row, value_input_option="USER_ENTERED")
    print(f"[✔] SUCCESS: Aligned row vector written to Social_Vault as {next_asset_id}.")
if __name__ == "__main__":
    main()
