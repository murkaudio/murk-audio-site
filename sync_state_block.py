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

import os
import requests
import google.auth.transport.requests
from google.oauth2.service_account import Credentials

# Strict System Architecture Paths
SERVICE_ACCOUNT_PATH = "/Users/jameswilliams/murk-runners/service_account.json"
LOCAL_STATE_PATH = "/Users/jameswilliams/murk-runners/MURK_STATE_SUMMARY.md"
DRIVE_FILE_ID = "1LQD-_S8I09Y2gd8u2gxldyq8fPfnEaVpjcq0OdKemL4"

def main():
    if not os.path.exists(LOCAL_STATE_PATH):
        print(f"[CRITICAL ERROR] Local state block file missing at: {LOCAL_STATE_PATH}")
        return

    try:
        print("[ENGINE] Reading local markdown state payload...")
        with open(LOCAL_STATE_PATH, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        print("[ENGINE] Initializing secure Google Drive API authorization handshake...")
        scopes = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=scopes)
        
        # Correct Transport Class: Instantiate the required library wrapper
        auth_request = google.auth.transport.requests.Request()
        creds.refresh(auth_request)
        
        # Target the media upload gateway for a direct file body overwrite
        url = f"https://www.googleapis.com/upload/drive/v3/files/{DRIVE_FILE_ID}?uploadType=media"
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "text/markdown"
        }
        
        print(f"[ENGINE] Injecting sync stream to remote Drive ID: {DRIVE_FILE_ID}")
        response = requests.patch(url, headers=headers, data=markdown_content.encode('utf-8'))
        
        if response.status_code == 200:
            print("==> 🟢 SUCCESS: Remote MURK_STATE_SUMMARY.md updated autonomously on Google Drive!")
        else:
            print(f"[ERROR] Google Drive API refused stream with Status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[CRITICAL ERROR] State block sync pipeline collapsed: {str(e)}")

if __name__ == "__main__":
    main()
