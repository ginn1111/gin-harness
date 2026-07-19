# Skill Benchmark: ginflow

**Model**: gpt-5.6-sol
**Date**: 2026-07-18T19:00:47Z
**Evals**: 10, 11, 12 (1 runs each per configuration)

## Summary

| Metric | With Skill | Old Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 38% ± 38% | +0.62 |
| Time | 108.1s ± 30.5s | 132.7s ± 35.1s | -24.6s |
| Tokens | 0 ± 0 | 0 ± 0 | +0 |

## Notes

- Current Ginflow passed all 14 assertions across the three Kanban integration evals; the old snapshot passed 5 of 14.
- The atomic completion eval is the strongest discriminator: current Ginflow passed 5/5 while the old snapshot passed 0/5 and substituted per-file SHA hashes plus a temporary card snapshot.
- The live startup adapter eval distinguishes direct board integration: current Ginflow uses --kanban-task-id/--board and in-memory normalization, while the old snapshot requires a temporary normalized --card JSON.
- The malformed-body eval is less discriminating: both versions block missing Acceptance and avoid inventing criteria; only current Ginflow explicitly reruns the live-card harness after repair.
- Current Ginflow averaged 24.6 seconds less total executor-plus-grader time per eval in this single-run sample; the reported standard deviation is variation across three different evals, not repeat-run variance.
- Token counts were not present in delegation notifications, so token statistics are unavailable rather than inferred as a measured zero.
- One assertion was refined from “runs the harness” to “provides the harness command” because the advisory prompt supplied no real target repository on which execution could be verified.
- Deterministic tests use isolated HERMES_HOME instances and prove the adapter against the real Hermes Kanban CLI, including a non-current named board; they do not prove that the production ginb profile is installed.
- A final global profile verification found gintary healthy but ginb absent from the active Hermes profile registry, so real gintary→ginb dispatch remains operationally blocked until the profile installation is repaired and reverified.
