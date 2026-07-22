#!/usr/bin/env python3
"""Test script: agent completes card via kanban_complete tool and verifies brief update."""

import json
import subprocess
from pathlib import Path

# Step 1: create card with linked brief
CARD_TITLE = "GINFLOW-3 Test tool-based completion"
CARD_BODY = """Objective: Test that ginflow-gate post_tool_call hook updates linked artifacts when using kanban_complete TOOL (not CLI).
Scope:
- Create linked brief
- Complete card via kanban_complete tool
- Verify brief gets footer
Acceptance:
- Hook logs updated artifact
Links:
- docs/briefs/GINFLOW-3.md"""

CREATE_CMD = [
    "hermes", "kanban", "create", CARD_TITLE,
    "--body", CARD_BODY,
    "--initial-status", "blocked",
    "--workspace", "dir:/Users/gin/dev/agent-hype",
    "--assignee", "gintary",
    "--json"
]

result = subprocess.run(CREATE_CMD, text=True, capture_output=True)
if result.returncode != 0:
    print(f"Create failed: {result.stderr}")
    exit(1)

card = json.loads(result.stdout)
task_id = card["id"]
print(f"Created card: {task_id}")

# Step 2: write brief file
brief_path = Path("/Users/gin/dev/agent-hype/docs/briefs/GINFLOW-3.md")
brief_path.parent.mkdir(parents=True, exist_ok=True)
brief_path.write_text(f"""# GINFLOW-3 — Test tool-based completion

## Objective

Test that ginflow-gate post_tool_call hook updates linked artifacts when using kanban_complete TOOL.

## Scope

- Create linked brief
- Complete card via kanban_complete tool
- Verify brief gets footer

## Acceptance criteria

- Hook logs updated artifact to stderr
- Brief file ends with completion footer
""")

# Step 3: commit brief
subprocess.run(["git", "add", "docs/briefs/GINFLOW-3.md"], cwd="/Users/gin/dev/agent-hype", check=True)
commit_result = subprocess.run(
    ["git", "commit", "-m", "GINFLOW-3: create test brief"],
    cwd="/Users/gin/dev/agent-hype",
    text=True, capture_output=True
)
commit = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd="/Users/gin/dev/agent-hype",
    text=True, capture_output=True
).stdout.strip()
print(f"Brief committed at {commit}")

# Step 4: report - agent should call kanban_complete tool here
print("\n=== AGENT SHOULD NOW CALL ===")
print(f"kanban_complete(task_id='{task_id}', result='test', metadata={{'verification_result': {{'commit': '{commit[:7]}', 'command': 'make test', 'result': 'passed'}}, 'artifact_baseline': {{'commit': '{commit[:7]}', 'paths': ['docs/briefs/GINFLOW-3.md']}}}})")
