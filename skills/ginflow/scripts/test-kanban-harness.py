#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "skills/ginflow/scripts/validate-harness.py"
CARD_FIELDS = {
    "id": "TEST-1",
    "title": "Test",
    "objective": "Verify gate",
    "scope": ["target"],
    "acceptance": ["check passes"],
    "workspace": "",
    "status": "ready",
    "assignee": "ginb",
    "links": ["docs/briefs/TEST-1.md"],
}


def run(target, card=None, task_id=None, board=None, env=None, baseline_commit=None, baseline_paths=None):
    command = ["python3", str(VALIDATOR), "--setup-repo", str(ROOT), "--target", str(target), "--json"]
    if card:
        command += ["--card", str(card)]
    if task_id:
        command += ["--kanban-task-id", task_id]
    if board:
        command += ["--board", board]
    if baseline_commit:
        command += ["--baseline-commit", baseline_commit]
    for path in baseline_paths or []:
        command += ["--baseline-path", path]
    return subprocess.run(command, text=True, capture_output=True, env=env)


def git(target, *args):
    return subprocess.run(
        ["git", *args], cwd=target, text=True, capture_output=True, check=True
    ).stdout.strip()


def create_live_card(env, target, body, board=None):
    subprocess.run(["hermes", "kanban", "init"], env=env, text=True, capture_output=True, check=True)
    if board:
        subprocess.run(
            ["hermes", "kanban", "boards", "create", board],
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
    create_command = ["hermes", "kanban"]
    if board:
        create_command += ["--board", board]
    created = subprocess.run(
        create_command + [
            "create", "TEST-1 — Test",
            "--body", body,
            "--assignee", "ginb",
            "--workspace", f"dir:{target}",
            "--initial-status", "blocked",
            "--json",
        ],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(created.stdout)["id"]


def main():
    with tempfile.TemporaryDirectory(prefix="ginflow-harness-") as directory:
        target = Path(directory)
        (target / "AGENTS.md").write_text(
            "Shared workflow rules come from `ginflow`.\n"
            "## Verification\nCanonical command: `make check`\n"
            "## Boundaries\nDo not edit generated files.\n"
        )

        missing = run(target)
        assert missing.returncode == 2, missing.stdout + missing.stderr
        missing_result = json.loads(missing.stdout)
        assert missing_result["status"] == "blocker"
        assert missing_result["subsystems"]["state"]["status"] == "blocker"

        card = target / "card.json"
        complete = CARD_FIELDS | {"workspace": f"dir:{target}"}
        card.write_text(json.dumps(complete))
        (target / "docs/briefs").mkdir(parents=True)
        (target / "docs/briefs/TEST-1.md").write_text("# Brief\n")
        valid = run(target, card)
        assert valid.returncode == 0, valid.stdout + valid.stderr
        valid_result = json.loads(valid.stdout)
        assert valid_result["status"] == "pass", valid.stdout

        kanban_show = {
            "task": {
                "id": "TEST-1",
                "title": "TEST-1 — Test",
                "body": (
                    "Objective: Verify gate\n"
                    "Scope:\n- target\n"
                    "Acceptance:\n- check passes\n"
                    "Links:\n- docs/briefs/TEST-1.md"
                ),
                "assignee": "ginb",
                "status": "ready",
                "workspace_kind": "dir",
                "workspace_path": str(target),
            },
            "latest_summary": None,
            "parents": [],
            "children": [],
            "comments": [],
            "events": [],
            "runs": [],
        }
        card.write_text(json.dumps(kanban_show))
        actual_shape = run(target, card)
        assert actual_shape.returncode == 0, actual_shape.stdout + actual_shape.stderr
        assert json.loads(actual_shape.stdout)["status"] == "pass"

        malformed_show = json.loads(json.dumps(kanban_show))
        malformed_show["task"]["body"] = (
            "Objective: Verify gate\n"
            "Scope:\n- target\n"
            "Links:\n- docs/briefs/TEST-1.md"
        )
        card.write_text(json.dumps(malformed_show))
        malformed = run(target, card)
        assert malformed.returncode == 2, malformed.stdout + malformed.stderr
        malformed_result = json.loads(malformed.stdout)
        assert malformed_result["status"] == "blocker"
        required = next(
            check for check in malformed_result["subsystems"]["state"]["checks"]
            if check["message"] == "Selected card has required fields"
        )
        assert required["pass"] is False

        with tempfile.TemporaryDirectory(prefix="ginflow-kanban-home-") as hermes_home:
            env = os.environ | {"HERMES_HOME": hermes_home}
            task_id = create_live_card(env, target, kanban_show["task"]["body"])
            live_card = run(target, task_id=task_id, env=env)
            assert live_card.returncode == 0, live_card.stdout + live_card.stderr
            assert json.loads(live_card.stdout)["status"] == "pass"
            missing_card = run(target, task_id="t_missing", env=env)
            assert missing_card.returncode == 2, missing_card.stdout + missing_card.stderr
            missing_result = json.loads(missing_card.stdout)
            assert missing_result["status"] == "blocker"
            assert "t_missing" in missing_result["card_load_error"]

        with tempfile.TemporaryDirectory(prefix="ginflow-kanban-home-") as hermes_home:
            env = os.environ | {"HERMES_HOME": hermes_home}
            task_id = create_live_card(env, target, kanban_show["task"]["body"], board="product")
            named_board = run(target, task_id=task_id, board="product", env=env)
            assert named_board.returncode == 0, named_board.stdout + named_board.stderr
            assert json.loads(named_board.stdout)["status"] == "pass"

        incomplete = complete.copy()
        del incomplete["acceptance"]
        card.write_text(json.dumps(incomplete))
        blocked = run(target, card)
        assert blocked.returncode == 2
        assert json.loads(blocked.stdout)["status"] == "blocker"

        brief = target / "docs/briefs/TEST-1.md"
        (target / "app.py").write_text("VERSION = 1\n")
        git(target, "init", "-q")
        git(target, "config", "user.name", "Ginflow Test")
        git(target, "config", "user.email", "ginflow@example.test")
        git(target, "add", "AGENTS.md", "app.py", "docs/briefs/TEST-1.md")
        git(target, "commit", "-qm", "complete TEST-1")
        completion_commit = git(target, "rev-parse", "HEAD")
        with tempfile.TemporaryDirectory(prefix="ginflow-kanban-home-") as hermes_home:
            env = os.environ | {"HERMES_HOME": hermes_home}
            task_id = create_live_card(env, target, kanban_show["task"]["body"])
            candidate = run(
                target,
                task_id=task_id,
                env=env,
                baseline_commit=completion_commit,
                baseline_paths=["docs/briefs/TEST-1.md"],
            )
            assert candidate.returncode == 0, candidate.stdout + candidate.stderr
            assert json.loads(candidate.stdout)["status"] == "pass"
            subprocess.run(
                [
                    "hermes", "kanban", "complete", task_id,
                    "--summary", "verified",
                    "--metadata", json.dumps({
                        "artifact_baseline": {
                            "commit": completion_commit,
                            "paths": ["docs/briefs/TEST-1.md"],
                        },
                    }),
                ],
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            live_completed = run(target, task_id=task_id, env=env)
            assert live_completed.returncode == 0, live_completed.stdout + live_completed.stderr
            assert json.loads(live_completed.stdout)["status"] == "pass"

        completed = json.loads(json.dumps(kanban_show))
        completed["task"]["status"] = "done"
        completed["runs"] = [{
            "id": 2,
            "status": "completed",
            "outcome": "completed",
            "metadata": {
                "artifact_baseline": {
                    "commit": completion_commit,
                    "paths": ["docs/briefs/TEST-1.md"],
                },
            },
        }, {
            "id": 1,
            "status": "completed",
            "outcome": "completed",
            "metadata": {
                "artifact_baseline": {
                    "commit": "obsolete-run",
                    "paths": ["docs/briefs/TEST-1.md"],
                },
            },
        }]
        card.write_text(json.dumps(completed))
        unchanged = run(target, card)
        assert unchanged.returncode == 0, unchanged.stdout + unchanged.stderr

        (target / "app.py").write_text("VERSION = 2\n")
        git(target, "add", "app.py")
        git(target, "commit", "-qm", "unrelated implementation change")
        unrelated = run(target, card)
        assert unrelated.returncode == 0, unrelated.stdout + unrelated.stderr

        brief.write_text("# Brief\n\nHuman changed acceptance after completion.\n")
        git(target, "add", "docs/briefs/TEST-1.md")
        git(target, "commit", "-qm", "change completed acceptance")
        drifted = run(target, card)
        assert drifted.returncode == 2, drifted.stdout + drifted.stderr
        drifted_result = json.loads(drifted.stdout)
        assert drifted_result["status"] == "blocker"
        drift_check = next(
            row
            for row in drifted_result["subsystems"]["state"]["checks"]
            if row["message"] == "Linked artifacts match the recorded completion commit"
        )
        assert not drift_check["pass"]
        assert "docs/briefs/TEST-1.md" in drift_check["details"]
        assert "create new versioned docs" in drift_check["resolution"]
        assert "link back" in drift_check["resolution"]
        assert "reopen card TEST-1" in drift_check["resolution"]
        assert "editorial" in drift_check["resolution"]

        current_commit = git(target, "rev-parse", "HEAD")
        uncommitted = complete | {
            "status": "in_progress",
            "artifact_baseline": {
                "commit": current_commit,
                "paths": ["docs/briefs/TEST-1.md"],
            }
        }
        brief.write_text("# Brief\n\nUncommitted completion edit.\n")
        card.write_text(json.dumps(uncommitted))
        dirty = run(target, card)
        assert dirty.returncode == 2, dirty.stdout + dirty.stderr
        dirty_result = json.loads(dirty.stdout)
        dirty_check = next(
            row
            for row in dirty_result["subsystems"]["state"]["checks"]
            if row["message"] == "Linked artifacts match the recorded completion commit"
        )
        assert not dirty_check["pass"]
        assert "commit linked artifacts" in dirty_check["resolution"].lower()

        no_baseline = complete | {"status": "done"}
        card.write_text(json.dumps(no_baseline))
        unguarded = run(target, card)
        assert unguarded.returncode == 2, unguarded.stdout + unguarded.stderr
        unguarded_result = json.loads(unguarded.stdout)
        baseline_check = next(
            row
            for row in unguarded_result["subsystems"]["state"]["checks"]
            if row["message"] == "Card records a path-scoped completion commit baseline"
        )
        assert not baseline_check["pass"]
        assert "reopen card test-1" in baseline_check["resolution"].lower()

        brief.write_text("# Brief\n\nHuman changed acceptance after completion.\n")
        untracked_spec = target / "docs/specs/TEST-1.md"
        untracked_spec.parent.mkdir(parents=True)
        untracked_spec.write_text("# Uncommitted spec\n")
        missing_from_commit = complete | {
            "status": "in_progress",
            "links": ["docs/briefs/TEST-1.md", "docs/specs/TEST-1.md"],
            "artifact_baseline": {
                "commit": current_commit,
                "paths": ["docs/briefs/TEST-1.md", "docs/specs/TEST-1.md"],
            },
        }
        card.write_text(json.dumps(missing_from_commit))
        uncommitted_new = run(target, card)
        assert uncommitted_new.returncode == 2, uncommitted_new.stdout + uncommitted_new.stderr
        uncommitted_new_result = json.loads(uncommitted_new.stdout)
        baseline_check = next(
            row
            for row in uncommitted_new_result["subsystems"]["state"]["checks"]
            if row["message"] == "Card records a path-scoped completion commit baseline"
        )
        assert not baseline_check["pass"]
        assert "docs/specs/TEST-1.md" in baseline_check["details"]

    print("ginflow Kanban harness test passed")


if __name__ == "__main__":
    main()
