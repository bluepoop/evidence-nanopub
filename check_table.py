"""Verify one decimal-valued comparison against a UTF-8 CSV table."""

import argparse
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def compare(table, claim):
    if not isinstance(claim, dict) or not all(isinstance(claim.get(k), str) and claim[k].strip()
            for k in ("metric", "left", "right", "left_value", "right_value", "relation")):
        raise ValueError("expected string fields metric, left, right, left_value, right_value and relation")
    if claim["left"] == claim["right"] or claim["relation"] not in ("gt", "lt", "eq"):
        raise ValueError("use two distinct row labels and gt, lt or eq")
    headings = next(table, [])
    if len(set(headings)) != len(headings) or claim["metric"] not in headings[1:]:
        raise ValueError("missing or ambiguous metric header")
    column = headings.index(claim["metric"])
    observed = {}
    for row in table:
        if not row:
            continue
        if len(row) != len(headings):
            raise ValueError(f"malformed CSV row ending at line {table.line_num}")
        label = row[0]
        if label in (claim["left"], claim["right"]):
            if label in observed:
                raise ValueError(f"ambiguous row label: {label}")
            observed[label] = row[column]
    issues = []
    values = []
    for side in ("left", "right"):
        label = claim[side]
        if label not in observed:
            raise ValueError(f"missing row: {label}")
        actual = Decimal(observed[label])
        reported = Decimal(claim[side + "_value"])
        if not actual.is_finite() or not reported.is_finite():
            raise ValueError("expected finite decimal values")
        if actual != reported:
            issues.append(f"{label}: observed {actual}, claimed {reported}")
        values.append(actual)
    left, right = values
    relation = "gt" if left > right else "lt" if left < right else "eq"
    if relation != claim["relation"]:
        issues.append(f"observed relation {relation}, claimed {claim['relation']}")
    return {"metric": claim["metric"], "observed": observed, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path)
    parser.add_argument("claim", type=Path)
    args = parser.parse_args()
    try:
        claim = json.loads(args.claim.read_text(encoding="utf-8-sig"))
        with args.table.open(encoding="utf-8-sig", newline="") as stream:
            report = compare(csv.reader(stream, strict=True), claim)
    except (OSError, ValueError, csv.Error, InvalidOperation) as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(json.dumps(report))
    return int(bool(report["issues"]))


if __name__ == "__main__":
    raise SystemExit(main())
