# Checklist – Đối chiếu 5 yêu cầu (Task 1–5)

**Pipeline tổng hợp:** Script path **`Jenkinsfile`** (một file duy nhất) chạy flow đầy đủ Task 1 + 2 + 3.

## Yêu cầu chung (BẮT BUỘC)

| Yêu cầu | Trạng thái | Ghi chú |
|---------|------------|---------|
| 01 repo hoàn chỉnh (GitHub public) | ✅ | Repo gốc concung |
| docker-compose.yml: chạy CI/CD local + security tools | ✅ | Jenkins, SonarQube, init-sonar, app (Go) |
| Giải thích giả lập (nếu có) – giới hạn | ✅ | README + docs: Sonar/Trivy optional khi thiếu CLI/token |
| 01 file PDF duy nhất (3–5 trang): hướng dẫn chạy, thiết kế, tư duy bảo mật | ✅ | Export `docs/DevSecOps_CaseStudy_Report.md` → **DevSecOps_CaseStudy_Report.pdf** |
| Cùng 1 repo, cùng môi trường (Docker), tối thiểu 03 task | ✅ | 1 repo; docker-compose; Task 1, 2, 3, 4, 5 đều có |

---

## Task 1 – CI/CD Pipeline + SAST

| Yêu cầu | Trạng thái | File / Ghi chú |
|---------|------------|-----------------|
| Pipeline: Build, Test, Security, (Optional) Deploy mock | ✅ | Jenkinsfile: Build (Go), Test (Go), Quality (Sonar), Security (Semgrep), Docker Build, Image Scan (Trivy) |
| Tích hợp SAST (Semgrep/SonarQube/CodeQL hoặc giả lập) | ✅ | Semgrep (SAST chính) + SonarQube (Quality optional) |
| Report JSON/SARIF/Markdown, pipeline parse pass/fail | ✅ | `reports/semgrep.json`, `ci/evaluate_semgrep.py` → exit 0/1 |
| PDF: Vì sao chọn SAST? Chạy SAST ở stage nào? Issue block/warning? Hướng dẫn demo | ✅ | `reports.md`, `docs/Task1_CICD_SAST_Analysis.md` |
| Output: Pipeline config, SAST report mẫu, mô tả trong PDF | ✅ | Jenkinsfile; bản mẫu `docs/sample_semgrep_report.json`; mô tả trong docs |

---

## Task 2 – SCA + Container / IaC Security

| Yêu cầu | Trạng thái | File / Ghi chú |
|---------|------------|-----------------|
| Ít nhất 2 trong 3: SCA, Container Image Scan, IaC Scan | ✅ | Cả 3: Trivy config (IaC), Trivy fs (SCA), Trivy image |
| Phân biệt: Vulnerability do code / do dependency / Misconfiguration | ✅ | `docs/Task2_Trivy_Report.md` mục 2 |
| 1–2 issue High/Critical: Root cause? Fix ở đâu? | ✅ | Issue A (Misconfig: docker.sock), Issue B (Dependency: Go CVE); root cause + remediation |
| Output: Report scan, remediation, mô tả trong PDF | ✅ | reports/*.json, `docs/Task2_Trivy_Report.md`, Jenkinsfile |

---

## Task 3 – Policy Enforcement & Security Governance

| Yêu cầu | Trạng thái | File / Ghi chú |
|---------|------------|-----------------|
| Scenario: 1 Critical, 2 High, 2 Medium | ✅ | Jenkinsfile stage Policy dùng mock `{"CRITICAL":1,"HIGH":2,"MEDIUM":2}` → BLOCK |
| Thiết kế policy: điều kiện block/allow, exception (ai approve?) | ✅ | `docs/Task3_Policy_Governance.md`: bảng block/allow, Exception (CISO approve) |
| Mô tả dashboard: CISO/BOD nhìn gì? Dev team nhìn gì? | ✅ | Bảng Dashboard / reporting trong Task3 doc |
| Quy trình: Ai fix? SLA Critical/High? Giao tiếp Product? | ✅ | Bảng Quy trình xử lý trong Task3 doc |
| Output: Sơ đồ logic policy, mô tả dashboard, hướng dẫn chạy (step-by-step) trong PDF | ✅ | Logic (text), bảng dashboard, hướng dẫn demo; Jenkinsfile, ci/evaluate_policy.py |

---

## Task 4 – Security of the Pipeline

| Yêu cầu | Trạng thái | File / Ghi chú |
|---------|------------|-----------------|
| Ít nhất 3 rủi ro: secrets, runner, pipeline modification, over-permission, supply chain | ✅ | 5 rủi ro trong bảng Threat → Impact → Mitigation |
| Bảng: Threat → Impact → Mitigation | ✅ | `docs/Task4_Security_of_Pipeline.md` |
| Liên hệ với pipeline Task 1/2 | ✅ | Mô tả Jenkins + docker-compose, đã áp dụng trong repo |
| Output: Bảng threat→mitigation, mô tả trong PDF | ✅ | Task4 doc + DevSecOps_CaseStudy_Report |

---

## Task 5 – Secure-by-Design & Threat Modeling

| Yêu cầu | Trạng thái | File / Ghi chú |
|---------|------------|-----------------|
| System **khác** Task 1–4: Web App + API + Database + External Payment | ✅ | Task5 doc: Web App, API, DB, External Payment Service |
| DFD (Data Flow Diagram) | ✅ | Sơ đồ ASCII trong `docs/Task5_Threat_Modeling.md` |
| 3 mối đe dọa chính, ít nhất 1 liên quan API/auth | ✅ | T1 Broken Auth (API/Auth), T2 SQLi/IDOR, T3 Payment callback |
| Mapping: Threat → Design control; Design control → CI/CD security check | ✅ | Bảng 3 cột trong Task5 doc |
| Output: DFD, bảng threat, mô tả trong PDF | ✅ | Task5 doc + DevSecOps_CaseStudy_Report |

---

## Tóm tắt

- **Task 1, 2, 3**: Một pipeline duy nhất (**Jenkinsfile**) chạy trong **cùng môi trường** (docker-compose).
- **Task 4, 5**: Chỉ tài liệu (không cần Jenkinsfile riêng); nội dung trong `docs/` và trong PDF.
- **Ứng dụng**: **Chỉ một app Go** (`app/`) – dùng cho Task 1, 2, 3 (Build/Test/SAST, SCA/IaC/Image scan, Policy). Đáp ứng “cùng một ứng dụng”.
- **PDF nộp bài**: Export `docs/DevSecOps_CaseStudy_Report.md` sang **DevSecOps_CaseStudy_Report.pdf** (3–5 trang).
