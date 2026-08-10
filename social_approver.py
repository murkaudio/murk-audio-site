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
