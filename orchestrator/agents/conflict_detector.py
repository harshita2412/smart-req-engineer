def detect_conflicts(parsed):
    """
    Simple rule-based conflict checks
    """
    conflicts = []

    # Example: conflicting actions
    actions = [a["action"] for a in parsed.get("actions", [])]
    if "delete" in actions and "read" in actions:
        conflicts.append("Cannot read and delete the same resource in the same requirement.")

    # Example: deadline check
    for d in parsed.get("deadlines", []):
        if d["unit"] == "days" and d["value"] < 1:
            conflicts.append("Deadline must be >= 1 day.")

    return conflicts
