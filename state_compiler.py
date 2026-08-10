import os, json, time, re, gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

S_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SA = os.path.expanduser("~/murk-runners/service_account.json")
DN = os.path.expanduser("~/murk-runners")
WEB_OUT = "/Users/jameswilliams/Documents/The Murk Audio LLC/The Murk Web Page Files/files/dashboard-data.json"
DASHBOARD_HTML = "/Users/jameswilliams/Documents/The Murk Audio LLC/The Murk Web Page Files/files/dashboard.html"
BASELINE_FILE = os.path.expanduser("~/murk-runners/social_velocity_baselines.json")

def safe_int(val, default=0):
    try: return int(str(val).replace(",", "").replace("$", "").strip())
    except: return default

def main():
    t0 = time.time()
    try:
        c = Credentials.from_service_account_file(SA, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        gc = gspread.authorize(c).open_by_key(S_ID)
        all_rows = gc.worksheet("Task_Queue").get_all_records()
        grant_rows = gc.worksheet("AIR_Grants_Pipeline").get_all_records()
        metric_rows = gc.worksheet("Live_Metrics").get_all_records()
    except Exception as e:
        print(f"❌ Sheets Connection Fault: {e}")
        return

    metrics_map = {}
    for row in metric_rows:
        metric_name = str(row.get("Metric", "")).strip().lower()
        if metric_name and "Value" in row:
            metrics_map[metric_name] = row["Value"]
        
        platform = str(row.get("Value", "")).strip().lower()
        metric_type = str(row.get("Last Update", "")).strip().lower()
        if "instagrar" in platform: platform = "instagram"
            
        if platform in ["x", "bluesky", "instagram", "tiktok", "patreon", "discord", "reddit"]:
            log_key = f"{platform} {metric_type}"
            val = row.get("Source / Notes")
            if val is not None and str(val).strip() != "":
                metrics_map[log_key] = val

    total_tasks = len(all_rows)
    act = [r for r in all_rows if str(r.get("Status")).strip() in ["Open", "Queued", "In Progress"] and r.get("Task")]
    cls = [r for r in all_rows if str(r.get("Status")).strip() in ["Closed", "Done", "Complete"] and r.get("Task")]
    global_comp_pct = round((len(cls) / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    project_map = {}
    for r in all_rows:
        p_name = str(r.get("Project", "")).strip()
        if not p_name or not r.get("Task"): continue
        if p_name not in project_map: project_map[p_name] = {"total": 0, "closed": 0}
        project_map[p_name]["total"] += 1
        if str(r.get("Status")).strip() in ["Closed", "Done", "Complete"]: project_map[p_name]["closed"] += 1

    portfolio_array = []
    for i, (p_name, stats) in enumerate(project_map.items(), 1):
        pct = round((stats["closed"] / stats["total"] * 100)) if stats["total"] > 0 else 0
        portfolio_array.append({
            "id": i, "name": p_name, "status": "[OK] Healthy" if pct >= 50 else "[WARN] Warning",
            "open_tasks": stats["total"] - stats["closed"], "completion_pct": pct
        })

    active_grants = [g for g in grant_rows if str(g.get("Status")).strip().lower() in ["open", "tracked"]]
    regional_count = len(active_grants)
    days_left, target_grant = 99, "None Pending"
    cur_dt_obj = datetime.now()

    for g in active_grants:
        raw_date = g.get("Public Deadline", "")
        if not raw_date: continue
        try:
            pub_date = datetime.strptime(str(raw_date).strip(), '%B %d, %Y')
            internal_gate = pub_date - timedelta(days=10)
            delta_days = (internal_gate - cur_dt_obj).days + 1
            if 0 <= delta_days < days_left:
                days_left = delta_days
                target_grant = g.get("Grant Name", "")
        except: pass

    def read_cache(fn):
        p = os.path.join(DN, fn)
        return json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else {}

    s_cache = read_cache("social_velocity_results.json")
    h_cache = read_cache("ks_health_metrics.json")
    x_met = s_cache.get("metrics", {})

    x_val = safe_int(metrics_map.get("x followers"), 9)
    bluesky_val = safe_int(metrics_map.get("bluesky followers")) or safe_int(x_met.get("bluesky"), 16)
    instagram_val = safe_int(metrics_map.get("instagram followers"), 17)
    tiktok_val = safe_int(metrics_map.get("tiktok followers")) or safe_int(x_met.get("tiktok"), 12)
    patreon_val = safe_int(metrics_map.get("patreon members"), 2)

    today_str = datetime.now().strftime("%Y-%m-%d")
    base_data = {"last_updated": today_str, "baselines": {"x": x_val, "bluesky": bluesky_val, "instagram": instagram_val, "tiktok": tiktok_val, "patreon": patreon_val}}
    
    if os.path.exists(BASELINE_FILE):
        try:
            stored_base = json.load(open(BASELINE_FILE, "r"))
            if stored_base.get("last_updated") == today_str:
                base_data = stored_base
            else:
                base_data["baselines"] = stored_base["baselines"]
                base_data["last_updated"] = today_str
                json.dump(base_data, open(BASELINE_FILE, "w"), indent=2)
        except: pass
    else:
        json.dump(base_data, open(BASELINE_FILE, "w"), indent=2)

    bl = base_data["baselines"]
    
    def calc_velocity_metrics(current, baseline_key):
        b_val = bl.get(baseline_key, current)
        diff = current - b_val
        if diff >= 2: return f"+{diff} today [SPIKE DETECTED]", "[WARN] Momentum Spike"
        elif diff > 0: return f"+{diff} today", "[OK] Growing"
        return "Stable", "[OK] Nominal"

    x_vel, x_stat = calc_velocity_metrics(x_val, "x")
    bsky_vel, bsky_stat = calc_velocity_metrics(bluesky_val, "bluesky")
    inst_vel, inst_stat = calc_velocity_metrics(instagram_val, "instagram")
    tok_vel, tok_stat = calc_velocity_metrics(tiktok_val, "tiktok")
    pat_vel, pat_stat = calc_velocity_metrics(patreon_val, "patreon")

    compiled_payload = {
        "meta": {"generated_at": datetime.now().isoformat(), "engine": "Soldier Boy - state_compiler.py v1.07"},
        "system_status": {"global_status": "[OK] Operational", "engine_latency_seconds": round(time.time() - t0, 2), "last_cron_execution": datetime.now().isoformat()},
        "completion_pct": global_comp_pct,
        "financial_telemetry": {"cash_runway_days": 45, "runway_status": "[OK] Healthy"},
        "task_ledger": {"total_rows_mapped": total_tasks, "active_workflows_count": len(act), "completion_percentage": global_comp_pct},
        "campaign_health": { 
            "lifecycle_status": "LIVE - PRE-LAUNCH" if datetime.now().strftime("%Y-%m-%d") < "2026-07-04" else "LIVE", 
            "currency": "USD", "total_pledged": 0, "backer_count": 0, 
            "launch_date": "2026-07-04 00:00:00", "close_date": "2026-08-15 00:00:00", 
            "prelaunch_signups": safe_int(h_cache.get("telemetry", {}).get("pre_launch_followers"), 1422), "target_signups": 2500 
        },
        "social_velocity": {
            "vault_safety_buffer_days": 7,
            "platforms": {
                "x": { "followers": x_val, "velocity": x_vel, "status": x_stat },
                "bluesky": { "followers": bluesky_val, "velocity": bsky_vel, "status": bsky_stat },
                "instagram": { "followers": instagram_val, "velocity": inst_vel, "status": inst_stat },
                "tiktok": { "followers": tiktok_val, "velocity": tok_vel, "status": tok_stat },
                "patreon": { "followers": patreon_val, "velocity": pat_vel, "status": pat_stat },
                "X": { "followers": x_val, "velocity": x_vel, "status": x_stat },
                "Bluesky": { "followers": bluesky_val, "velocity": bsky_vel, "status": bsky_stat },
                "Instagram": { "followers": instagram_val, "velocity": inst_vel, "status": inst_stat },
                "TikTok": { "followers": tiktok_val, "velocity": tok_vel, "status": tok_stat },
                "Patreon": { "followers": patreon_val, "velocity": pat_vel, "status": pat_stat }
            }
        },
        "grants_pipeline": {"last_synchronization": datetime.now().strftime("%Y-%m-%d"), "regional_sources_active": regional_count, "next_internal_deadline_days": days_left if days_left != 99 else 0, "next_grant_target": target_grant},
        "competitor_intelligence": {"total_tracked_campaigns": 3},
        "project_portfolio": portfolio_array
    }

    try:
        os.makedirs(os.path.dirname(WEB_OUT), exist_ok=True)
        json.dump(compiled_payload, open(WEB_OUT, "w", encoding="utf-8"), indent=2)
        print(f"✅ Dynamic Dataset written to: {WEB_OUT}")
    except Exception as e:
        print(f"❌ Write failed: {e}")
        return

    if os.path.exists(DASHBOARD_HTML):
        try:
            html_content = open(DASHBOARD_HTML, "r", encoding="utf-8").read()
            new_platforms_block = f"""const AUD_PLATFORMS = [
  {{ key: 'X', color: '#3b8ce8', followers: {x_val} }},
  {{ key: 'Bluesky', color: '#1aa87c', followers: {bluesky_val} }},
  {{ key: 'Instagram', color: '#e05ca0', followers: {instagram_val} }},
  {{ key: 'TikTok', color: '#d95f30', followers: {tiktok_val} }},
  {{ key: 'Discord', color: '#7c5de8', followers: 4 }},
  {{ key: 'Email list', color: '#e8a020', followers: 20 }},
  {{ key: 'Patreon', color: '#22c55e', followers: {patreon_val} }},
];"""
            html_content = re.sub(r"const AUD_PLATFORMS = \[\s*([\s\S]*?)\s*\];", new_platforms_block, html_content)
            total_aud = x_val + bluesky_val + instagram_val + tiktok_val + 4 + 20 + patreon_val
            html_content = re.sub(r'<div class="aud-total-num" id="aud-total">\d+</div>', f'<div class="aud-total-num" id="aud-total">{total_aud}</div>', html_content)
            open(DASHBOARD_HTML, "w", encoding="utf-8").write(html_content)
            print("✅ HTML frontend compilation overwrite clear.")
        except Exception as e:
            print(f"❌ HTML tracking injection patch failed: {e}")

if __name__ == "__main__":
    main()
