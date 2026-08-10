import os, json, requests
from datetime import datetime
QUEUE_FILE = os.path.expanduser("~/murk-runners/social_queue.json")
BSKY_HANDLE = "murkaudio.bsky.social"
BSKY_PASSWORD = "your-app-password"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/your-webhook-id"
def copy_to_clipboard(text):
    os.system(f"echo {json.dumps(text)} | pbcopy")
def trigger_macos_notification(title, msg):
    os.system(f"osascript -e 'display notification \"{msg}\" with title \"{title}\" sound name \"Glass\"'")
def post_to_bluesky(text):
    try:
        sess = requests.post("https://bsky.social/xrpc/com.atproto.server.createSession", json={"identifier": BSKY_HANDLE, "password": BSKY_PASSWORD}).json()
        headers = {"Authorization": f"Bearer {sess['accessJwt']}"}
        payload = {"repo": sess["did"], "collection": "app.bsky.feed.post", "record": {"text": text, "createdAt": datetime.utcnow().isoformat() + "Z"}}
        return requests.post("https://bsky.social/xrpc/com.atproto.repo.createRecord", json=payload, headers=headers).status_code == 200
    except: return False
def post_to_discord(text):
    try: return requests.post(DISCORD_WEBHOOK, json={"content": text}).status_code in [200, 204]
    except: return False
def main():
    if not os.path.exists(QUEUE_FILE): return
    with open(QUEUE_FILE, "r") as f: queue = json.load(f)
    now = datetime.now()
    updated = False
    for item in queue:
        sched_time = datetime.fromisoformat(item["scheduled_time"])
        if now < sched_time: continue
        if item["status"] == "pending_review":
            trigger_macos_notification("⚠️ HOLD: Review Required", f"Post {item['id']} for {item['platform'].upper()} is overdue but lacks Julie's approval.")
            continue
        if item["status"] != "approved": continue
        platform = item["platform"].lower()
        caption = item["caption"]
        if platform == "bluesky":
            if post_to_bluesky(caption): item["status"] = "published"; updated = True
        elif platform == "discord":
            if post_to_discord(caption): item["status"] = "published"; updated = True
        else:
            copy_to_clipboard(caption)
            media_note = f" 🖼️ Media: {item['media_path']}" if item.get("media_path") else ""
            trigger_macos_notification(f"THE MURK: Post to {platform.upper()}", f"Cleared by Julie! Caption on clipboard.{media_note}")
            item["status"] = "published_manual"
            updated = True
    if updated:
        with open(QUEUE_FILE, "w") as f: json.dump(queue, f, indent=2)
if __name__ == "__main__":
    main()
