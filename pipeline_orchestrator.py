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

import datetime
from typing import Dict, List, Optional

def log_pipeline_event(opportunity: Dict[str, str], action: str, token_cost: float, reason: str):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "target": opportunity.get("title", "untitled"),
        "source_url": opportunity.get("source_url", ""),
        "action_executed": action,
        "token_cost": token_cost,
        "reason": reason,
    }
    print(f"[LOG] {entry}")
    return entry

def five_axis_gemini_gate(opportunity: Dict[str, str]) -> Dict[str, str]:
    raise NotImplementedError(
        "five_axis_gemini_gate is a structural placeholder. "
        "Wire in the real Gemini API call here before production use."
    )

def process_scraped_opportunity(opportunity: Dict[str, str], gate_fn=five_axis_gemini_gate) -> Optional[Dict[str, str]]:
    status = opportunity.get("cycle_status", "UNKNOWN")

    if status in ("LIKELY_CLOSED", "FETCH_FAILED", "PARSE_FAILED"):
        log_pipeline_event(opportunity, "DROPPED_PRE_GATE", 0.0,
                            f"cycle_status={status}, short-circuited before any AI call")
        return None

    try:
        gate_result = gate_fn(opportunity)
    except NotImplementedError:
        log_pipeline_event(opportunity, "GATE_NOT_IMPLEMENTED", 0.0,
                            "five_axis_gemini_gate is still a placeholder")
        raise

    if gate_result.get("verdict") != "KEEP":
        log_pipeline_event(opportunity, "DROPPED_POST_GATE", 0.0001,
                            f"Gemini gate verdict=KILL, axis_failed={gate_result.get('axis_failed')}")
        return None

    log_pipeline_event(opportunity, "PASSED_TO_MARIE_GATE", 0.0001,
                        "Cleared both stages, awaiting human pre-screen before sheet write")
    opportunity["gate_verdict"] = gate_result
    return opportunity

def run_full_pipeline(scraped_opportunities: List[Dict[str, str]], gate_fn=five_axis_gemini_gate) -> List[Dict[str, str]]:
    survivors = [r for o in scraped_opportunities if (r := process_scraped_opportunity(o, gate_fn=gate_fn)) is not None]
    print(f"\n[+] Pipeline complete: {len(survivors)}/{len(scraped_opportunities)} survived to human pre-screen.")
    return survivors

print("[+] Orchestration wrapper locked and loaded.")
