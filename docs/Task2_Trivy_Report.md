# Task 2 – SCA + Container / IaC Security

## 1. Report scan – Output và cấu trúc

### 1.1. Output scan (file report)

| File | Nguồn | Nội dung |
|------|--------|----------|
| `reports/iac.trivy.json` | `trivy config .` | Misconfiguration IaC (Dockerfile, docker-compose): rule ID, severity, file:line, message. |
| `reports/sca.trivy.json` | `trivy fs app` | Vulnerability dependency (SCA): CVE ID, package, version, severity, fixed version. |
| `reports/trivy.json` / `reports/image.trivy.json` | `trivy image demo-app:tag` | OS package + dependency trong image: Target, Vulnerabilities (CVE, Severity, PkgName, InstalledVersion, FixedVersion). |

### 1.2. Cách đọc report (Trivy JSON)

- **Vulnerabilities**: mảng `Results[].Vulnerabilities[]` – mỗi phần tử có `VulnerabilityID` (CVE), `Severity`, `PkgName`, `InstalledVersion`, `FixedVersion`, `Title`, `Description`.
- **Misconfigurations**: mảng `Results[].Misconfigurations[]` – mỗi phần tử có `ID`, `Severity`, `Title`, `Message`, `Resolution`, `PrimaryURL`.
- **Summary**: script `ci/evaluate_trivy.py` đọc file JSON, đếm CRITICAL/HIGH/MEDIUM/LOW; nếu `TRIVY_STRICT=true` và có CRITICAL hoặc HIGH thì pipeline fail (exit 1).
- **Xem report sau khi chạy Jenkins**: Build → Build Artifacts → mở file trong `reports/`.

---

## 2. Yêu cầu phân tích: Phân biệt loại issue

| Loại | Mô tả | Công cụ thường dùng | Fix ở đâu (điển hình) |
|------|--------|---------------------|------------------------|
| **Vulnerability do code** | Lỗi do implementation trong source (logic, xử lý input, auth, v.v.). | SAST (Semgrep, CodeQL), DAST | **Code** – sửa source, pattern, validation. |
| **Vulnerability do dependency** | CVE / advisory trong thư viện (go.mod, package.json, …). | SCA – Trivy fs, Dependency-Check, npm audit | **Code** (cập nhật dependency, lockfile) hoặc **base image** (nếu CVE ở layer OS). |
| **Misconfiguration** | Cấu hình không an toàn trong IaC (Dockerfile, docker-compose, Terraform, …). | Trivy config, Checkov, tfsec | **Config / IaC** – sửa Dockerfile, compose; **pipeline** nếu cần bắt buộc bước scan. |

---

## 3. 1–2 issue High/Critical: Root cause và Fix ở đâu

### Issue A – Misconfiguration: mount docker.sock cho Jenkins

| Yêu cầu | Nội dung |
|---------|----------|
| **Loại** | Misconfiguration |
| **Severity** | High/Critical (tùy rule scanner) |
| **Root cause là gì?** | Mount `/var/run/docker.sock` vào container Jenkins → process trong container có quyền gọi Docker daemon của host (build/run/pull image tùy ý). Rủi ro: chiếm quyền host, escape container. |
| **Fix ở đâu?** | **Config/IaC** + **pipeline**. Sửa file docker-compose (bỏ volume docker.sock hoặc dùng volume read-only nếu bắt buộc); trong pipeline dùng Kaniko hoặc BuildKit remote thay vì docker-in-docker. |
| **Remediation** | (1) Bỏ mount docker.sock nếu không bắt buộc. (2) Production: dùng Kaniko/BuildKit remote hoặc agent build riêng. (3) Pipeline: bắt buộc stage IaC scan (Trivy config) để phát hiện tương tự. |
| **Evidence** | `iac/docker-compose.insecure.yml` |

### Issue B – Vulnerability do dependency: thư viện Go có CVE (SCA)

