#!/usr/bin/env python3
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ITERATION = ROOT / "iteration-1"
CONFIGS = ("with_skill", "old_skill")


def stats(values):
    return {
        "mean": round(statistics.mean(values), 4) if values else 0.0,
        "stddev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
        "min": round(min(values), 4) if values else 0.0,
        "max": round(max(values), 4) if values else 0.0,
    }


def main():
    runs = []
    for eval_dir in sorted(ITERATION.glob("eval-*")):
        metadata = json.loads((eval_dir / "eval_metadata.json").read_text())
        for config in CONFIGS:
            grading = json.loads((eval_dir / config / "grading.json").read_text())
            metrics = grading.get("execution_metrics", {})
            notes = grading.get("user_notes_summary", {})
            runs.append({
                "eval_id": metadata["eval_id"],
                "eval_name": metadata["eval_name"],
                "configuration": config,
                "run_number": 1,
                "result": {
                    "pass_rate": grading["summary"]["pass_rate"],
                    "passed": grading["summary"]["passed"],
                    "failed": grading["summary"]["failed"],
                    "total": grading["summary"]["total"],
                    "time_seconds": 0.0,
                    "tokens": metrics.get("output_chars", 0),
                    "tool_calls": metrics.get("total_tool_calls", 0),
                    "errors": metrics.get("errors_encountered", 0),
                    "expectations": grading["expectations"],
                    "notes": notes.get("uncertainties", []) + notes.get("needs_review", []) + notes.get("workarounds", []),
                },
            })

    summary = {}
    for config in CONFIGS:
        config_runs = [run["result"] for run in runs if run["configuration"] == config]
        summary[config] = {
            "pass_rate": stats([run["pass_rate"] for run in config_runs]),
            "time_seconds": stats([run["time_seconds"] for run in config_runs]),
            "tokens": stats([run["tokens"] for run in config_runs]),
        }
    summary["delta"] = {
        "pass_rate": f"{summary['with_skill']['pass_rate']['mean'] - summary['old_skill']['pass_rate']['mean']:+.4f}",
        "time_seconds": "+0.0",
        "tokens": f"{summary['with_skill']['tokens']['mean'] - summary['old_skill']['tokens']['mean']:+.1f}",
    }

    benchmark = {
        "metadata": {
            "skill_name": "ginflow",
            "skill_path": str((ROOT.parent.parent / "ginflow").resolve()),
            "executor_model": "gpt-5.6-sol",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evals_run": [7, 8, 9],
            "runs_per_configuration": 1,
            "paired_eval_duration_seconds": {"7": 43.53, "8": 56.55, "9": 59.95},
            "parallel_batch_wall_clock_seconds": 60.02,
            "grading_duration_seconds": {"7": 120.03, "8": 132.81, "9": 115.77},
            "grading_batch_wall_clock_seconds": 132.87,
        },
        "runs": runs,
        "run_summary": summary,
        "notes": [
            "Each delegated evaluator produced both paired outputs, so per-configuration timing is unavailable. Combined paired durations were 43.53s, 56.55s, and 59.95s; parallel batch wall clock was 60.02s.",
            "Grading durations were 120.03s, 132.81s, and 115.77s; grading batch wall clock was 132.87s.",
            "Output characters are reported as a size proxy, not token counts.",
            "Eval 8 preserves the unrelated-change regression while also checking the commit-baseline mechanism; evals 7 and 9 cover drift resolution and completion blocking.",
            "One run per configuration measures correctness but not variance; stddev is therefore zero and should not be interpreted as stability evidence.",
        ],
    }
    (ITERATION / "benchmark.json").write_text(json.dumps(benchmark, indent=2) + "\n")

    lines = ["# Ginflow commit-drift benchmark", "", "| Configuration | Mean pass rate | Output chars |", "|---|---:|---:|"]
    for config in CONFIGS:
        lines.append(f"| {config} | {summary[config]['pass_rate']['mean']:.1%} | {summary[config]['tokens']['mean']:.0f} |")
    lines.extend([
        "",
        "## Paired execution timing",
        "",
        "| Eval | Combined current + old duration |",
        "|---|---:|",
        "| 7 | 43.53s |",
        "| 8 | 56.55s |",
        "| 9 | 59.95s |",
        "",
        "Parallel batch wall clock: **60.02s**.",
        "",
        "## Grading timing",
        "",
        "| Eval | Grading duration |",
        "|---|---:|",
        "| 7 | 120.03s |",
        "| 8 | 132.81s |",
        "| 9 | 115.77s |",
        "",
        "Grading batch wall clock: **132.87s**.",
        "",
        "## Notes",
        *[f"- {note}" for note in benchmark["notes"]],
        "",
    ])
    (ITERATION / "benchmark.md").write_text("\n".join(lines))
    print(ITERATION / "benchmark.json")


if __name__ == "__main__":
    main()
