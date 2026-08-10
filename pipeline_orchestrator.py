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
