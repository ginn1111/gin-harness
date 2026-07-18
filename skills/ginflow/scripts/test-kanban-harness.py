#!/usr/bin/env python3
import json
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


def run(target, card=None):
    command = ["python3", str(VALIDATOR), "--setup-repo", str(ROOT), "--target", str(target), "--json"]
    if card:
        command += ["--card", str(card)]
    return subprocess.run(command, text=True, capture_output=True)


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

        incomplete = complete.copy()
        del incomplete["acceptance"]
        card.write_text(json.dumps(incomplete))
        blocked = run(target, card)
        assert blocked.returncode == 2
        assert json.loads(blocked.stdout)["status"] == "blocker"

    print("ginflow Kanban harness test passed")


if __name__ == "__main__":
    main()
