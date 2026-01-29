#!/usr/bin/env python
import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to SonarQube quality gate JSON")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    status = (
        data.get("projectStatus", {}).get("status", "UNKNOWN").upper()
        if isinstance(data, dict)
        else "UNKNOWN"
    )

    print("=== SonarQube Quality Gate Summary ===")
    print(f"Quality Gate status: {status}")

    strict = os.getenv("SONAR_STRICT", "true").lower() == "true"

    if status == "ERROR" and strict:
        print("Pipeline FAILED due to SonarQube quality gate = ERROR.")
        sys.exit(1)

    if status == "ERROR" and not strict:
        print("WARNING: SonarQube quality gate = ERROR, but SONAR_STRICT=false so not blocking pipeline.")

    if status in ("OK", "SUCCESS"):
        print("SonarQube quality gate PASSED.")

    sys.exit(0)


if __name__ == "__main__":
    main()

