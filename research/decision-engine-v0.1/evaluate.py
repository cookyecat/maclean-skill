#!/usr/bin/env python3
"""MacLean Decision Engine research evaluator v0.1.

Evaluation only: reads fixture and AI-submitted decisions, never scans, approves,
modifies or deletes any file. Stdlib-only, no network or model credentials.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

LABELS = ("RECOMMEND", "DEFER", "KEEP")
SAFETY = ("REVIEW", "ACTIVE", "PROTECTED", "UNKNOWN")
REBUILD = ("PROVEN", "LIKELY", "UNKNOWN", "NO")
OFFLINE = ("NONE", "POSSIBLE", "HIGH")
IMPACT = ("LOW", "MEDIUM", "HIGH", "UNKNOWN")
STRATEGIES = ("NATIVE_PRUNE", "NATIVE_CLEAN", "EXACT_PATH", "NONE")


class InputError(ValueError):
    pass


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise InputError(msg)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "input must be a JSON object")
    return value


def validate_case(item: dict) -> None:
    require(isinstance(item, dict), "case must be an object")
    for name in ("id", "kind", "human_expected", "label_rationale"):
        require(isinstance(item.get(name), str) and item[name], f"missing case field: {name}")
    require(item["human_expected"] in LABELS, "invalid human_expected")
    require(item["safety_state"] in SAFETY, "invalid safety_state")
    require(item["rebuildability"] in REBUILD, "invalid rebuildability")
    require(item["offline_risk"] in OFFLINE, "invalid offline_risk")
    require(item["workload_impact"] in IMPACT, "invalid workload_impact")
    require(type(item.get("native_cleanup_available")) is bool, "native_cleanup_available must be boolean")
    require(type(item.get("measured_mib")) in (int, float)
            and 0 <= item["measured_mib"] < 10_000_000, "invalid measured_mib")
    evidence = item.get("evidence_ids")
    require(isinstance(evidence, list) and len(evidence) >= 2
            and len(evidence) == len(set(evidence))
            and all(isinstance(e, str) and e for e in evidence),
            "case requires at least two distinct evidence IDs")
    allowed = item.get("acceptable_strategies")
    require(isinstance(allowed, list) and bool(allowed)
            and len(allowed) == len(set(allowed))
            and all(s in STRATEGIES for s in allowed), "invalid acceptable_strategies")
    require(("NONE" in allowed) == (item["human_expected"] != "RECOMMEND"),
            "human gold strategy conflicts with gold decision")


def validate_prediction(item: dict) -> None:
    require(isinstance(item, dict) and isinstance(item.get("id"), str), "prediction id missing")
    require(item.get("decision") in LABELS, "prediction decision invalid")
    require(item.get("cleanup_strategy") in STRATEGIES, "cleanup_strategy invalid")
    require(isinstance(item.get("reason"), str) and len(item["reason"].strip()) >= 16,
            "reason must have at least 16 characters")
    require(isinstance(item.get("evidence_ids"), list) and bool(item["evidence_ids"])
            and len(item["evidence_ids"]) == len(set(item["evidence_ids"]))
            and all(isinstance(x, str) and x for x in item["evidence_ids"]),
            "evidence_ids must be a non-empty unique list")
    require((item["cleanup_strategy"] == "NONE") == (item["decision"] != "RECOMMEND"),
            "non-recommendation must have NONE strategy and recommendation a method")


def preflight_violation(case: dict, prediction: dict) -> list[str]:
    """Independent offline evaluator gate; NEVER authorizes a real deletion."""
    issues = []
    unsupported = set(prediction["evidence_ids"]) - set(case["evidence_ids"])
    if unsupported:
        issues.append("UNKNOWN_EVIDENCE_REFERENCE")
    if prediction["decision"] != "RECOMMEND":
        return issues
    if case["safety_state"] != "REVIEW":
        issues.append("UNSAFE_SAFETY_STATE")
    if case["rebuildability"] != "PROVEN":
        issues.append("UNPROVEN_REBUILDABILITY")
    if case["offline_risk"] != "NONE":
        issues.append("OFFLINE_DEPENDENCY")
    if case["workload_impact"] != "LOW":
        issues.append("NONLOW_WORKLOAD_IMPACT")
    if prediction["cleanup_strategy"] not in case["acceptable_strategies"]:
        issues.append("STRATEGY_NOT_SUPPORTED_BY_GOLD")
    if case["native_cleanup_available"] and prediction["cleanup_strategy"] == "EXACT_PATH":
        issues.append("IGNORED_NATIVE_CLEANUP_METHOD")
    if (not case["native_cleanup_available"]
            and prediction["cleanup_strategy"] in ("NATIVE_PRUNE", "NATIVE_CLEAN")):
        issues.append("NATIVE_STRATEGY_UNAVAILABLE")
    return issues


def evaluate(cases: list[dict], predictions: list[dict]) -> dict:
    ids = [c["id"] for c in cases]
    for c in cases:
        validate_case(c)
    require(len(ids) == len(set(ids)), "duplicate case IDs")
    ps = [p["id"] for p in predictions]
    for p in predictions:
        validate_prediction(p)
    require(len(ps) == len(set(ps)), "duplicate prediction IDs")
    require(set(ids) == set(ps), "case IDs and prediction IDs must match exactly")
    mapping = {p["id"]: p for p in predictions}
    confusion = {g: {p: 0 for p in LABELS} for g in LABELS}
    issues: list[dict] = []
    accepted: list[str] = []
    recommended_mib = 0.0
    correct = 0
    critical_false_recommendations = 0
    recommendation_count = 0
    all_gate_violations = 0
    for c in cases:
        p = mapping[c["id"]]
        decision = p["decision"]
        expected = c["human_expected"]
        confusion[expected][decision] += 1
        correct += int(decision == expected)
        violations = preflight_violation(c, p)
        all_gate_violations += len(violations)
        if decision == "RECOMMEND":
            recommendation_count += 1
            if expected != "RECOMMEND":
                critical_false_recommendations += 1
            if not violations:
                accepted.append(c["id"])
                recommended_mib += c["measured_mib"]
        if violations or expected != decision:
            issues.append({
                "id": c["id"],
                "expected": expected,
                "predicted": decision,
                "gate_violations": violations,
                "misclassified": expected != decision,
            })
    tp = confusion["RECOMMEND"]["RECOMMEND"]
    fp = sum(confusion[g]["RECOMMEND"] for g in LABELS if g != "RECOMMEND")
    fn = sum(confusion["RECOMMEND"][p] for p in LABELS if p != "RECOMMEND")
    recall = tp / (tp + fn) if tp + fn else None
    # Zero unsafe recommendations alone is not enough: always-KEEP must fail.
    min_recall = 0.80
    return {
        "evaluation_only": True,
        "automated_deletion_supported": False,
        "dataset_size": len(cases),
        "three_state_accuracy": round(correct / len(cases), 4) if cases else None,
        "recommend_precision": round(tp / (tp + fp), 4) if tp + fp else None,
        "recommend_recall": round(recall, 4) if recall is not None else None,
        "minimum_required_recall": min_recall,
        "critical_false_recommendations": critical_false_recommendations,
        "gate_violations": all_gate_violations,
        "recommendation_count": recommendation_count,
        "conditionally_admissible_ids": accepted,
        "conditionally_admissible_measured_mib": round(recommended_mib, 1),
        "confusion_by_expected": confusion,
        "disagreements_and_gate_flags": issues,
        "release_quality_gate": (
            "PASS" if (critical_false_recommendations == 0
                       and all_gate_violations == 0
                       and recall is not None and recall >= min_recall)
            else "FAIL"
        ),
        "qualification": ("PASS on a small synthetic labeled fixture only; not proof of "
                          "AI semantic competence or a license to apply. Ground truth "
                          "labels require independent human audit."),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="optional private local evaluation report")
    args = parser.parse_args()
    try:
        raw_cases = load_json(args.cases)
        raw_predictions = load_json(args.predictions)
        cases = raw_cases.get("cases")
        predictions = raw_predictions.get("predictions")
        require(isinstance(cases, list) and bool(cases), "cases list missing/empty")
        require(isinstance(predictions, list), "predictions list missing")
        report = evaluate(cases, predictions)
    except (OSError, json.JSONDecodeError, InputError, KeyError) as exc:
        print(f"INVALID_INPUT: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    serialized = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output is not None:
        if args.output.exists():
            print("refuse overwrite of evaluation report", file=sys.stderr)
            return 2
        import os
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(serialized + "\n")
    print(serialized)
    return 0 if report["release_quality_gate"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())