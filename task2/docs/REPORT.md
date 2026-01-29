## Task 2 – Report scan + remediation (mẫu)

### 1) Output scan

- `reports/iac.trivy.json`: Trivy config (IaC misconfiguration)
- `reports/sca.trivy.json`: Trivy fs (dependency vulnerabilities)
- `reports/image.trivy.json`: Trivy image (OS package + app deps trong image)

### 2) Phân biệt loại issue

- **Vulnerability do code**: lỗi do implementation trong source (SAST/DAST thường bắt).
- **Vulnerability do dependency**: CVE/advisory trong thư viện (SCA bắt).
- **Misconfiguration**: cấu hình insecure trong IaC (Trivy config bắt).

### 3) 1–2 issue High/Critical (điền từ kết quả scan)

#### Issue A – Misconfiguration: docker.sock mount cho Jenkins

- **Type**: Misconfiguration
- **Severity**: High/Critical (tuỳ rule scanner)
- **Root cause**: mount `/var/run/docker.sock` vào container Jenkins → container có thể điều khiển Docker daemon host.
- **Fix ở đâu**: **config/IaC + pipeline**
- **Remediation**:
  - Bỏ docker.sock mount nếu không bắt buộc.
  - Dùng Kaniko/BuildKit remote hoặc agent build riêng để tránh cấp quyền host.
- **Evidence**: `iac/docker-compose.insecure.yml`

#### Issue B – Dependency vulnerability: lodash version vulnerable

- **Type**: Vulnerability do dependency (SCA)
- **Severity**: High/Critical (tuỳ advisory)
- **Root cause**: pin `lodash@4.17.20` trong `app/package.json` (cũ, có advisory).
- **Fix ở đâu**: **dependency** (bump version) + lockfile
- **Remediation**:
  - Nâng lodash lên `>= 4.17.21` và regenerate lockfile.
  - Chạy lại scan để verify.
- **Evidence**: `app/package.json`

### 4) Hướng dẫn chạy demo

Chạy script PowerShell:

```powershell
pwsh -File task2/ci/run_local_demo.ps1
```

Hoặc chạy từng lệnh theo `task2/README.md`.

