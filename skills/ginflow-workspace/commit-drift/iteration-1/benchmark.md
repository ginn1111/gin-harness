# Ginflow commit-drift benchmark

| Configuration | Mean pass rate | Output chars |
|---|---:|---:|
| with_skill | 100.0% | 1039 |
| old_skill | 64.0% | 939 |

## Paired execution timing

| Eval | Combined current + old duration |
|---|---:|
| 7 | 43.53s |
| 8 | 56.55s |
| 9 | 59.95s |

Parallel batch wall clock: **60.02s**.

## Grading timing

| Eval | Grading duration |
|---|---:|
| 7 | 120.03s |
| 8 | 132.81s |
| 9 | 115.77s |

Grading batch wall clock: **132.87s**.

## Notes
- Each delegated evaluator produced both paired outputs, so per-configuration timing is unavailable. Combined paired durations were 43.53s, 56.55s, and 59.95s; parallel batch wall clock was 60.02s.
- Grading durations were 120.03s, 132.81s, and 115.77s; grading batch wall clock was 132.87s.
- Output characters are reported as a size proxy, not token counts.
- Eval 8 preserves the unrelated-change regression while also checking the commit-baseline mechanism; evals 7 and 9 cover drift resolution and completion blocking.
- One run per configuration measures correctness but not variance; stddev is therefore zero and should not be interpreted as stability evidence.
