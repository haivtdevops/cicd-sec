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
docker compose build --no-cache jenkins
docker compose up -d jenkins sonarqube init-sonar
```

Truy cập **Jenkins**: `http://localhost:8080`  
Truy cập **SonarQube**: `http://localhost:9000` (sau khi init-sonar chạy xong)

---

## Đăng nhập (credentials mặc định)

| Dịch vụ    | User   | Mật khẩu / Ghi chú |
|------------|--------|--------------------|
| **Jenkins** | `admin` | Lần đầu: lấy **initial admin password** trong container: `docker exec jenkins-ci cat /var/jenkins_home/secrets/initialAdminPassword` (hoặc xem trong `docker logs jenkins-ci`). Sau khi setup wizard xong, dùng tài khoản bạn tạo. |
| **SonarQube** | `admin` | **`admin`** / **`admin`**. Lần đầu đăng nhập SonarQube sẽ yêu cầu đổi mật khẩu. |

---

## Cấu hình Jenkins Job (Pipeline from SCM)

1. **New Item** → Pipeline.  
2. **Pipeline script from SCM** → SCM: Git, URL repo (public), branch `main`.  
3. **Script path**: **`Jenkinsfile`** (mặc định — một pipeline cho Task 1, 2, 3).  
4. **Build Now** để chạy pipeline.

**Nếu build "SUCCESS" nhưng không có stage nào chạy:**  
1. **Executor:** **Manage Jenkins** → **Nodes** → **Built-In Node** → **Configure** → **Number of executors** = **1** trở lên → **Save**.  
2. **Restrict where this project can be run:** Job → **Configure** → mục này **để trống** (hoặc nhập `master` nếu node của bạn có label đó).  
3. **Label node:** **Manage Jenkins** → **Nodes** → **Built-In Node** → **Configure** → **Labels** phải có **`master`** (Jenkinsfile dùng `agent { label 'master' }`). Nếu node chỉ có label khác (vd. `built-in`), sửa trong Jenkinsfile thành `agent { label 'built-in' }` hoặc `agent any`.  
4. **Custom workspace (tùy chọn):** Job → **Configure** → **Advanced** → **Use custom workspace** = **`/workspace`** để pipeline dùng đúng thư mục mount từ docker-compose.

**Lỗi khác:** Line ending: Jenkinsfile cần LF (repo có `.gitattributes`). Script path: `Jenkinsfile`, branch đúng (vd. `main`).

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