| Yêu cầu | Nội dung |
|---------|----------|
| **Loại** | Vulnerability do dependency (SCA) |
| **Severity** | High/Critical (tùy advisory) |
| **Root cause là gì?** | Dependency khai báo trong `app/go.mod` / `app/go.sum` có bản cũ chứa CVE đã công bố. Trivy fs scan thư mục `app/` đọc go.sum và so khớp với database CVE. |
| **Fix ở đâu?** | **Code** (dependency): cập nhật version module Go đã fix CVE; chạy `go mod tidy`; không phải config hay base image nếu CVE nằm ở thư viện ứng dụng. Nếu CVE ở package trong base image thì fix ở **base image** (đổi image hoặc patch). |
| **Remediation** | (1) `go get -u module/path` hoặc sửa version trong go.mod. (2) `go mod tidy`. (3) Chạy lại `trivy fs app` để xác nhận. (4) Pipeline: giữ stage SCA (Trivy fs) và block khi CRITICAL/HIGH (TRIVY_STRICT). |
| **Evidence** | `app/go.mod`, `app/go.sum` |

---

## 4. Đề xuất remediation (tổng hợp)

| Loại finding | Đề xuất remediation |
|--------------|---------------------|
| **IaC (Misconfiguration)** | (1) Sửa Dockerfile/compose: bỏ hoặc hạn chế docker.sock; chạy app bằng user không root khi có thể. (2) Pipeline: thêm stage **Trivy config** (IaC scan), block khi CRITICAL/HIGH. (3) Production: dùng Kaniko hoặc BuildKit remote thay docker-in-docker. (4) Review định kỳ file IaC khi thay đổi. |
| **SCA (Dependency)** | (1) Cập nhật dependency lên bản đã fix CVE (`go get -u`, `go mod tidy`; npm audit fix; pip install -U). (2) Pin version trong lockfile (go.sum, package-lock.json). (3) Pipeline: stage **Trivy fs** (hoặc SCA tương đương), block khi CRITICAL/HIGH (`TRIVY_STRICT=true`). (4) Theo dõi advisory (GitHub Dependabot, Renovate) và xử lý theo SLA. |
| **Image (Container)** | (1) Dùng **base image** nhỏ, official, có cập nhật bảo mật (alpine, distroless). (2) Quét image trước khi push registry; block deploy nếu CRITICAL/HIGH. (3) Pipeline: stage **Trivy image** sau Docker build; gắn với policy (ví dụ không deploy image có CRITICAL). (4) Patch/rebuild image khi base image có bản mới fix CVE. |

**Thứ tự ưu tiên:** (1) Fix ngay CRITICAL. (2) Fix HIGH trong sprint/SLA. (3) Misconfiguration IaC và dependency MEDIUM/LOW đưa vào backlog, xử lý theo roadmap.

---

## 5. Hướng dẫn chạy demo

### 5.1. Chạy bằng Jenkins (Pipeline Task 2)

1. Khởi động môi trường (từ thư mục gốc repo):

   ```bash
   docker compose build
   docker compose up -d jenkins sonarqube init-sonar
   ```

2. Truy cập Jenkins: `http://localhost:8080`.  
3. New Item → Pipeline → Pipeline script from SCM → Git, URL repo, branch `main`.  
4. **Script path:** `Jenkinsfile` (cùng pipeline với Task 1 và Task 3).  
5. **Build Now.** Pipeline chạy: IaC Scan (Trivy config) → SCA (Trivy fs) → Docker Build → Image Scan (Trivy image). Report lưu trong `reports/` và build artifacts.

### 5.2. Chạy local (không cần Jenkins)

Từ **thư mục gốc repo**:

```powershell
pwsh -File ci/run_local_demo.ps1
```

Script thực hiện: Trivy config → Trivy fs (app) → Docker build app → Trivy image; gọi `ci/evaluate_trivy.py` với `--mode config/fs/image`.

### 5.3. Chạy từng lệnh thủ công

```bash
# (A) IaC scan
trivy config --format json --output reports/iac.trivy.json .
python ci/evaluate_trivy.py --input reports/iac.trivy.json --mode config

# (B) SCA (dependency)
trivy fs --scanners vuln --format json --output reports/sca.trivy.json app
python ci/evaluate_trivy.py --input reports/sca.trivy.json --mode fs

# (C) Build image + image scan
docker build -f app/Dockerfile -t demo-app:demo app
trivy image --format json --output reports/trivy.json demo-app:demo
python ci/evaluate_trivy.py --input reports/trivy.json --mode image
```

Toàn bộ dùng **cùng ứng dụng Go** (thư mục `app/`).
