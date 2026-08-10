import os
import re
import json
import time
import datetime
import requests
import gspread
from google.oauth2.service_account import Credentials

# 🔐 Configuration Constants
SERVICE_ACCOUNT_FILE = "/Users/jameswilliams/murk-runners/service_account.json"
SPREADSHEET_ID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

TARGET_IDS = [
    "PROD-263", "PROD-264", "PROD-267", "PROD-273", "PROD-274", "PROD-275", 
    "PROD-277", "PROD-278", "PROD-279", "PROD-281", "PROD-283", "PROD-284", 
    "PROD-285", "PROD-286", "PROD-287", "PROD-290", "PROD-291", "PROD-293", 
    "PROD-310", "PROD-312", "PROD-314", "PROD-315", "PROD-316", "PROD-330"
]

def batch_gemini_gate_with_retry(candidates_batch: dict, max_retries: int = 3) -> dict:
    if not GEMINI_API_KEY:
        print("[-] Error: GEMINI_API_KEY is missing.")
        return {}

    system_prompt = (
        "You are the Zero-Trust Evaluation Gate (v6.24) for an automated audio production grant pipeline.\n"
        "Your task is to analyze a comprehensive batch of grant records simultaneously and determine their status verdicts.\n\n"
        "CURRENT SYSTEM DATE: Monday, June 22, 2026\n\n"
        "CRITICAL RULES FOR REJECTION (KILL):\n"
        "1. If the context notes state the grant explicitly covers visual art, writing about art (criticism/journalism instead of creation), or printmakers, KILL on DISCIPLINE.\n"
        "2. If the context explicitly notes it is entirely non-applicable to the applicant demographic (e.g. exclusively for female artists and the applicant is male), KILL on ENTITY.\n"
        "3. If the cycle is totally dead or confirmed non-viable for narrative audio production, KILL.\n"
        "Otherwise, if it is a strong, verified, pending, or monitored fit for the audio fiction project, return KEEP.\n\n"
        "OUTPUT JSON FORMAT: You must return a single unified raw JSON object mapping each separate task ID to its exact result schema with no markdown formatting wraps:\n"
        '{\n'
        '  "PROD-XXX": {"verdict": "KEEP" or "KILL", "axis_failed": "CHRONOLOGY"|"ENTITY"|"GEOGRAPHY"|"DISCIPLINE"|"SCHEMA"|"LIVENESS"|"NONE", "reasoning": "1-sentence reason."}\n'
        '}'
    )

    batch_text_payload = []
    for task_id, info in candidates_batch.items():
        batch_text_payload.append(f"Task ID: {task_id}\nTitle: {info['title']}\nExisting Notes: {info['notes']}\n---")
    
    full_user_input = "Analyze this batch collection of grant entries:\n\n" + "\n".join(batch_text_payload)
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_prompt}\n\n{full_user_input}"}]
        }],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    # 🔄 Retry loop handler
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[+] Connecting to Gemini API (Attempt {attempt}/{max_retries})...")
            res = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"}, timeout=35)
            
            if res.status_code == 200:
                raw_text = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                return json.loads(raw_text)
            elif res.status_code in [503, 429]:
                print(f"  [!] Server busy or high demand ({res.status_code}). Engaging backoff...")
                time.sleep(attempt * 5) # Spaced delay: 5s, 10s...
            else:
                print(f"[-] API Error Status: {res.status_code} - {res.text}")
                break
        except Exception as e:
            print(f"  [!] Connection flaw during transmit: {e}")
            time.sleep(5)
            
    return {}

def main():
    print(f"[*] Starting Resilient Batch Qualification Sequence: {datetime.datetime.now().isoformat()}")
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("[-] Fatal: Google credential layout array missing.")
        return

    spreadsheet = gspread.authorize(Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])).open_by_key(SPREADSHEET_ID)
    portfolio_sheet = spreadsheet.get_worksheet(0)
    all_rows = portfolio_sheet.get_all_values()
    
    headers = all_rows[0]
    id_col_idx = next(i for i, h in enumerate(headers, 1) if "id" in h.lower() or "prod" in h.lower())
    title_col_idx = next(i for i, h in enumerate(headers, 1) if "title" in h.lower() or "name" in h.lower())
    status_col_idx = next(i for i, h in enumerate(headers, 1) if "status" in h.lower() or "verdict" in h.lower() or "scope" in h.lower())
    notes_col_idx = next(i for i, h in enumerate(headers, 1) if "note" in h.lower() or "context" in h.lower())

    candidates_batch = {}
    for row_num, row_data in enumerate(all_rows[1:], start=2):
        while len(row_data) < len(headers):
            row_data.append("")
        task_id = row_data[id_col_idx - 1].strip()
        title = row_data[title_col_idx - 1].strip()
        notes = row_data[notes_col_idx - 1].strip()

        if task_id in TARGET_IDS:
            candidates_batch[task_id] = {"row_num": row_num, "title": title, "notes": notes}

    if not candidates_batch:
        print("[-] Zero target candidates discovered matching your list array.")
        return

    print(f"[+] Compiled {len(candidates_batch)} target items. Launching batch transmission...")
    batch_results = batch_gemini_gate_with_retry(candidates_batch)

    if not batch_results:
        print("[-] Error: Empty or broken payload returned after max retry capacity reached.")
        return

    print("[+] Batch verification payload received. Synchronizing sheet matrix values...")
    total_killed = 0
    total_preserved = 0

    for task_id, info in candidates_batch.items():
        row_num = info["row_num"]
        eval_data = batch_results.get(task_id)

        if not eval_data:
            continue
        
        verdict = eval_data.get("verdict", "KEEP")
        reasoning = eval_data.get("reasoning", "")
        axis_failed = eval_data.get("axis_failed", "NONE")

        if verdict == "KILL":
            print(f"  [-] Row {row_num} [{task_id}]: KILL Verdict applied (Axis: {axis_failed})")
            portfolio_sheet.update_cell(row_num, status_col_idx, "KILL")
            portfolio_sheet.update_cell(row_num, notes_col_idx, f"BATCH SANITIZATION | Fails Axis: {axis_failed} | Reason: {reasoning} | Previous Notes: {info['notes']}")
            total_killed += 1
        else:
            print(f"  [+] Row {row_num} [{task_id}]: Maintained as In Progress")
            portfolio_sheet.update_cell(row_num, status_col_idx, "In Progress")
            total_preserved += 1
        time.sleep(1.2)

    try:
        log_sheet = spreadsheet.worksheet("System_Log")
        all_log_ids = log_sheet.col_values(1)[1:]
        max_log_num = max([int(re.search(r"LOG-(\d+)", l).group(1)) for l in all_log_ids if re.search(r"LOG-(\d+)", l)] + [0])
        next_log_id = f"LOG-{str(max_log_num + 1).zfill(3)}"
        
        status_note = f"Status: Complete | Notes: High-speed resilient batch processing run finalized across {len(candidates_batch)} entries. {total_killed} items dropped to KILL, {total_preserved} rows maintained as active In Progress values."
        log_sheet.append_row([next_log_id, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-07:00"), "System_Log", next_log_id, "RUNNER_REPORT - Fault-Tolerant Batch Triage", "Operations Admin", status_note], value_input_option="USER_ENTERED")
        print(f"[✔] Telemetry logged to sheet as {next_log_id}.")
    except Exception as e:
        print(f"[-] Log Error: {e}")

    print(f"[*] Batch qualification cycle finished. Audited: {len(candidates_batch)} entries.")

if __name__ == "__main__":
    main()
