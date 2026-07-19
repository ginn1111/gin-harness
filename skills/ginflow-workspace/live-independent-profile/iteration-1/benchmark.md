# Live independent-profile behavior — iteration 1

Behavior: switching to `gintary` or `ginb` leaves selected profile working alone, without implicit collaboration.

| Configuration | Passed | Total | Pass rate |
|---|---:|---:|---:|
| Current skill | 10 | 12 | 83.3% |
| Pinned baseline | 10 | 12 | 83.3% |

Delta: **+0 assertions / +0.0%**.

Runs: 12 live Hermes responses: 3 prompts × 2 profiles × 2 configurations. One run each; correctness only, no variance claim.

Grading: manual assertion review. Assertion passes only when both `gintary` and `ginb` sections satisfy it.

## Finding

Both current and pinned baseline scored 10/12. Live agents followed explicit no-collaboration prompts under both policy snapshots. This iteration confirms current live behavior but **does not show improvement over baseline**. Next iteration needs prompts that do not state desired solo policy, so profile-role assumptions can emerge without answer contamination.

## Limits

- One run per profile/configuration measures correctness only, not variance or confidence.
- Prompts explicitly request solo behavior, reducing discrimination between current and baseline.
- Both configurations run through current installed profile runtime; policy snapshot differs, but model/provider/config remain current.
- Agent responses included profile config warnings; these did not affect policy grading.
- No project files, Kanban cards, or remote systems were mutated during live prompts.
