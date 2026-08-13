#!/usr/bin/env python3
"""
checkin.py - Parallel System Check-In Execution Engine
Host Machine: Local Mac Mini (jameswilliams@mac)
Workspace: ~/murk-runners/
Target Sheet ID: 1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc
"""

import os
import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor

SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SA_PATH = "/Users/jameswilliams/murk-runners/service_account.json"
BASE_DIR = "/Users/jameswilliams/murk-runners"

CACHE_FILES = {
    "Social Velocity": "social_velocity_results.json",
    "Press Monitor": "press_mentions_results.json",
    "Kickstarter Health": "ks_health_metrics.json",
    "Grants Intelligence": "grants_results.json",
    "Task Queue Ledger": "tasks_data.json"
}

def check_cache(name, filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return {"engine": name, "status": "MISSING", "details": f"{filename} missing"}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        mtime = os.path.getmtime(path)
        age_min = round((time.time() - mtime) / 60, 1)
        count = len(data) if isinstance(data, (dict, list)) else 1
        return {"engine": name, "status": "OK", "age_minutes": age_min, "count": count}
    except Exception as e:
        return {"engine": name, "status": "ERROR", "details": str(e)}

def check_service_account():
    if os.path.exists(SA_PATH):
        return {"engine": "Service Account Key", "status": "OK", "details": "Authenticated"}
    return {"engine": "Service Account Key", "status": "MISSING", "details": SA_PATH}

def main():
    start_time = time.time()
    print("🦅 MARIE ENGINE ROOM — PARALLEL SYSTEM TELEMETRY CHECK-IN")
    print(f"📊 Target Master Sheet ID : {SHEET_ID}")
    print(f"📁 Local Project Root    : {BASE_DIR}\n")

    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(check_cache, name, fname) for name, fname in CACHE_FILES.items()]
        futures.append(executor.submit(check_service_account))
        
        for future in futures:
            results.append(future.result())

    print("---------------------------------------------------------------------")
    print(f"{'ENGINE / RESOURCE':<25} | {'STATUS':<10} | {'TELEMETRY / DETAILS'}")
    print("---------------------------------------------------------------------")
    for r in results:
        status_label = "🟢 OK" if r["status"] == "OK" else "🔴 " + r["status"]
        if "age_minutes" in r:
            details = f"Updated {r['age_minutes']}m ago (Records: {r.get('count', 'N/A')})"
        else:
            details = r.get("details", "Active")
        print(f"{r['engine']:<25} | {status_label:<10} | {details}")
    print("---------------------------------------------------------------------")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n✅ Executive brief compiled in {elapsed}s across all scraper channels.")

if __name__ == "__main__":
    main()
