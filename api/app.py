import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, os, importlib.util
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

# import pipeline runner
try:
    from orchestrator.run_pipeline import run_pipeline_text
except Exception:
    spec = importlib.util.spec_from_file_location("run_pipeline", os.path.join(os.getcwd(),"orchestrator","run_pipeline.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run_pipeline_text = module.run_pipeline_text

# import session service
try:
    from orchestrator.session_store import session_service
except Exception:
    session_service = None

# logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("smart-req-engineer")

# prometheus metrics
REQUESTS = Counter("sre_requests_total", "Total pipeline requests", ["endpoint"])
PIPELINE_LATENCY = Gauge("sre_pipeline_latency_ms", "Pipeline latency (ms)")

app = FastAPI(title="Smart Requirements Engineer Agent - API (observability enabled)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RawReq(BaseModel):
    text: str
    project_id: str | None = None
    session_id: str | None = None

@app.get("/")
async def root():
    return {"message":"Smart Requirements Engineer Agent - API running"}

@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.post("/pipeline")
async def pipeline(req: RawReq):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    REQUESTS.labels(endpoint="/pipeline").inc()
    import time
    start = time.time()
    try:
        res = run_pipeline_text(req.text, session_id=req.session_id)
    except Exception as e:
        logger.exception("Pipeline error")
        raise HTTPException(status_code=500, detail=f"pipeline error: {e}")
    elapsed_ms = (time.time() - start) * 1000.0
    PIPELINE_LATENCY.set(elapsed_ms)
    logger.info("Pipeline run: session=%s time_ms=%.2f actions=%s conflicts=%s",
                req.session_id, elapsed_ms, len(res.get("parsed",{}).get("actions",[])), len(res.get("conflicts",[])))
    return res

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_service is None:
        raise HTTPException(status_code=500, detail="Session service not available")
    data = session_service.get(session_id)
    if data is None:
        raise HTTPException(status_code=404, detail="session not found")
    return {"session_id": session_id, "data": data}

@app.get("/scenarios/run")
async def run_scenarios():
    try:
        from tools import run_scenarios as runner
    except Exception:
        spec = importlib.util.spec_from_file_location("run_scenarios", os.path.join(os.getcwd(), "tools", "run_scenarios.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        runner = module
    runner.run_all()
    summary_path = os.path.join("tests", "results", "summary.json")
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=500, detail="Scenario run failed")
    with open(summary_path, "r", encoding="utf8") as f:
        summary = json.load(f)
    return {"summary": summary}
