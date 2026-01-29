$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$reports = Join-Path $root "reports"

New-Item -ItemType Directory -Force $reports | Out-Null

Write-Host "=== Task2 demo: IaC scan ==="
trivy config --format json --output (Join-Path $reports "iac.trivy.json") $root
python (Join-Path $root "ci/evaluate_trivy.py") --input (Join-Path $reports "iac.trivy.json") --mode config

Write-Host "=== Task2 demo: SCA (fs) scan ==="
trivy fs --scanners vuln --format json --output (Join-Path $reports "sca.trivy.json") $root
python (Join-Path $root "ci/evaluate_trivy.py") --input (Join-Path $reports "sca.trivy.json") --mode fs

Write-Host "=== Task2 demo: build image + image scan ==="
docker build -t task2-node-vuln:demo -f (Join-Path $root "app/Dockerfile") (Join-Path $root "app")
trivy image --format json --output (Join-Path $reports "image.trivy.json") task2-node-vuln:demo
python (Join-Path $root "ci/evaluate_trivy.py") --input (Join-Path $reports "image.trivy.json") --mode image

Write-Host "=== DONE. Reports in task2/reports/ ==="

