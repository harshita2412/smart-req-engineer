from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import importlib.util

# deterministic pipeline runner
try:
    # normal import if orchestrator package exists
    from orchestrator.run_pipeline import run_pipeline_text
except Exception:
    # fallback if running from source without package init
    spec = importlib.util.spec_from_file_location("run_pipeline", os.path.join(os.getcwd(),"orchestrator","run_pipeline.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run_pipeline_text = module.run_pipeline_text

app = FastAPI(title="Smart Requirements Engineer Agent - API")

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

@app.get("/")
async def root():
    return {"message":"Smart Requirements Engineer Agent - API running"}

@app.post("/pipeline")
async def pipeline(req: RawReq):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        res = run_pipeline_text(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"pipeline error: {e}")
    return res

@app.get("/scenarios/run")
async def run_scenarios():
    # run the scenario runner (tools/run_scenarios.py)
    try:
        # prefer importing module if present
        from tools import run_scenarios as runner
        runner.run_all()
    except Exception:
        spec = importlib.util.spec_from_file_location("run_scenarios", os.path.join(os.getcwd(),"tools","run_scenarios.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.run_all()

    summary_path = os.path.join("tests","results","summary.json")
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=500, detail="Scenario run failed")
    with open(summary_path, "r", encoding="utf8") as f:
        summary = json.load(f)
    return {"summary": summary}
