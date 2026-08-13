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
import json

CONTACTS_PATH = os.path.expanduser("~/murk-runners/priority_contacts.json")

def get_live_monitoring_targets():
    if not os.path.exists(CONTACTS_PATH):
        print("[ERROR] Priority contact registry file not found.")
        return []
        
    with open(CONTACTS_PATH, "r") as f:
        registry = json.load(f)
        
    # Isolate only individuals with an explicit "active" status flag
    active_targets = [
        c for c in registry.get("contacts", [])
        if c.get("status") == "active"
    ]
    
    return active_targets

if __name__ == "__main__":
    active = get_live_monitoring_targets()
    print(f"\n[CONTACTS API] Extracted {len(active)} active monitoring nodes from registry:")
    print("-" * 60)
    for c in active:
        print(f"👤 {c['name']} ({c['email']}) — Role: {c['role']}")
    print("-" * 60 + "\n")
