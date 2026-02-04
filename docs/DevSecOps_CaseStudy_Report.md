# DevSecOps Case Study – Báo cáo tổng hợp (Task 1–5)

**Tên file nộp:** `DevSecOps_CaseStudy_Report.pdf` hoặc `DevSecOps_CaseStudy_Report.docx`  
**Tài liệu này dùng để:** (1) Hướng dẫn cách run, (2) Giải thích thiết kế, (3) Trình bày tư duy bảo mật. **Là tài liệu chấm điểm chính.**

*Export:* Mở file `.md` trong editor, export sang PDF (VS Code: Markdown PDF; hoặc Pandoc: `pandoc -o DevSecOps_CaseStudy_Report.pdf DevSecOps_CaseStudy_Report.md`). Để có file `.docx`: `pandoc -o DevSecOps_CaseStudy_Report.docx DevSecOps_CaseStudy_Report.md`, hoặc mở PDF/HTML trong Word rồi Save As .docx.

---

# PHẦN I. HƯỚNG DẪN CÁCH RUN

## 1.1. Yêu cầu môi trường

- Docker Desktop hoặc Docker Engine  
- Docker Compose  

## 1.2. Chạy toàn bộ môi trường (Jenkins + SonarQube + init Sonar)

Từ **thư mục gốc repository** (chứa `docker-compose.yml`):

```bash
docker compose build
docker compose up -d jenkins sonarqube init-sonar
```

- **Jenkins:** `http://localhost:8080`  
- **SonarQube:** `http://localhost:9000` (sau khi init-sonar chạy xong)  
- Lần đầu Jenkins: lấy mật khẩu admin bằng `docker logs jenkins-ci`.

## 1.3. Cấu hình Jenkins Job (Pipeline from SCM)

1. **New Item** → nhập tên job → chọn **Pipeline** → OK.  
2. **Pipeline:** chọn **Pipeline script from SCM**.  
3. **SCM:** Git; Repository URL = URL repo (public); Branch: `main`.  
4. **Script path:** **`Jenkinsfile`** — Một pipeline duy nhất cho Task 1 + 2 + 3 (cùng ứng dụng, cùng môi trường).  
5. **Build Now** để chạy pipeline. Report trong **Build Artifacts** → thư mục `reports/`.

## 1.4. Chạy demo Task 2 local (không cần Jenkins)

Từ thư mục gốc repo:

```powershell
pwsh -File ci/run_local_demo.ps1
```

## 1.5. Deploy ứng dụng (mock)

```bash
docker compose up -d app
```

Truy cập `http://localhost:8000`.

---

# PHẦN II. GIẢI THÍCH THIẾT KẾ

## 2.1. Tổng quan pipeline (Task 1, 2, 3)

- **Một repo, một pipeline, một môi trường:** Task 1, 2, 3 dùng **cùng một file Jenkinsfile**, cùng `docker-compose.yml`, cùng Jenkins image và cùng ứng dụng Go (`app/`).  
- **Ứng dụng:** Một app Go duy nhất (`app/`) cho Task 1, 2, 3 (Build, Test, SAST, IaC, SCA, Image Scan, Policy).

## 2.2. Task 1 – CI/CD + SAST

- **Stages:** Build (Go) → Test (Go) → Quality (SonarQube, tùy chọn) → **Security (Semgrep)** → Docker Build → Image Scan (Trivy).  
- **SAST:** Semgrep với rule có sẵn (`--config auto`) và rule bổ sung (`.semgrep/go.yml`). Report JSON `reports/semgrep.json` → script `ci/evaluate_semgrep.py` → pass/fail (ERROR = block khi `SAST_STRICT=true`).  
- **Vì sao chọn Semgrep:** Rule có sẵn (Registry), không bắt buộc viết rule; phù hợp CI/CD local; đa ngôn ngữ; xuất JSON để pipeline parse.  
- **SAST ở stage nào:** Stage **Security**, sau Build và Test, trước Docker Build/Image Scan — để code đã compile và test trước khi quét, Security làm cổng kiểm soát.  
- **Block vs warning:** ERROR + SAST_STRICT=true → block; WARNING/INFO → chỉ cảnh báo; SAST_STRICT=false → tạm không block.

## 2.3. Task 2 – SCA + Container / IaC Security

