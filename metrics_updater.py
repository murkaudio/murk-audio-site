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
import os, sys, json, gspread
from datetime import datetime

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1-Faz0FUlPcI4GoRT5poeoap-HMVwgseufhfKZCBXeE4"
JSON_OUTPUT = "/Users/jameswilliams/murk-runners/metrics_data.json"

def parse_amount(val):
    if not val: return 0.0
    try:
        clean = "".join(c for c in str(val) if c.isdigit() or c == ".")
        return float(clean) if clean else 0.0
    except Exception:
        return 0.0

def main():
    if not os.path.exists(SF):
        print("❌ Authentication key file missing.")
        sys.exit(1)

    try:
        gc = gspread.service_account(filename=SF)
        sheet = gc.open_by_key(MID)
        
        ws_source = sheet.worksheet("Project Portfolio")
        ws_dest = sheet.worksheet("Live Metrics")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)

    try:
        all_records = ws_source.get_all_records()
        
        # Deduplicate rows by Grant Name from bottom up (freshest rows rule)
        unique_grants = {}
        for r in all_records:
            name = str(r.get("Grant Name", "")).strip()
            if name:
                unique_grants[name] = r

        pipeline_total = len(unique_grants)
        submitted_count = 0
        keep_count = 0
        park_count = 0
        kill_count = 0
        total_value = 0.0
        submitted_value = 0.0

        for name, r in unique_grants.items():
            # Support both column names safely
            verdict = str(r.get("Verdict", r.get("Status", ""))).strip().upper()
            amount = parse_amount(r.get("Amount", 0))
            
            total_value += amount
            if "SUBMITTED" in verdict:
                submitted_count += 1
                submitted_value += amount
            elif "KEEP" in verdict:
                keep_count += 1
            elif "PARK" in verdict:
                park_count += 1
            elif "KILL" in verdict:
                kill_count += 1

        # Generate both timestamp variations for old vs new frontend hooks
        legacy_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        verbose_ts = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        # Provide dual-type keys (raw numbers AND formatted strings) so JavaScript never breaks
        dashboard_data = {
            "pipeline_total": int(pipeline_total),
            "submitted_count": int(submitted_count),
            "approved_count": int(keep_count), 
            "keep_count": int(keep_count),
            "park_count": int(park_count),
            "kill_count": int(kill_count),
            
            # Numeric Floats for JavaScript math/charts
            "total_value": float(total_value),
            "submitted_value": float(submitted_value),
            
            # String Formats for direct UI rendering
            "total_value_str": f"${total_value:,.2f}",
            "submitted_value_str": f"${submitted_value:,.2f}",
            
            # Timestamps
            "last_updated": legacy_ts,
            "last_updated_verbose": verbose_ts
        }

        with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=4)

        # Mirror these clean numbers onto your Google Sheet summary tab view
        dashboard_rows = [
            ["MARIE ENGINE SUMMARY DASHBOARD", "", ""],
            [f"Last Core Sync Execution: {verbose_ts}", "", ""],
            ["----------------------------------------", "-----------------", ""],
            ["METRIC PARAMETER", "VALUE / METRIC", "NOTES"],
            ["----------------------------------------", "-----------------", ""],
            ["Total Tracked Opportunities", pipeline_total, "Unique active pipeline targets"],
            ["Verdict Status: SUBMITTED", submitted_count, "Applications under active review"],
            ["Verdict Status: KEEP (Active Hunt)", keep_count, "High priority targets moving to draft"],
            ["Verdict Status: PARK (On Hold)", park_count, "Viable tracks deferred for timing"],
            ["Verdict Status: KILL (Dropped)", kill_count, "Archived/Ineligible leads filtered out"],
            ["----------------------------------------", "-----------------", ""],
            ["Total Pipeline Gross Value", f"${total_value:,.2f}", "Cumulative potential capital value"],
            ["Total Capital Currently Submitted", f"${submitted_value:,.2f}", "Active requests out in the wild"]
        ]
        
        ws_dest.clear()
        ws_dest.update(range_name="A1", values=dashboard_rows)
        print("🟢 SUCCESS: High-compatibility metrics pushed to JSON and Google Sheet.")

    except Exception as err:
        print(f"❌ Processing Error: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
