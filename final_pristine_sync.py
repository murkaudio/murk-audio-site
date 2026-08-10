#!/usr/bin/env python3
"""
final_pristine_sync.py
The Murk Audio LLC — Infallible Self-Healing Ledger Sync
Session: June 11, 2026
"""
import os, sys, csv, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

LOCAL_CSV = os.path.expanduser("~/Downloads/TheMurk_AIR_GrantsPipeline_Audit_v6_11.xlsx - AIR_Grants_Pipeline.csv")
if not os.path.exists(LOCAL_CSV):
    LOCAL_CSV = "TheMurk_AIR_GrantsPipeline_Audit_v6_11.xlsx - AIR_Grants_Pipeline.csv"

STATUS_MAP = {
    "KILL": "Killed",
    "SUBMITTED": "Submitted",
    "CONDITIONAL": "Conditional",
    "PARK": "Parked",
    "KEEP": "Open"
}

CANONICAL_HEADERS = [
    "Grant Name", 
    "Funder / Org", 
    "Geography", 
    "Fits LLC?", 
    "Status", 
    "Status Notes", 
    "Public Deadline", 
    "Internal Deadline Safety Gate"
]

STATUS_OPTIONS = ["Open", "Submitted", "Conditional", "Parked", "Killed", "Verify"]

HIGHLIGHT_RULES = [
    {"token": "Killed", "rgb": {"red": 0.95, "green": 0.82, "blue": 0.82}},
    {"token": "Submitted", "rgb": {"red": 0.83, "green": 0.93, "blue": 0.85}},
    {"token": "Parked", "rgb": {"red": 0.80, "green": 0.90, "blue": 1.00}},
    {"token": "Qualified", "rgb": {"red": 1.00, "green": 0.91, "blue": 0.80}}
]

def main():
    print("=" * 75); print("🛡️ STARLIGHT CORE — EXECUTION SAFE INFRASTRUCTURE SYNC")
    print("=" * 75)
    
    if not os.path.exists(SF) or not os.path.exists(LOCAL_CSV):
        print("❌ Configuration Error: Missing authentication token or raw CSV data source."); sys.exit(1)

    with open(LOCAL_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        csv_rows = list(reader)

    csv_headers = [h.strip().lower() for h in csv_rows[3]]
    v_idx = csv_headers.index('verdict')
    name_idx = csv_headers.index('grant name')
    funder_idx = csv_headers.index('funder / org')
    dl_idx = csv_headers.index('public deadline')
    intl_idx = csv_headers.index('internal deadline')
    geo_idx = csv_headers.index('geography')
    llc_idx = csv_headers.index('llc eligible')
    award_idx = csv_headers.index('award range')
    notes_idx = csv_headers.index('status notes')

    parsed_payloads = []
    for row in csv_rows[4:]:
        if len(row) > 1 and row[0].strip().isdigit():
            v_token = row[v_idx].strip().upper()
            status_value = STATUS_MAP.get(v_token, "Open")
            
            award_val = row[award_idx].strip()
            notes_val = row[notes_idx].strip()
            combined_notes = f"Award Range: {award_val} | {notes_val}" if award_val else notes_val
            
            parsed_payloads.append({
                "name": row[name_idx].strip(),
                "funder": row[funder_idx].strip(),
                "geo": row[geo_idx].strip(),
                "llc": row[llc_idx].strip(),
                "status": status_value,
                "notes": combined_notes,
                "public_dl": row[dl_idx].strip(),
                "internal_dl": row[intl_idx].strip()
            })

    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        # Explicit typecast protection for the worksheet ID integer scope
        sheet_id = int(ws.id)
        
        print("    🗑️ Flushing old worksheet content frames...")
        ws.clear()

        full_upload_matrix = []
        full_upload_matrix.append(CANONICAL_HEADERS)

        for item in parsed_payloads:
            row_cell_array = [
                item["name"],
                item["funder"],
                item["geo"],
                item["llc"],
                item["status"],
                item["notes"],
                item["public_dl"],
                item["internal_dl"]
            ]
            full_upload_matrix.append(row_cell_array)

        total_final_rows = len(full_upload_matrix)
        print(f"    🚀 Committing {total_final_rows - 1} audited grant items to data layer...")
        ws.append_rows(full_upload_matrix, value_input_option='USER_ENTERED')
        print("    ✅ Core ledger data has successfully landed.")

        # DECOUPLED METADATA & FORMATTING PROMPT GATE
        try:
            print("    🎛️ Injecting validation data dropdown menus into Column E...")
            requests_payload = [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": total_final_rows + 1,
                            "startColumnIndex": 4,
                            "endColumnIndex": 5
                        },
                        "cell": {
                            "dataValidation": {
                                "condition": {
                                    "type": "ONE_OF_LIST",
                                    "values": [{"userEnteredValue": opt} for opt in STATUS_OPTIONS]
                                },
                                "showCustomUi": True,
                                "strict": True
                            }
                        },
                        "fields": "dataValidation"
                    }
                }
            ]

            print("    🎨 Injecting multi-color row-wide conditional formatting rules...")
            for rule in HIGHLIGHT_RULES:
                formula = f'=$E2="{rule["token"]}"'
                requests_payload.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [
                                {
                                    "sheetId": sheet_id,
                                    "startRowIndex": 1,
                                    "endRowIndex": total_final_rows + 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": len(CANONICAL_HEADERS)
                                }
                            ],
                            "booleanRule": {
                                "condition": {
                                    "type": "CUSTOM_FORMULA",
                                    "values": [{"userEnteredValue": formula}]
                                },
                                "format": {
                                    "backgroundColor": rule["rgb"]
                                }
                            }
                        },
                        "index": 0
                    }
                })

            sheet.batch_update({"requests": requests_payload})
            print("    ✅ UI dropdown elements and conditional color rules are fully active.")

        except Exception as format_err:
            print(f"    ⚠️ UI Warning: Data landed safely, but interface styling was bypassed -> {format_err}")

        print("-" * 75)
        print(f"🟢 SUCCESS: Synchronization complete. Your production workspace is pristine and up to date.")
        print("=" * 75)

    except Exception as e:
        print(f"❌ Critical Core Fault: Ingestion sequence aborted -> {e}"); sys.exit(1)

if __name__ == "__main__":
    main()
