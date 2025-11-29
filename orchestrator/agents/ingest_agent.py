import re

def ingest_text(text: str):
    """
    Very simple deterministic requirement parser:
    - Extract actions: create/read/update/delete
    - Extract time constraints (e.g., 'within 30 days')
    - Extract entities (noun phrases)
    """
    text_l = text.lower()

    actions = []
    for act in ["create", "read", "delete", "update", "archive"]:
        if act in text_l:
            actions.append({"action": act})

    deadlines = []
    m = re.search(r"(\d+)\s+(day|days|hour|hours|week|weeks)", text_l)
    if m:
        deadlines.append({"value": int(m.group(1)), "unit": m.group(2)})

    # naive noun extraction
    nouns = []
    tokens = re.findall(r"[a-zA-Z]+", text_l)
    for w in tokens:
        if w.endswith("s") and w != "days":
            nouns.append(w)

    return {
        "actions": actions,
        "deadlines": deadlines,
        "entities": list(set(nouns))
    }
