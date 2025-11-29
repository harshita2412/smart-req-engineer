import json
from orchestrator.agents.ingest_agent import ingest_text
from orchestrator.agents.conflict_detector import detect_conflicts
from orchestrator.agents.api_designer import design_api

def run_pipeline_text(text: str):
    parsed = ingest_text(text)
    conflicts = detect_conflicts(parsed)
    api = design_api(parsed)
    result = {
        "parsed": parsed,
        "conflicts": conflicts,
        "api": api
    }
    return result

def run_and_save(text: str, outpath: str):
    res = run_pipeline_text(text)
    with open(outpath, "w", encoding="utf8") as f:
        json.dump(res, f, indent=2)
    return res
