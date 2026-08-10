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
