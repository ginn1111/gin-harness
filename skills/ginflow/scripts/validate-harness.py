#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def check(name, tests, exercised=True):
    if not exercised:
        return {"status": "not_exercised", "checks": []}
    rows = []
    for test in tests:
        ok, message, severity, *context = test
        row = {"pass": ok, "message": message, "severity": severity}
        if context and not ok:
            row["details"], row["resolution"] = context
        rows.append(row)
    failed = [row for row in rows if not row["pass"]]
    status = "blocker" if any(row["severity"] == "blocker" for row in failed) else "warning" if failed else "pass"
    return {"status": status, "checks": rows}


def has(text, value):
    return value.lower() in text.lower()


def parse_card_body(body):
    fields = {"objective": "", "scope": [], "acceptance": [], "links": []}
    current = None
    for raw_line in str(body or "").splitlines():
        line = raw_line.strip()
        heading = re.match(r"^(?:#{1,6}\s*)?(Objective|Scope|Acceptance|Links):\s*(.*)$", line, re.I)
        if heading:
            current = heading.group(1).lower()
            value = heading.group(2).strip().strip("`")
            if value:
                if current == "objective":
                    fields[current] = value
                else:
                    fields[current].append(value)
            continue
        if current and line.startswith(("- ", "* ")):
            value = line[2:].strip().strip("`")
            if current == "objective":
                fields[current] = value
            elif value:
                fields[current].append(value)
    return fields


def normalize_card(document):
    task = document.get("task") if isinstance(document, dict) else None
    if not isinstance(task, dict):
        return document if isinstance(document, dict) else {}

    fields = parse_card_body(task.get("body"))
    metadata_runs = [
        run for run in document.get("runs", [])
        if isinstance(run, dict) and isinstance(run.get("metadata"), dict)
    ]
    metadata = {}
    if metadata_runs:
        def run_order(run):
            run_id = run.get("id")
            if isinstance(run_id, int):
                return 2, run_id
            return 1, str(run.get("finished_at") or run.get("started_at") or run_id or "")

        metadata = max(metadata_runs, key=run_order)["metadata"]
    ginflow_metadata = metadata.get("ginflow", {}) if isinstance(metadata.get("ginflow"), dict) else {}
    for name in ("objective", "scope", "acceptance", "links"):
        if name in ginflow_metadata:
            fields[name] = ginflow_metadata[name]

    workspace_kind = task.get("workspace_kind")
    workspace_path = task.get("workspace_path")
    workspace = workspace_kind or ""
    if workspace_kind in {"dir", "worktree"} and workspace_path:
        workspace = f"{workspace_kind}:{workspace_path}"

    card = {
        "id": task.get("id"),
        "title": task.get("title"),
        "objective": fields["objective"],
        "scope": fields["scope"],
        "acceptance": fields["acceptance"],
        "workspace": workspace,
        "status": task.get("status"),
        "assignee": task.get("assignee"),
        "links": fields["links"],
    }
    if "artifact_baseline" in metadata:
        card["artifact_baseline"] = metadata["artifact_baseline"]
    return card


def load_kanban_card(task_id, board=None):
    command = ["hermes", "kanban"]
    if board:
        command += ["--board", board]
    command += ["show", task_id, "--json"]
    try:
        result = subprocess.run(command, text=True, capture_output=True)
    except OSError as error:
        return {}, f"Unable to run Hermes Kanban for card {task_id}: {error}"
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        return {}, f"Unable to read Kanban card {task_id}: {detail}"
    if not result.stdout.strip():
        return {}, f"Kanban card {task_id} returned no JSON; verify the task ID and board"
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as error:
        return {}, f"Kanban card {task_id} returned invalid JSON: {error}"


def linked_artifacts(card, target):
    if not target:
        return []
    artifacts = []
    for link in card.get("links", []):
        path = link.get("path") if isinstance(link, dict) else link
        if not isinstance(path, str) or "://" in path:
            continue
        candidate = (target / path).resolve()
        try:
            relative = candidate.relative_to(target)
        except ValueError:
            continue
        if relative.parts[:1] == ("docs",):
            artifacts.append((relative.as_posix(), candidate))
    return artifacts


