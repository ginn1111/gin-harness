# GINFLOW-5 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Require Ginflow agents to load `plan` before creating plans for planning-required work.

**Architecture:** Keep one instruction in Ginflow task-shaping guidance and mirror it in both routing-context branches. Extend existing stdlib assertion test.

**Tech Stack:** Markdown, Python standard library, Make.

---

### Task 1: Add Ginflow planning instruction

**Objective:** Make task-shaping guidance require `plan` before plan creation.

**Files:**
- Modify: `skills/ginflow/SKILL.md:77-83`

**Step 1:** Add one rule: planning-required work loads and follows `plan` before creating a plan.

**Step 2:** Review wording against card acceptance.

### Task 2: Mirror instruction in routing context

**Objective:** Preserve instruction in routing output for empty and active boards.

**Files:**
- Modify: `plugins/ginflow-routing/__init__.py:93-108`

**Step 1:** Add exact plan-skill instruction to both context strings.

**Step 2:** Keep existing board routing behavior unchanged.

### Task 3: Lock behavior with regression coverage

**Objective:** Prove active Ginflow context contains instruction.

**Files:**
- Modify: `skills/ginflow/scripts/test-ginflow-routing.py:50-89`

**Step 1:** Assert active routing context contains `load and follow the `plan` skill before creating a plan`.

**Step 2:** Run `python3 skills/ginflow/scripts/test-ginflow-routing.py`.

Expected: `ginflow routing test passed`.

### Task 4: Verify repository

**Objective:** Check docs, plugin, and regression under canonical targets.

**Files:**
- Review: `skills/ginflow/SKILL.md`
- Review: `plugins/ginflow-routing/__init__.py`
- Review: `skills/ginflow/scripts/test-ginflow-routing.py`

**Step 1:** Run `make lint`.

Expected: `lint ok`.

**Step 2:** Run `make test`.

Expected: all test targets pass.

## Risks / open questions

- No runtime logic changes. Routing instruction is advisory context only.
