#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills/ginflow"


def require(text, values, source):
    missing = [value for value in values if value not in text]
    assert not missing, f"{source}: missing {missing}"


def main():
    skill = (SKILL / "SKILL.md").read_text()
    layout = (SKILL / "references/doc-layout.md").read_text()
    content = (SKILL / "references/artifact-content-guide.md").read_text()
    kanban = (SKILL / "references/kanban-guide.md").read_text()
    drift = (SKILL / "references/drift-detect.md").read_text()

    artifact_paths = (
        "docs/briefs/<CARD-ID>.md",
        "docs/specs/<CARD-ID>.md",
        "docs/plans/<CARD-ID>.md",
        "docs/handoffs/<CARD-ID>.md",
        "docs/adrs/",
    )
    require(skill, artifact_paths, "SKILL.md")
    require(layout, artifact_paths, "doc-layout.md")
    require(kanban, artifact_paths[:3], "kanban-guide.md")

    require(content, (
        "## Authority and boundaries",
        "## Brief",
        "## Spec",
        "## Plan",
        "## Kanban card",
        "## ADR",
        "## Session handoff",
        "observable, testable, atomic",
        "never invent them",
        "Record unresolved drift on card",
        "docs/adrs/NNNN-<kebab-title>.md",
    ), "artifact-content-guide.md")

    require(skill, (
        "No selected card blocks project execution",
        "Never copy harness script into target repo",
        "Report project verification and ginflow harness as separate results",
    ), "SKILL.md")
    require(kanban, ("No selected card blocks execution", "never copy harness into target repo"), "kanban-guide.md")
    require(drift, ("Never copy harness script into target repo", "Project verification: pass|fail|blocked"), "drift-detect.md")

    for template in ("brief.md", "spec.md", "plan.md", "kanban-task.md", "session-handoff.md"):
        text = (SKILL / "templates" / template).read_text()
        require(text, ("references/artifact-content-guide.md",), template)

    legacy_paths = ("`briefs/<CARD-ID>.md`", "`specs/<CARD-ID>.md`", "`plans/<CARD-ID>.md`", "`adrs/`")
    for path in (SKILL / "SKILL.md", SKILL / "references/doc-layout.md", SKILL / "references/kanban-guide.md"):
        text = path.read_text()
        found = [value for value in legacy_paths if value in text]
        assert not found, f"{path.name}: legacy root paths remain: {found}"

    print("ginflow artifact guidance test passed")


if __name__ == "__main__":
    main()
