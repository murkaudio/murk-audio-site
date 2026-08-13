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

import os, json
QUEUE_FILE = os.path.expanduser("~/murk-runners/social_queue.json")
def main():
    print("═" * 60)
    print("🛸 THE MURK AUDIO — SOCIAL CONTENT REVIEW DECK")
    print("═" * 60)
    if not os.path.exists(QUEUE_FILE):
        print("❌ No active queue database found.")
        return
    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)
    pending = [i for i in queue if i["status"] == "pending_review"]
    if not pending:
        print("🟢 Clean desk policy: Zero posts currently awaiting evaluation.")
        return
    print(f"📋 Found {len(pending)} items awaiting review.\n")
    updated = False
    for item in queue:
        if item["status"] != "pending_review": continue
        print(f"🔹 [POST ID: {item['id']}] 🕒 Target: {item['scheduled_time']}")
        print(f"📢 Platform: \033[94m{item['platform'].upper()}\033[0m")
        print(f"📝 Content:\n\033[93m{item['caption']}\033[0m")
        if item.get("media_path"):
            print(f"🖼️ Attached Media: {item['media_path']}")
        print("-" * 40)
        choice = input("Clear this post for automated flight? (y/n): ").strip().lower()
        if choice == 'y':
            item["status"] = "approved"
            print("✅ Status changed to APPROVED.\n")
            updated = True
        else:
            print("🚫 Post held in review sandbox.\n")
    if updated:
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)
        print("💾 Master staging ledger cleanly synced to disk.")
if __name__ == "__main__":
    main()
