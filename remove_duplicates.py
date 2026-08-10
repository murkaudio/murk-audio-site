#!/usr/bin/env python3
"""
remove_duplicates.py
The Murk Audio LLC — Automated Pipeline Deduplication Engine
Session: June 11, 2026
"""
import os
import sys
import gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

def main():
    print("=" * 75)
    print("🛡️ STARLIGHT PURGE SYSTEM — EXECUTING PIPELINE DE-DUPLICATION")
    print("=" * 75)
    
    if not os.path.exists(SF):
        print("❌ System Error: Service account credentials missing."); sys.exit(1)
        
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        
        try:
            ws = sheet.worksheet("AIR_Grants_Pipeline")
        except gspread.exceptions.WorksheetNotFound:
            ws = sheet.worksheet("AIR_Grants")
            
        all_rows = ws.get_all_values()
        if not all_rows:
            print("❌ Processing Error: Worksheet is completely empty."); sys.exit(1)

        header_idx = 3
        grant_col_idx = 1
        
        for i, row in enumerate(all_rows):
            row_lower = [str(cell).strip().lower() for cell in row]
            if "grant name" in row_lower:
                header_idx = i
                grant_col_idx = row_lower.index("grant name")
                break
                
        print(f"    📊 Layout Map Confirmed: Header Row Found at Index {header_idx}")
        print(f"    🔍 Matching Parameter Set: Deduplicating via Column index {grant_col_idx} ('Grant Name')")

        prefix_rows = all_rows[:header_idx + 1]
        data_rows = all_rows[header_idx + 1:]

        seen_names = set()
        unique_data_rows = []
        duplicate_count = 0

        for row in data_rows:
            if not row or len(row) <= grant_col_idx:
                continue
                
            g_name = row[grant_col_idx].strip()
            g_name_lower = g_name.lower()
            
            if not g_name_lower:
                if any(cell.strip() for cell in row):
                    unique_data_rows.append(row)
                continue
                
            if g_name_lower in seen_names:
                duplicate_count += 1
                continue
                
            seen_names.add(g_name_lower)
            unique_data_rows.append(row)

        print(f"    ⚡ Scan Analysis: Identified {duplicate_count} duplicate row objects.")

        header_row_lower = [str(c).strip().lower() for c in all_rows[header_idx]]
        if "#" in header_row_lower:
            id_idx = header_row_lower.index("#")
            serial_counter = 1
            for row in unique_data_rows:
                if len(row) > id_idx and (row[id_idx].strip().isdigit() or row[id_idx].strip() == ""):
                    row[id_idx] = str(serial_counter)
                    serial_counter += 1

        print("    🗑️ Flushing workspace cells to execute clean data overwrite...")
        ws.clear()

        final_matrix = prefix_rows + unique_data_rows
        print(f"    🚀 Uploading {len(final_matrix)} pristine deduplicated rows...")
        ws.append_rows(final_matrix, value_input_option='USER_ENTERED')
        
        print("-" * 75)
        print(f"🟢 PURGE SECURE: Successfully removed {duplicate_count} duplicate rows from the master pipeline.")
        print("=" * 75)
        
    except Exception as e:
        print(f"❌ Execution Fault: {e}"); sys.exit(1)

if __name__ == "__main__":
    main()
