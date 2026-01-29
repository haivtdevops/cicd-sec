#!/usr/bin/env python
import argparse
import json
import os
import sys
from collections import Counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to Trivy JSON report")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Trivy JSON structure: có thể là array hoặc object với Results
    results = []
    if isinstance(data, list):
        results = data
    elif isinstance(data, dict):
        results = data.get("Results", [])

    severities = Counter()
    blocking = 0

    for result in results:
        vulnerabilities = result.get("Vulnerabilities", [])
        for vuln in vulnerabilities:
            sev = (vuln.get("Severity") or "UNKNOWN").upper()
            severities[sev] += 1
            # CRITICAL và HIGH sẽ block pipeline
            if sev in ("CRITICAL", "HIGH"):
                blocking += 1

    print("=== Trivy Image Scan Summary ===")
    for sev, count in severities.items():
        print(f"{sev}: {count}")
    print(f"Blocking findings (CRITICAL/HIGH): {blocking}")

    strict = os.getenv("TRIVY_STRICT", "true").lower() == "true"

    if blocking > 0 and strict:
        print("Pipeline FAILED due to blocking (CRITICAL/HIGH) vulnerabilities in image.")
        sys.exit(1)

    if blocking > 0 and not strict:
        print("WARNING: Có vulnerabilities CRITICAL/HIGH, nhưng TRIVY_STRICT=false nên không block pipeline.")

    if blocking == 0:
        print("Pipeline PASSED: no blocking vulnerabilities in image.")

    sys.exit(0)


if __name__ == "__main__":
    main()
