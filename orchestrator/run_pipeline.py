import json
import asyncio
from typing import Dict, Any
from orchestrator.agents.ingest_agent import ingest_text
from orchestrator.agents.conflict_detector import detect_conflicts
from orchestrator.agents.api_designer import design_api
from orchestrator.session_store import session_service

def run_pipeline_text(text: str, session_id: str | None = None) -> Dict[str, Any]:
    """
    Synchronous wrapper kept for compatibility.
    Internally uses the async pipeline runner.
    """
    return asyncio.run(run_pipeline_text_async(text, session_id))

async def run_pipeline_text_async(text: str, session_id: str | None = None) -> Dict[str, Any]:
    """
    1) ingest_text (fast, CPU-bound heuristics)
    2) run conflict_detector and api_designer in parallel (demonstrates parallel agents)
    3) store results in session store if session_id provided
    """
    parsed = ingest_text(text)

    # run two agents in parallel (conflict detector & api designer)
    # they both are independent after ingestion, so we can run concurrently
    loop = asyncio.get_event_loop()
    conflict_task = loop.run_in_executor(None, detect_conflicts, parsed)
    api_task = loop.run_in_executor(None, design_api, parsed)

    conflicts, api = await asyncio.gather(conflict_task, api_task)

    result = {
        "parsed": parsed,
        "conflicts": conflicts,
        "api": api
    }

    # persist to session store if requested
    if session_id:
        session_service.merge(session_id, result)

    return result

def run_and_save(text: str, outpath: str, session_id: str | None = None):
    res = run_pipeline_text(text, session_id=session_id)
    with open(outpath, "w", encoding="utf8") as f:
        json.dump(res, f, indent=2)
    return res
