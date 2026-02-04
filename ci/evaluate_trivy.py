#!/usr/bin/env python
import argparse
import json
import os
import sys
from collections import Counter


def _iter_results(data):
    if isinstance(data, list):
        for item in data:
            yield item
        return
    if isinstance(data, dict):
        for r in data.get("Results", []) or []:
            yield r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to Trivy JSON report")
    parser.add_argument(
        "--mode",
        choices=["auto", "image", "fs", "config"],
        default="auto",
        help="How to interpret the report. 'auto' counts both vulns + misconfigs if present.",
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    sev = Counter()
    blocking = 0

    for result in _iter_results(data):
        if args.mode in ("auto", "image", "fs"):
            for v in result.get("Vulnerabilities", []) or []:
                s = (v.get("Severity") or "UNKNOWN").upper()
                sev[s] += 1
                if s in ("CRITICAL", "HIGH"):
                    blocking += 1

        if args.mode in ("auto", "config"):
            for m in result.get("Misconfigurations", []) or []:
                s = (m.get("Severity") or "UNKNOWN").upper()
                sev[s] += 1
                if s in ("CRITICAL", "HIGH"):
                    blocking += 1

    strict = os.getenv("TRIVY_STRICT", "true").lower() == "true"

    print("=== Trivy Summary ===")
    for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
        if k in sev:
            print(f"{k}: {sev[k]}")
    # Include any other keys Trivy might emit
    for k, v in sev.items():
        if k not in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"):
            print(f"{k}: {v}")
    print(f"Blocking findings (CRITICAL/HIGH): {blocking}")

    if blocking > 0 and strict:
        print("Pipeline FAILED due to blocking (CRITICAL/HIGH) findings.")
        sys.exit(1)

    if blocking > 0 and not strict:
        print("WARNING: Có findings CRITICAL/HIGH, nhưng TRIVY_STRICT=false nên không block pipeline.")

    if blocking == 0:
        print("Pipeline PASSED: no blocking findings.")

    sys.exit(0)


if __name__ == "__main__":
    main()
