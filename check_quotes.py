"""Check verbatim evidence against independently extracted, located passages."""

import argparse
import json
import sys
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def check(passages, quotes):
    if not isinstance(passages, dict) or not all(isinstance(v, str) for v in passages.values()):
        raise ValueError("passages must map locators to text")
    if not isinstance(quotes, list) or not quotes:
        raise ValueError("expected a nonempty list of quote records")
    issues = []
    for row, record in enumerate(quotes, 1):
        if not isinstance(record, dict) or not all(
            isinstance(record.get(key), str) and record[key].strip()
            for key in ("claim_id", "locator", "quote")
        ):
            raise ValueError(f"invalid quote record at row {row}")
        locator = record["locator"]
        if locator not in passages:
            reason = "unknown locator"
        elif " ".join(record["quote"].split()) not in " ".join(passages[locator].split()):
            reason = "quote absent at locator"
        else:
            continue
        issues.append({"row": row, "claim_id": record["claim_id"], "locator": locator, "reason": reason})
    return {"checked": len(quotes), "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("passages")
    parser.add_argument("quotes")
    args = parser.parse_args()
    try:
        report = check(read_json(args.passages), read_json(args.quotes))
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(report))
    return int(bool(report["issues"]))


if __name__ == "__main__":
    sys.exit(main())