- **Ba loại scan:** (1) **IaC** — Trivy config (Dockerfile, docker-compose). (2) **SCA** — Trivy fs (dependency trong `app/`). (3) **Image** — Trivy image (sau Docker build).  
- **Phân biệt:** Vulnerability do **code** (SAST/DAST) → fix ở code. Vulnerability do **dependency** (SCA) → fix ở dependency/base image. **Misconfiguration** (Trivy config) → fix ở config/IaC và pipeline.  
- **Report:** `reports/iac.trivy.json`, `reports/sca.trivy.json`, `reports/trivy.json`; script `ci/evaluate_trivy.py` với `--mode config/fs/image`.  
- **Ví dụ issue:** (A) Misconfiguration: mount docker.sock — fix ở Config/IaC + pipeline (Kaniko/BuildKit). (B) Dependency CVE (Go) — fix ở code (go mod tidy, bump version).

## 2.4. Task 3 – Policy Enforcement & Security Governance

- **Scenario:** Pipeline phát hiện 1 Critical, 2 High, 2 Medium.  
- **Điều kiện block/allow:** Critical ≥ 1 hoặc High ≥ 2 hoặc Medium ≥ 2 (và không có exception) → **BLOCK**; ngược lại → ALLOW.  
- **Exception:** Có cho phép; **CISO hoặc Security Lead** approve (ticket + lý do + thời hạn); ghi nhận qua `POLICY_STRICT=false` hoặc whitelist.  
- **Dashboard (mock):** CISO/BOD — tổng hợp severity, trend, exception, SLA breach. Dev team — findings theo repo, link report, trạng thái pipeline.  
- **Quy trình:** Dev/owner fix code/dependency; DevOps/SRE fix config/IaC. SLA: Critical 7 ngày, High 14 ngày. Giao tiếp Product: Security gửi summary; release block đến khi pass policy hoặc exception được approve.  
- **Stage Policy:** Đọc aggregate từ Semgrep + Trivy hoặc mock `reports/policy_summary.json`; script `ci/evaluate_policy.py` — policy task3_demo → exit 1 nếu vượt ngưỡng.

## 2.5. Task 4 – Security of the Pipeline

- **Ý tưởng:** Bản thân pipeline (Jenkins, docker-compose, scripts) là hệ thống cần bảo vệ.  
- **Năm nhóm rủi ro (ít nhất 3):** (1) Secrets leakage, (2) Compromised CI runner, (3) Malicious pipeline modification, (4) Over-permissioned service account, (5) Supply chain attack.  
- **Thiết kế đã áp dụng:** Token không hardcode, `.gitignore` sonar_token.txt; Jenkins chạy trong container; Jenkinsfile trong SCM (Git); pin version sonar-scanner và Trivy trong `jenkins/Dockerfile`; base image official (jenkins/jenkins:lts-jdk17). Demo dùng docker.sock — tài liệu ghi rõ production dùng Kaniko/BuildKit.

## 2.6. Task 5 – Secure-by-Design & Threat Modeling (hệ thống khác Task 1–4)

- **Hệ thống:** Web App + API + Database + External Payment Service (không phải app Go trong repo).  
- **DFD:** User ↔ Web App ↔ API ↔ Database; External Payment ↔ API (callback). Luồng: HTTPS, callback, SQL/TLS.  
- **Ba threat:** T1 Broken Authentication/Session hijack (API/Auth); T2 SQL Injection/IDOR (API→DB); T3 Payment callback manipulation/Replay (API↔Payment).  
- **Mapping:** Threat → Design control (auth/JWT, prepared statement, signature/HMAC callback); Design control → CI/CD security check (SAST, SCA, secret scan, pipeline test).

---

# PHẦN III. TRÌNH BÀY TƯ DUY BẢO MẬT

## 3.1. Task 1 – SAST và policy trong pipeline

- **Tư duy:** Security là cổng, không phải bước tùy chọn. Build và Test trước để tránh lãng phí scan trên code chưa ổn định. ERROR (command injection, SQLi, secret, …) phải block; WARNING/INFO để backlog, tránh “nghẽn” khi mới tích hợp. Tool chọn Semgrep vì rule có sẵn và dễ tích hợp pass/fail từ JSON.

## 3.2. Task 2 – Phân biệt loại finding và fix đúng chỗ

- **Tư duy:** Vulnerability do **code** → sửa code (SAST/DAST). Do **dependency** → sửa dependency hoặc base image (SCA). **Misconfiguration** → sửa IaC và pipeline (Trivy config). Remediation phải chỉ rõ root cause và **fix ở đâu** (code, config, pipeline, base image) để tránh xử lý sai lớp.

