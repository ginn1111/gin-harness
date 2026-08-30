#!/usr/bin/env python3
"""Ensure live Kanban tests never write to the active working board."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_BOARD = "gin-harness-testing"
LIVE_KANBAN_TESTS = (
    ROOT / "skills/ginflow/scripts/test-kanban-harness.py",
    ROOT / "plugins/ginflow-gate/test_ginflow_gate.py",
    ROOT / "skills/ginflow/scripts/test-status-transition.sh",
    ROOT / "scripts/test-post-tool-hook.py",
)

for path in LIVE_KANBAN_TESTS:
    text = path.read_text()
    assert TEST_BOARD in text, f"{path.relative_to(ROOT)}: missing dedicated test board"

    python_commands = re.findall(
        r'\[\s*["\']hermes["\']\s*,\s*["\']kanban["\'](?P<body>.*?)]',
        text,
        re.DOTALL,
    )
    unscoped_python = [
        command
        for command in python_commands
        if not re.search(r'["\'](?:init|boards)["\']', command)
        and not re.search(r'["\']--board["\']\s*,\s*(?:[A-Za-z_]*TEST_BOARD|test_board|["\']gin-harness-testing["\'])', command)
    ]
    assert not unscoped_python, (
        f"{path.relative_to(ROOT)}: unscoped Python hermes kanban commands: {unscoped_python}"
    )

    unscoped_shell = re.findall(
        r"hermes kanban (?!boards|init)(?:create|show|complete|claim|unblock|archive|reclaim)\b",
        text,
    )
    assert not unscoped_shell, (
        f"{path.relative_to(ROOT)}: unscoped shell hermes kanban commands: {unscoped_shell}"
    )

print("Kanban test board isolation passed")
