# DevSecOps Case Study – CI/CD Pipeline & Security

Repository thực hiện **Task 1** (CI/CD + SAST), **Task 2** (SCA + IaC + Container Security), **Task 3** (Policy Enforcement) trên **cùng một ứng dụng, một CI/CD pipeline, một môi trường** (Docker/docker-compose). Task 4 và Task 5 là tài liệu phân tích. **Chỉ một file Jenkinsfile** cho tất cả task (trừ Task 5).

---

## Cấu trúc repo

| Thành phần | Mô tả |
|------------|--------|
| `docker-compose.yml` | Chạy Jenkins, SonarQube, init-sonar và ứng dụng Go. |
| `jenkins/Dockerfile` | Image Jenkins (Go, Python, Semgrep, sonar-scanner, Trivy). |
| **`Jenkinsfile`** | **Một pipeline duy nhất** cho Task 1 + 2 + 3: Build → Test → Quality → Security (Semgrep) → IaC Scan → SCA → Docker Build → Image Scan → Policy. Cùng ứng dụng Go (`app/`), cùng môi trường (docker-compose). |
| `app/` | Ứng dụng Go duy nhất; dùng cho Task 1, 2, 3. |
| `iac/` | File docker-compose mẫu (insecure) cho demo IaC scan (Task 2). |
| `ci/` | Script đánh giá report: Semgrep, SonarQube, Trivy, Policy; và `run_local_demo.ps1` (demo Task 2 local). |
| `.semgrep/go.yml` | Rule Semgrep bổ sung (command-injection). Kết hợp với `--config auto`; khi chạy Task 1 có thể fail stage Security và sinh report mẫu. |
| `docs/sample_semgrep_report.json` | Bản mẫu SAST report (format JSON, 1 finding ERROR). |
| **`docs/DevSecOps_CaseStudy_Report.md`** | **Báo cáo tổng hợp Task 1–5** — hướng dẫn run, thiết kế, tư duy bảo mật. **Tài liệu chấm điểm chính.** Export sang PDF hoặc .docx (từ thư mục repo: `pandoc docs/DevSecOps_CaseStudy_Report.md -o DevSecOps_CaseStudy_Report.pdf` hoặc `-o DevSecOps_CaseStudy_Report.docx`). |
| `docs/*.md` | Tài liệu phân tích từng task (Task1–Task5). |

---

## Yêu cầu môi trường

- Docker Desktop hoặc Docker Engine  
- Docker Compose  

---

## Khởi động

```bash
docker compose build
docker compose up -d jenkins sonarqube init-sonar
```

Truy cập **Jenkins**: `http://localhost:8080`  
Truy cập **SonarQube**: `http://localhost:9000` (sau khi init-sonar chạy xong)

---

## Cấu hình Jenkins Job (Pipeline from SCM)

1. **New Item** → Pipeline.  
2. **Pipeline script from SCM** → SCM: Git, URL repo (public), branch `main`.  
3. **Script path**: **`Jenkinsfile`** (mặc định — một pipeline cho Task 1, 2, 3).  
4. **Build Now** để chạy pipeline.

---

## Chạy demo Task 2 local (không dùng Jenkins)

Từ **thư mục gốc repo**:

```powershell
pwsh -File ci/run_local_demo.ps1
```

Chi tiết từng bước: `docs/Task2_Trivy_Report.md`.

---

## Deploy ứng dụng (mock)

```bash
docker compose up -d app
```

Truy cập `http://localhost:8000`.
