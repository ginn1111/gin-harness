#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from harness_core import artifact_gate, check, has, linked_artifacts, load_kanban_card, normalize_card


def main():
    parser = argparse.ArgumentParser(description="Validate the ginflow five-subsystem harness")
    parser.add_argument("--setup-repo", type=Path)
    parser.add_argument("--target", type=Path)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--card", type=Path, help="Card JSON file; accepts normalized Ginflow or `hermes kanban show --json` shape")
    source.add_argument("--kanban-task-id", help="Read a live card with `hermes kanban show <id> --json`")

    parser.add_argument("--baseline-commit", help="Candidate completion commit to validate before closing a live card")
    parser.add_argument("--baseline-path", action="append", default=[], help="Candidate linked artifact path; repeat for each path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if bool(args.baseline_commit) != bool(args.baseline_path):
        parser.error("--baseline-commit and at least one --baseline-path must be supplied together")


    root = (args.setup_repo or Path(__file__).resolve().parents[3]).resolve()
    ginflow = (root / "skills/ginflow/SKILL.md").read_text()
    target = args.target.resolve() if args.target else None
    local = ""
    local_path = None
    if target:
        for name in (".hermes.md", "AGENTS.md"):
            candidate = target / name
            if candidate.exists():
                local_path, local = candidate, candidate.read_text()
                break

    card_load_error = None
    if args.card:
        card_document = json.loads(args.card.read_text())
    elif args.kanban_task_id:
        card_document, card_load_error = load_kanban_card(args.kanban_task_id)
    else:
        card_document = {}
    card = normalize_card(card_document)
    if args.baseline_commit:
        card["artifact_baseline"] = {
            "commit": args.baseline_commit,
            "paths": args.baseline_path,
        }
    card_fields = ("id", "title", "objective", "scope", "acceptance", "workspace", "status", "assignee", "links")
    linked_briefs = [candidate for path, candidate in linked_artifacts(card, target) if path.startswith("docs/briefs/")]
    brief_exists = bool(linked_briefs and any(path.exists() for path in linked_briefs))
    artifact_status = artifact_gate(card, target)

    verify_match = re.search(r"(?:Canonical (?:verification )?command|Verification)[^\n]*:\s*`?([^`\n]+)", local, re.I)
    verification_documented = bool(verify_match)

    subsystems = {
        "instructions": check("instructions", [
            (True, "Profile routing is distribution-owned; setup repo validates ginflow only", "warning"),
            (all(has(ginflow, heading) for heading in ("## Project session startup", "## Execution contract", "## Definition of done", "## Completion report")), "Canonical ginflow instruction sections exist", "warning"),
            (not target or bool(local_path), "Target local instruction file exists when target supplied", "warning"),
            (not target or has(local, "come from `ginflow`"), "Target local instructions route shared workflow to ginflow when target supplied", "warning"),
        ]),
        "state": check("state", [
            (
                not card_load_error and bool(card) and all(card.get(field) for field in card_fields),
                "Selected card has required fields",
                "blocker",
                card_load_error or "required Ginflow fields are missing from the card body or metadata",
                "Use Objective, Scope, Acceptance, and Links sections in the card body, plus a real target workspace and assignee.",
            ),
            (brief_exists, "Card-ID brief exists", "blocker"),
            (
                artifact_status["baseline_complete"],
                "Card records a path-scoped completion commit baseline",
                "blocker",
                artifact_status["baseline_details"],
                artifact_status["baseline_resolution"],
            ),
            (
                artifact_status["matches"],
                "Linked artifacts match the recorded completion commit",
                "blocker",
                artifact_status["drift_details"],
                artifact_status["drift_resolution"],
            ),
            (not target or not (target / "session-handoff.md").exists(), "Mandatory root session handoff is absent", "warning"),
        ], exercised=bool(target)),
        "verification": check("verification", [
            (verification_documented, "Canonical project verification is documented", "blocker"),
            (has(ginflow, "Quote canonical") and has(ginflow, "exact fresh result"), "Fresh evidence format is required", "warning"),
        ], exercised=bool(target)),
        "scope": check("scope", [
            (has(ginflow, "One active card per mutable workspace"), "Mutable-workspace isolation rule exists", "warning"),
            (bool(card and all(card.get(field) for field in ("scope", "acceptance", "workspace"))), "Card tracks scope, acceptance, and workspace", "blocker"),
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
    result = {
        "setup_repo": str(root),
        "target": str(target) if target else None,
        "kanban_task_id": args.kanban_task_id,
        "candidate_baseline": bool(args.baseline_commit),
        "card_load_error": card_load_error,
        "subsystems": subsystems,
    }
    statuses = {item["status"] for item in subsystems.values()}
    result["status"] = "blocker" if "blocker" in statuses else "warning" if "warning" in statuses else "pass"
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, item in subsystems.items():
            print(f"{name}: {item['status']}")
            for row in item["checks"]:
                print(f"  {'PASS' if row['pass'] else 'FAIL'} {row['message']}")
                if not row["pass"] and row.get("details"):
                    print(f"    Details: {row['details']}")
                if not row["pass"] and row.get("resolution"):
                    print(f"    Resolution: {row['resolution']}")
    return 2 if result["status"] == "blocker" else 0


if __name__ == "__main__":
    sys.exit(main())