## 3.3. Task 3 – Policy và governance

- **Tư duy:** Policy rõ ràng (Critical/High/Medium → block) để mọi người hiểu ngưỡng. Exception có kiểm soát (CISO/Security Lead approve) và có thời hạn. Dashboard cho CISO (trend, exception, SLA) và Dev (findings, link report) để vừa governance vừa hỗ trợ fix. Quy trình: ai fix, SLA, giao tiếp Product — release block cho đến khi pass hoặc exception được approve.

## 3.4. Task 4 – Pipeline cũng là hệ thống cần bảo vệ

- **Tư duy:** Pipeline chạy với quyền cao (build, deploy, secret). Secrets leakage, runner bị chiếm, pipeline bị sửa độc hại, over-permission (docker.sock), supply chain (tool/image) — mỗi threat cần mitigation rõ ràng. Đã áp dụng: không commit token, container cô lập, Jenkinsfile trong SCM, pin version tool, base LTS; production không dùng docker.sock (Kaniko/BuildKit).

## 3.5. Task 5 – Secure-by-Design và Threat Modeling

- **Tư duy:** Thiết kế kiểm soát (auth, prepared statement, signature callback) trước; sau đó ánh xạ từ design control sang CI/CD security check (SAST, SCA, secret scan, test) để đảm bảo kiểm soát đó được duy trì qua pipeline. Hệ thống Web App + API + DB + Payment — 3 threat (Auth, SQLi/IDOR, Payment callback) và mapping Threat → Design control → CI/CD check thể hiện tư duy này.

---

# PHỤ LỤC – BẢNG VÀ SƠ ĐỒ TÓM TẮT

## A. Task 1 – Issue block vs warning

| Loại | Severity | Hành vi |
|------|----------|---------|
| Block | ERROR (SAST_STRICT=true) | pipeline FAIL |
| Warning | WARNING, INFO | Ghi report, không fail |
| Tạm không block | ERROR + SAST_STRICT=false | In summary, không fail |

## B. Task 2 – Phân biệt loại issue và fix ở đâu

| Loại | Fix ở đâu (điển hình) |
|------|------------------------|
| Vulnerability do code | Code |
| Vulnerability do dependency | Code (dependency) hoặc base image |
| Misconfiguration | Config/IaC + pipeline |

## C. Task 3 – Logic policy (tóm tắt)

```
IF có_exception_approved THEN pipeline PASS (log warning)
ELSE IF (Critical≥1 OR High≥2 OR Medium≥2) THEN pipeline FAIL (exit 1)
ELSE pipeline PASS (exit 0)
```

## D. Task 4 – Threat → Mitigation đã cài đặt

| Threat | Đã cài đặt trong pipeline |
|--------|----------------------------|
| Secrets leakage | Token từ env/file; .gitignore sonar_token.txt; không hardcode trong Jenkinsfile. |
| Compromised runner | Jenkins trong container; image chỉ cài tool cần thiết; base LTS. |
| Malicious pipeline modification | Jenkinsfile trong SCM (Git); thay đổi qua commit/merge; Git audit. |
| Over-permissioned | Demo: docker.sock; tài liệu: production dùng Kaniko/BuildKit. |
| Supply chain | Pin version sonar-scanner, Trivy trong jenkins/Dockerfile; base official. |

## E. Task 5 – Bảng threat và mapping

**3 threat:** T1 Broken Auth/Session hijack (API/Auth); T2 SQLi/IDOR; T3 Payment callback/Replay.

**Threat → Design control:** T1: JWT/OAuth, rate limit, MFA, log auth. T2: Prepared statement, authorization check, validation. T3: Verify signature/HMAC, idempotency key, validate payload.

**Design control → CI/CD check:** Auth → SAST (secret, weak crypto), SCA (auth lib CVE). SQLi/IDOR → SAST (SQLi, path traversal), code review, DAST. Callback → SAST (hardcoded key, missing signature), secret scan, pipeline test (signed payload).

---

*Tài liệu tham chiếu chi tiết trong repo: `reports.md`, `docs/Task1_CICD_SAST_Analysis.md`, `docs/Task2_Trivy_Report.md`, `docs/Task3_Policy_Governance.md`, `docs/Task4_Security_of_Pipeline.md`, `docs/Task5_Threat_Modeling.md`.*
