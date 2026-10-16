#!/usr/bin/env python3
"""Emit an evaluation prompt corpus without gold labels or strategy answers."""
import argparse
import json
from pathlib import Path
from sys import stdout

EXPOSE = (
    "id", "kind", "safety_state", "rebuildability", "offline_risk",
    "workload_impact", "native_cleanup_available", "measured_mib",
    "evidence_ids",
)
FORBIDDEN = {"human_expected", "label_rationale", "acceptable_strategies"}

def redact_cases(data):
    assert isinstance(data.get("cases"), list) and data["cases"]
    examples = [{k: case[k] for k in EXPOSE} for case in data["cases"]]
    assert all(FORBIDDEN.isdisjoint(example) for example in examples)
    return {
        "purpose": "BLIND SYNTHETIC DECISION EVALUATION ONLY; NOT A CLEANUP PLAN",
        "dataset_id": data.get("dataset_id", "synthetic"),
        "instructions": ("Classify each case RECOMMEND, DEFER or KEEP; specify "
                         "NATIVE_PRUNE, NATIVE_CLEAN, EXACT_PATH or NONE; "
                         "include a reason and cite evidence_ids supplied."),
        "cases": examples
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases", type=Path, required=True)
    args = p.parse_args()
    raw = json.loads(args.cases.read_text(encoding="utf-8"))
    print(json.dumps(redact_cases(raw), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
