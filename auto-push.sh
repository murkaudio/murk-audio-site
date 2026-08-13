#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

REPO_DIR = "/Users/jameswilliams/murk-runners"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S PT")

print(f"[GIT_ENGINE] Initializing secure upstream push for {TIMESTAMP}...")

try:
    os.chdir(REPO_DIR)
    
    json_files = [f for f in os.listdir(REPO_DIR) if f.endswith('.json') and 'service_account' not in str(f)]
    if json_files:
        subprocess.run(["git", "add", "--ignore-errors"] + json_files, check=True)
    
    diff_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
    
    if diff_check.returncode == 1:
        commit_msg = f"Automated Telemetry Update — {TIMESTAMP} [Engine Room Run]"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print("[GIT_ENGINE] New mutations committed locally.")
    else:
        print("[GIT_ENGINE] No new layout mutations detected to commit.")

    print("[GIT_ENGINE] Synchronizing upstream remote telemetry branch...")
    subprocess.run(["git", "push", "origin", "main:telemetry", "--force"], check=True)
    print("[GIT_ENGINE] Success. Upstream repository synchronized cleanly.")
    print("[GITHUB_PUSH_SUCCESS]")

except Exception as e:
    print(f"[ERROR] Critical Git transport failure: {e}")
    sys.exit(1)
