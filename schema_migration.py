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
"""
schema_migration.py
The Murk Audio LLC — Grants Pipeline Schema Normalization
Session: June 11, 2026
"""
import os
import sys
import re
import gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

def parse_status_components(raw_value):
    """Normalizes raw status strings into crisp tracking tokens and descriptive notes."""
    val = raw_value.strip()
    if not val:
        return "", ""
        
    val_lower = val.lower()
    
    # Target specific edge case strings captured in the user's layout screenshot
    if val_lower == "deadline past":
        return "Killed", "Deadline past"
        
    # Standard delimiter extraction engine (handles both em-dashes and standard hyphens)
    match = re.split(r'\s*[\​—\-]\s*', val, maxsplit=1)
    if len(match) == 2:
        token = match[0].strip()
        note = match[1].strip()
        # Capitalize the base categorical state token cleanly
        return token.capitalize(), note
        
    # Catch standalone entries without notes (e.g., "Conditional")
    if "verify" in val_lower:
        return "Verify", val.replace("Verify", "").replace("verify", "").strip(" —-")
        
    return val.capitalize(), ""

def main():
    print("=" * 75)
    print("🛡️ SCHEMA MIGRATION SYSTEM — EXECUTING LEDGER STRUCTURAL REFACTOR")
    print("=" * 75)
    
    if not os.path.exists(SF):
        print("❌ System Error: Service Account credentials missing."); sys.exit(1)
        
    try:
        # Connect natively via automated gspread configuration wrapper
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        # Pull down the complete data matrix from cloud storage
        raw_matrix = ws.get_all_values()
        if not raw_matrix:
            print("❌ Migration Fault: Target worksheet is empty."); sys.exit(1)
            
        headers = [h.strip().lower() for h in raw_matrix[0]]
        print(f"    📊 Live Header Pre-Check: Located columns -> {headers}")
        
        if "status" not in headers:
            print("❌ Structure Error: Base column layout is missing an explicit 'Status' cell."); sys.exit(1)
            
        status_col_idx = headers.index("status")
        
        # Build out the target matrix space
        migrated_matrix = []
        
        # 1. Generate upgraded header template array
        header_row = list(raw_matrix[0])
        header_row.insert(status_col_idx + 1, "Status Notes")
        migrated_matrix.append(header_row)
        
        # 2. Iterate through rows and separate data attributes
        print("    ⚡ Processing matrix rows... Separating state categories from historic notes.")
        for row in raw_matrix[1:]:
            if not row:
                continue
                
            # Pad row array if structural rows are truncated
            while len(row) <= status_col_idx:
                row.append("")
                
            original_status_text = row[status_col_idx]
            clean_status, clean_note = parse_status_components(original_status_text)
            
            # Reconstruct the row array dynamically
            new_row = list(row)
            new_row[status_col_idx] = clean_status
            new_row.insert(status_col_idx + 1, clean_note)
            migrated_matrix.append(new_row)
            
        # 3. Clear worksheet layout to accommodate shifted column dimensions
        print("    🗑️ Flushing legacy layout structures to allow coordinate expansion...")
        ws.clear()
        
        # 4. Commit normalized data array in a single network transaction block
        print("    🚀 Committing updated structural dataset back to Google Workspace...")
        ws.update('A1', migrated_matrix, value_input_option='USER_ENTERED')
        
        print("-" * 75)
        print("🟢 SCHEMA REFACTOR COMPLETE: Status data split into tracking tokens and clean notes.")
        print("=" * 75)
        
    except Exception as e:
        print(f"❌ Structural Refactor Aborted: {e}"); sys.exit(1)

if __name__ == "__main__":
    main()
