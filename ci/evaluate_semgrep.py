#!/usr/bin/env python
import argparse
import json
import os
import sys
from collections import Counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to Semgrep JSON report")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    findings = data.get("results", []) if isinstance(data, dict) else []
    severities = Counter()
    blocking = 0

    for r in findings:
        sev = (r.get("extra", {}).get("severity") or "UNKNOWN").upper()
        severities[sev] += 1
        # Chính sách: ERROR sẽ block pipeline, WARNING chỉ cảnh báo
        if sev == "ERROR":
            blocking += 1

    print("=== Semgrep Summary ===")
    for sev, count in severities.items():
        print(f"{sev}: {count}")
    print(f"Blocking findings (ERROR): {blocking}")

    # Nếu SAST_STRICT=true (mặc định), ERROR sẽ làm fail pipeline.
    # Nếu SAST_STRICT=false thì chỉ cảnh báo (không fail).
    strict = os.getenv("SAST_STRICT", "true").lower() == "true"

    if blocking > 0 and strict:
        print("Pipeline FAILED due to blocking (ERROR) SAST issues.")
        sys.exit(1)

    if blocking > 0 and not strict:
        print("WARNING: Có SAST findings severity ERROR, nhưng SAST_STRICT=false nên không block pipeline.")

    if blocking == 0:
        print("Pipeline PASSED: no blocking SAST issues.")

    sys.exit(0)


if __name__ == "__main__":
    main()

