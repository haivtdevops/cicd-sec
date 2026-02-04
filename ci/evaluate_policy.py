#!/usr/bin/env python
"""
Task 3 – Policy Enforcement: aggregate findings và áp dụng policy (block/allow).
Scenario: 1 Critical, 2 High, 2 Medium → policy quyết định BLOCK/ALLOW.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def load_severity_counts(path: str) -> dict:
    """Đọc file JSON có thể là policy summary { CRITICAL: n, HIGH: n, ... } hoặc Trivy/Semgrep report."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Nếu đã là bảng severity (policy summary)
    if isinstance(data, dict) and any(k in data for k in ("CRITICAL", "HIGH", "MEDIUM")):
        return {k.upper(): int(v) for k, v in data.items() if k.upper() in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")}
    # Trivy: Results[].Vulnerabilities / Misconfigurations
    out = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    if isinstance(data, dict):
        for r in data.get("Results") or []:
            for v in (r.get("Vulnerabilities") or []) + (r.get("Misconfigurations") or []):
                s = (v.get("Severity") or "UNKNOWN").upper()
                out[s] = out.get(s, 0) + 1
    return out


def main():
    parser = argparse.ArgumentParser(description="Task 3 Policy: evaluate aggregated findings.")
    parser.add_argument("--input", help="Path to policy summary JSON (e.g. { CRITICAL: 1, HIGH: 2, MEDIUM: 2 })")
    parser.add_argument("--semgrep", help="Path to semgrep.json (optional, aggregate)")
    parser.add_argument("--trivy", help="Path to trivy.json (optional, aggregate)")
    parser.add_argument(
        "--policy",
        default="strict",
        choices=["strict", "task3_demo"],
        help="strict=block if Critical>=1 or High>=1; task3_demo=block if Critical>=1 or High>=2 or Medium>=2",
    )
    args = parser.parse_args()

    total = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}

    if args.input and Path(args.input).exists():
        total = load_severity_counts(args.input)
    if args.semgrep and Path(args.semgrep).exists():
        with open(args.semgrep, "r", encoding="utf-8") as f:
            d = json.load(f)
        for r in d.get("results") or []:
            s = (r.get("extra", {}).get("severity") or "UNKNOWN").upper()
            if s == "ERROR":
                total["CRITICAL"] = total.get("CRITICAL", 0) + 1
            elif s == "WARNING":
                total["HIGH"] = total.get("HIGH", 0) + 1
            else:
                total["MEDIUM"] = total.get("MEDIUM", 0) + 1
    if args.trivy and Path(args.trivy).exists():
        c = load_severity_counts(args.trivy)
        for k, v in c.items():
            total[k] = total.get(k, 0) + v

    print("=== Task 3 – Policy Enforcement Summary ===")
    for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
        if total.get(k, 0) > 0:
            print(f"  {k}: {total[k]}")

    c, h, m = total.get("CRITICAL", 0), total.get("HIGH", 0), total.get("MEDIUM", 0)

    if args.policy == "strict":
        block = c >= 1 or h >= 1
    else:
        # task3_demo: scenario 1 Critical, 2 High, 2 Medium → BLOCK
        block = c >= 1 or h >= 2 or m >= 2

    policy_strict = os.getenv("POLICY_STRICT", "true").lower() == "true"

    if block and policy_strict:
        print("Policy: BLOCK – pipeline FAILED (thresholds exceeded).")
        sys.exit(1)
    if block and not policy_strict:
        print("Policy: WARNING – thresholds exceeded but POLICY_STRICT=false, not blocking.")
        sys.exit(0)
    print("Policy: PASS – no blocking thresholds exceeded.")
    sys.exit(0)


if __name__ == "__main__":
    main()
