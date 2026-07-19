#!/usr/bin/env python3
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "skills/ginflow/lib/harness_core.py"

spec = importlib.util.spec_from_file_location("harness_core", CORE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

fields = module.parse_card_body(
    "Objective: Ship gate\nScope:\n- plugin\nAcceptance:\n- rejects bad completion\nLinks:\n- docs/briefs/GATE-1.md"
)
assert fields == {
    "objective": "Ship gate",
    "scope": ["plugin"],
    "acceptance": ["rejects bad completion"],
    "links": ["docs/briefs/GATE-1.md"],
}
print("ginflow harness core test passed")
