#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


def check(name, tests, exercised=True):
    if not exercised:
        return {"status": "not_exercised", "checks": []}
    rows = [{"pass": ok, "message": message, "severity": severity} for ok, message, severity in tests]
    failed = [row for row in rows if not row["pass"]]
    status = "blocker" if any(row["severity"] == "blocker" for row in failed) else "warning" if failed else "pass"
    return {"status": status, "checks": rows}


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
    brief_exists = bool(card and target and card.get("id") and (target / "docs" / "briefs" / f"{card['id']}.md").exists())

    verify_match = re.search(r"(?:Canonical (?:verification )?command|Verification)[^\n]*:\s*`?([^`\n]+)", local, re.I)
    verification_documented = bool(verify_match)

    subsystems = {
        "instructions": check("instructions", [
            (has(gintary, "load and follow `ginflow`") and has(ginb, "load and follow `ginflow`"), "Profiles route target-project work through ginflow", "warning"),
            (all(has(ginflow, heading) for heading in ("## Project session startup", "## Execution contract", "## Definition of done", "## Completion report")), "Canonical ginflow instruction sections exist", "warning"),
            (not target or bool(local_path), "Target local instruction file exists when target supplied", "warning"),
            (not target or has(local, "come from `ginflow`"), "Target local instructions route shared workflow to ginflow when target supplied", "warning"),
        ]),
        "state": check("state", [
            (bool(card) and all(field in card for field in card_fields), "Selected card has required fields", "blocker"),
            (brief_exists, "Card-ID brief exists", "blocker"),
            (not target or not (target / "session-handoff.md").exists(), "Mandatory root session handoff is absent", "warning"),
        ], exercised=bool(target)),
        "verification": check("verification", [
            (verification_documented, "Canonical project verification is documented", "blocker"),
            (has(ginflow, "Quote canonical") and has(ginflow, "exact fresh result"), "Fresh evidence format is required", "warning"),
        ], exercised=bool(target)),
        "scope": check("scope", [
            (has(ginflow, "One active card per worker"), "One-active-card rule exists", "warning"),
            (bool(card and all(field in card for field in ("scope", "acceptance", "workspace"))), "Card tracks scope, acceptance, and workspace", "blocker"),
            (any(has(local, word) for word in ("forbidden", "boundaries", "sensitive paths")), "Target local boundaries exist", "warning"),
        ], exercised=bool(target)),
        "lifecycle": check("lifecycle", [
            (has(ginflow, "## Project session startup"), "Startup contract exists", "warning"),
            (has(ginflow, "## Session close and restart"), "Close/restart contract exists", "warning"),
            (has(ginflow, "Kanban card is default durable handoff"), "Kanban-first handoff exists", "warning"),
            (has(ginflow, "## Optional session handoff export"), "Optional export exists", "warning"),
            (not target or verification_documented, "Clean restart verification path is documented when target supplied", "blocker"),
        ]),
    }
    result = {"setup_repo": str(root), "target": str(target) if target else None, "subsystems": subsystems}
    statuses = {item["status"] for item in subsystems.values()}
    result["status"] = "blocker" if "blocker" in statuses else "warning" if "warning" in statuses else "pass"
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, item in subsystems.items():
            print(f"{name}: {item['status']}")
            for row in item["checks"]:
                print(f"  {'PASS' if row['pass'] else 'FAIL'} {row['message']}")
    return 2 if result["status"] == "blocker" else 0


if __name__ == "__main__":
    sys.exit(main())
