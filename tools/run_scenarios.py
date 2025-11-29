import os, json
from orchestrator.run_pipeline import run_pipeline_text

SCENARIO_DIR = os.path.join("tests", "scenarios")
RESULT_DIR = os.path.join("tests", "results")

def run_all():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    summary = {}

    for filename in os.listdir(SCENARIO_DIR):
        if not filename.endswith(".txt"):
            continue
        
        path = os.path.join(SCENARIO_DIR, filename)
        with open(path, "r", encoding="utf8") as f:
            text = f.read()

        output = run_pipeline_text(text)
        out_path = os.path.join(RESULT_DIR, filename.replace(".txt", ".json"))

        with open(out_path, "w", encoding="utf8") as fout:
            json.dump(output, fout, indent=2)

        summary[filename] = {
            "parsed": len(output.get("parsed", {})),
            "conflicts": len(output.get("conflicts", [])),
            "api_paths": len(output.get("api", {}).get("paths", {}))
        }

    summary_path = os.path.join(RESULT_DIR, "summary.json")
    with open(summary_path, "w", encoding="utf8") as fsum:
        json.dump(summary, fsum, indent=2)

    print("Scenarios executed. Summary written to tests/results/summary.json")
