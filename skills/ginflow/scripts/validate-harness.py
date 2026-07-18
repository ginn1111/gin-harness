#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


def check(name, tests, exercised=True):
    if not exercised:
        return {"status": "not_exercised", "checks": []}
    rows = [{"pass": ok, "message": message} for ok, message in tests]
    return {"status": "pass" if all(row["pass"] for row in rows) else "fail", "checks": rows}


def has(text, value):
    return value.lower() in text.lower()


def main():
    parser = argparse.ArgumentParser(description="Validate the ginflow five-subsystem harness")
    parser.add_argument("--setup-repo", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--card", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = (args.setup_repo or Path(__file__).resolve().parents[3]).resolve()
    ginflow = (root / "skills/ginflow/SKILL.md").read_text()
    gintary = (root / "profiles/gintary.SOUL.md").read_text()
    ginb = (root / "profiles/ginb.SOUL.md").read_text()
    target = args.target.resolve() if args.target else None
    local = ""
    local_path = None
    if target:
        for name in (".hermes.md", "AGENTS.md"):
            candidate = target / name
            if candidate.exists():
                local_path, local = candidate, candidate.read_text()
                break

    card = json.loads(args.card.read_text()) if args.card else {}
    card_fields = ("id", "title", "objective", "scope", "acceptance", "workspace", "status", "assignee", "links")
    brief_exists = bool(card and target and (target / "briefs" / f"{card['id']}.md").exists())

    verify_match = re.search(r"(?:Verify|Verification)[^\n]*[:` ]+`?([^`\n]+)`?", local, re.I)
    verify_script = target / "verify.sh" if target else None
    verification_documented = bool(verify_match or (local and "./verify.sh" in local))
    fail_fast = bool(verify_script and verify_script.exists() and re.search(r"set\s+-[^\n]*(?:e|errexit)", verify_script.read_text()))

    subsystems = {
        "instructions": check("instructions", [
            (has(gintary, "load and follow `ginflow`") and has(ginb, "load and follow `ginflow`"), "Profiles route target-project work through ginflow"),
            (all(has(ginflow, heading) for heading in ("## Project session startup", "## Execution contract", "## Definition of done", "## Completion report")), "Canonical ginflow instruction sections exist"),
            (not target or bool(local_path), "Target local instruction file exists when target supplied"),
            (not target or has(local, "come from `ginflow`"), "Target local instructions route shared workflow to ginflow when target supplied"),
        ]),
        "state": check("state", [
            (all(field in card for field in card_fields), "Selected card has required fields"),
            (brief_exists, "Card-ID brief exists"),
            (not target or not (target / "session-handoff.md").exists(), "Mandatory root session handoff is absent"),
        ], exercised=bool(card and target)),
        "verification": check("verification", [
            (verification_documented, "Canonical project verification is documented"),
            (bool(verify_script and verify_script.exists()), "Canonical verify.sh exists for fixture target"),
            (fail_fast, "Verification script fails fast"),
            (has(ginflow, "Quote canonical command and exact fresh result"), "Fresh evidence format is required"),
        ], exercised=bool(target)),
        "scope": check("scope", [
            (has(ginflow, "One active card per worker"), "One-active-card rule exists"),
            (bool(card and all(field in card for field in ("scope", "acceptance", "workspace"))), "Card tracks scope, acceptance, and workspace"),
            (any(has(local, word) for word in ("forbidden", "boundaries", "sensitive paths")), "Target local boundaries exist"),
        ], exercised=bool(card and target)),
        "lifecycle": check("lifecycle", [
            (has(ginflow, "## Project session startup"), "Startup contract exists"),
            (has(ginflow, "## Session close and restart"), "Close/restart contract exists"),
            (has(ginflow, "Kanban card is default durable handoff"), "Kanban-first handoff exists"),
            (has(ginflow, "## Optional session handoff export"), "Optional export exists"),
            (not target or verification_documented, "Clean restart verification path is documented when target supplied"),
        ]),
    }
    result = {"setup_repo": str(root), "target": str(target) if target else None, "subsystems": subsystems}
    result["status"] = "fail" if any(item["status"] == "fail" for item in subsystems.values()) else "pass"
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, item in subsystems.items():
            print(f"{name}: {item['status']}")
            for row in item["checks"]:
                print(f"  {'PASS' if row['pass'] else 'FAIL'} {row['message']}")
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
