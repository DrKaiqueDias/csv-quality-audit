"""Streaming CSV quality audit. Reports counts, never raw field values."""
import argparse
import csv
import json
import math
import sys
from pathlib import Path


def audit(path: Path, required=(), numeric=()) -> dict:
    """O(rows * columns) time and O(columns) auxiliary memory."""
    required, numeric = set(required), set(numeric)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.reader(stream, strict=True)
        headers = next(reader, None)
        if not headers or any(not h.strip() for h in headers):
            raise ValueError("a non-empty header is required")
        if len(set(headers)) != len(headers):
            raise ValueError("duplicate column names")
        unknown = (required | numeric) - set(headers)
        if unknown:
            raise ValueError(f"unknown columns: {', '.join(sorted(unknown))}")
        missing = dict.fromkeys(headers, 0)
        invalid = dict.fromkeys(sorted(numeric), 0)
        rows = malformed = bad_rows = 0
        for row in reader:
            # csv.reader represents physically blank lines as []; ignore them.
            if not row:
                continue
            rows += 1
            if len(row) != len(headers):
                malformed += 1
                bad_rows += 1
                continue
            bad = False
            for name, value in zip(headers, row):
                if not value.strip():
                    missing[name] += 1
                    bad |= name in required
                elif name in numeric:
                    try:
                        if not math.isfinite(float(value)):
                            raise ValueError("not finite")
                    except ValueError:
                        invalid[name] += 1
                        bad = True
            bad_rows += int(bad)
    if rows == 0:
        raise ValueError("CSV contains no data rows")
    return {"rows": rows, "columns": headers, "malformed_rows": malformed,
            "missing_by_column": missing, "invalid_numeric_by_column": invalid,
            "failed_rows": bad_rows, "passed": bad_rows == 0}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--required", nargs="+", default=[])
    parser.add_argument("--numeric", nargs="+", default=[])
    args = parser.parse_args(argv)
    try:
        report = audit(args.input, args.required, args.numeric)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
