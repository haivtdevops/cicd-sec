#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="${PROJECT_ROOT}/reports"
mkdir -p "${REPORT_DIR}"

echo "===== CI PIPELINE START ====="

################################
# Stage 1: Build
################################
echo ">>> [BUILD] Install app dependencies"
cd "${PROJECT_ROOT}/app"
pip install --no-cache-dir -r requirements.txt

echo ">>> [BUILD] Static check (optional: byte-compile)"
python -m py_compile src/*.py

################################
# Stage 2: Test
################################
echo ">>> [TEST] Run unit tests"
pytest -q

################################
# Stage 3: Security (SAST)
################################
echo ">>> [SECURITY] Run Semgrep SAST scan"
cd "${PROJECT_ROOT}"

semgrep \
  --config .semgrep.yml \
  --json \
  --output "${REPORT_DIR}/semgrep.json" \
  --error || echo "Semgrep finished with findings – will be evaluated."

echo ">>> [SECURITY] Evaluate Semgrep results (block only high severity)"
python ci/evaluate_semgrep.py \
  --input "${REPORT_DIR}/semgrep.json"

################################
# Stage 4: Deploy mock (optional)
################################
echo ">>> [DEPLOY] (mock) Starting app container via docker-compose (run manually)"
echo "You can run: docker compose up -d app"

echo "===== CI PIPELINE SUCCESS ====="