def artifact_gate(card, target):
    completed = str(card.get("status", "")).lower() in {"done", "completed", "closed"}
    baseline = card.get("artifact_baseline")
    guarded = completed or baseline is not None
    artifacts = linked_artifacts(card, target) if guarded else []
    linked_paths = [path for path, _ in artifacts]
    commit = baseline.get("commit") if isinstance(baseline, dict) else None
    baseline_commit = commit if isinstance(commit, str) else ""
    paths = baseline.get("paths") if isinstance(baseline, dict) else None
    schema_valid = (
        isinstance(commit, str)
        and bool(commit)
        and isinstance(paths, list)
        and all(isinstance(path, str) for path in paths)
        and set(paths) == set(linked_paths)
    )
    commit_valid = False
    missing_from_commit = []
    if schema_valid and target:
        commit_check = subprocess.run(
            ["git", "cat-file", "-e", f"{baseline_commit}^{{commit}}"],
            cwd=target,
            text=True,
            capture_output=True,
        )
        commit_valid = commit_check.returncode == 0
        if commit_valid:
            for path in linked_paths:
                path_check = subprocess.run(
                    ["git", "cat-file", "-e", f"{baseline_commit}:{path}"],
                    cwd=target,
                    text=True,
                    capture_output=True,
                )
                if path_check.returncode != 0:
                    missing_from_commit.append(path)
    baseline_complete = not artifacts or (
        schema_valid and commit_valid and not missing_from_commit
    )
    drifted = []
    if baseline_complete and artifacts:
        diff = subprocess.run(
            ["git", "diff", "--name-only", baseline_commit, "--", *linked_paths],
            cwd=target,
            text=True,
            capture_output=True,
        )
        drifted = [line for line in diff.stdout.splitlines() if line] if diff.returncode == 0 else linked_paths
    card_id = card.get("id", "<CARD-ID>")
    baseline_resolution = (
        f"Keep card {card_id} open or reopen card {card_id}. Commit linked artifacts, record artifact_baseline.commit "
        "and the exact linked paths, rerun project verification and the external harness, then complete the card."
    )
    drift_resolution = (
        f"Block use of card {card_id} as authority. Choose one: restore the completed artifacts, create new versioned docs "
        f"and a follow-up card that link back to card {card_id}; reopen card {card_id}, reconcile artifacts with "
        "implementation, acceptance, and verification evidence, commit linked artifacts, record the new completion "
        "commit, and rerun verification; or, only after explicit human classification as editorial, advance the "
        "baseline commit with an approval note. Never silently replace the completion commit."
    )
    if not artifacts:
        baseline_details = "no linked target-local docs require a completion baseline"
    elif not schema_valid:
        baseline_details = "artifact_baseline must contain commit and paths exactly matching linked target-local docs"
    elif not commit_valid:
        baseline_details = f"completion commit is unavailable: {commit}"
    elif missing_from_commit:
        baseline_details = "linked artifacts absent from completion commit: " + ", ".join(missing_from_commit)
    else:
        baseline_details = "completion commit and linked paths are recorded"
    return {
        "baseline_complete": baseline_complete,
        "baseline_details": baseline_details,
        "baseline_resolution": baseline_resolution,
        "matches": not drifted,
        "drift_details": "changed, missing, or uncommitted relative to completion commit: " + ", ".join(drifted),
        "drift_resolution": drift_resolution,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate the ginflow five-subsystem harness")
    parser.add_argument("--setup-repo", type=Path)
    parser.add_argument("--target", type=Path)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--card", type=Path, help="Card JSON file; accepts normalized Ginflow or `hermes kanban show --json` shape")
    source.add_argument("--kanban-task-id", help="Read a live card with `hermes kanban show <id> --json`")
    parser.add_argument("--board", help="Kanban board slug used with --kanban-task-id")
    parser.add_argument("--baseline-commit", help="Candidate completion commit to validate before closing a live card")
    parser.add_argument("--baseline-path", action="append", default=[], help="Candidate linked artifact path; repeat for each path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if bool(args.baseline_commit) != bool(args.baseline_path):
        parser.error("--baseline-commit and at least one --baseline-path must be supplied together")
    if args.board and not args.kanban_task_id:
        parser.error("--board requires --kanban-task-id")

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

    card_load_error = None
    if args.card:
        card_document = json.loads(args.card.read_text())
    elif args.kanban_task_id:
        card_document, card_load_error = load_kanban_card(args.kanban_task_id, args.board)
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
            (has(gintary, "load and follow `ginflow`") and has(ginb, "load and follow `ginflow`"), "Profiles route target-project work through ginflow", "warning"),
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
            (has(ginflow, "One active card per worker"), "One-active-card rule exists", "warning"),
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
