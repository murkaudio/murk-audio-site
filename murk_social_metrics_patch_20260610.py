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

import os, sys, gspread
from google.oauth2.service_account import Credentials
CP = os.path.expanduser("~/murk-runners/service_account.json")
ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
creds = Credentials.from_service_account_file(CP, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
sheet = gspread.authorize(creds).open_by_key(ID)
lm = sheet.worksheet("Live_Metrics")
m_data = {
    "X Followers": ["9", "June 10, 2026", "X profile screenshot — James — June 10, 2026. 9 followers. No change from June 5. 47 posts. FLAG: X bio needs noir-only calibration."],
    "X Posts": ["47", "June 10, 2026", "X profile screenshot — James — June 10, 2026. 47 posts. Up from 44 on June 5."],
    "Bluesky Followers": ["17", "June 10, 2026", "Bluesky profile screenshot — James — June 10, 2026. 17 followers. Up from 15. 53 posts."],
    "Bluesky Posts": ["53", "June 10, 2026", "Bluesky profile screenshot — James — June 10, 2026. 53 posts. Up from 50 on June 5."],
    "Instagram Followers": ["17", "June 10, 2026", "Instagram profile screenshot — James — June 10, 2026. 17 followers. No change from June 5. 30 posts."],
    "Instagram Posts": ["30", "June 10, 2026", "Instagram profile screenshot — James — June 10, 2026. 30 posts. Up from 27 on June 5."]
}
for k, v in m_data.items():
    row = next((i+1 for i, r in enumerate(lm.col_values(1)) if r.strip() == k), None)
    if row:
        lm.update_cell(row, 2, v[0]); lm.update_cell(row, 3, v[1]); lm.update_cell(row, 4, v[2])
sv = sheet.worksheet("Social_Vault")
if "2026-06-10-POST" not in [val.strip() for val in sv.col_values(1)]:
    sv.append_row(["2026-06-10-POST", "Daily post — X + Bluesky — June 10, 2026", "Social Media — Summer Strategy", "James", "June 10, 2026", "Posted — Live", "Post live on X and Bluesky. copy: A distant hum. Not mechanical. Not natural. Something... else. You feel it too, don't you? #DeadSignal. Noir register confirmed. Passes Julie gate.", "June 10, 2026", "T0"], value_input_option="USER_ENTERED")
print("✅ SOCIAL METRICS INEQTED SUCCESSFULLY!")
