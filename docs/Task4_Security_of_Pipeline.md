# Task 4 – Security of the Pipeline

Phân tích **bản thân pipeline** là một hệ thống cần được bảo vệ. Tài liệu liên hệ với pipeline đã build ở **Task 1/2** (Jenkins + docker-compose, Semgrep, Trivy, SonarQube) và nêu mitigation đã cài đặt cùng đề xuất bổ sung.

---

## 1. Yêu cầu: Ít nhất 3 rủi ro trong các nhóm

Các nhóm rủi ro được xem xét:

1. **Secrets leakage** (API key, token)  
2. **Compromised CI runner**  
3. **Malicious pipeline modification**  
4. **Over-permissioned service account**  
5. **Supply chain attack** (CI tool / action)  

Dưới đây phân tích **đủ 5** threat; yêu cầu tối thiểu là 3.

---

## 2. Yêu cầu phân tích: Threat → Impact → Mitigation

| # | Threat | Impact | Mitigation (đề xuất chung) |
|---|--------|--------|-----------------------------|
| 1 | **Secrets leakage (API key, token)** | Token SonarQube, credential Jenkins lộ → attacker truy cập Sonar/Jenkins, đọc code, sửa quality gate, thực hiện build độc hại. | Lưu token trong Jenkins Credentials hoặc file chỉ mount trong môi trường tin cậy; không hardcode trong Jenkinsfile; dùng `withCredentials`/env; scan secret trong repo (Semgrep rule, git-secrets) trước build. |
| 2 | **Compromised CI runner** | Runner/agent bị chiếm → chạy code tùy ý, đọc source, inject malicious build, exfil data. | Chạy Jenkins trong container cô lập; giảm surface (chỉ cài tool cần thiết); hạn chế network outbound; cập nhật image/base thường xuyên. |
| 3 | **Malicious pipeline modification** | Sửa Jenkinsfile/script trong repo → pipeline chạy lệnh nguy hiểm (exfil, crypto mining, backdoor). | Jenkinsfile trong SCM; chỉ merge sau code review; branch protection (không push trực tiếp lên main); audit log ai sửa, khi nào; dùng pipeline từ branch/tag tin cậy. |
| 4 | **Over-permissioned service account** | Jenkins container mount docker.sock → quyền điều khiển Docker host (build/pull/run image tùy ý, escape container). | Production: dùng Kaniko hoặc BuildKit remote thay docker.sock; service account Jenkins chỉ cần quyền tối thiểu (ví dụ chỉ push image lên registry). |
| 5 | **Supply chain attack (CI tool / action)** | Semgrep/Trivy/sonar-scanner hoặc base image bị compromise → pipeline tải và chạy mã độc. | Pin version từng tool; base image official (jenkins/jenkins:lts-jdk17); cập nhật định kỳ; mirror/internal registry nếu có thể; scan image Jenkins (Trivy) trước khi deploy. |

---

## 3. Liên hệ với pipeline Task 1/2 – Demo minh họa

Pipeline hiện tại (Task 1/2/3) gồm:

- **Môi trường**: `docker-compose.yml` – services Jenkins, SonarQube, init-sonar, app; volume mount `./:/workspace`; mount `/var/run/docker.sock` cho Jenkins.
- **Image Jenkins**: `jenkins/Dockerfile` – base `jenkins/jenkins:lts-jdk17`; cài Go, Python, Semgrep (trong pipeline), sonar-scanner, Trivy; pin version sonar-scanner và Trivy.
- **Pipeline config**: `Jenkinsfile` (một file duy nhất) – lưu trong Git; đọc token Sonar từ env hoặc file, không hardcode.
- **Repo**: `.gitignore` loại trừ `sonar_token.txt`, `reports/*.json`; không commit secret hay artifact.

*Demo minh họa:* Chạy `docker compose up -d jenkins sonarqube init-sonar` → tạo job với Script path `Jenkinsfile` → Build Now. Pipeline chạy trong container Jenkins; report trong `reports/`; token (nếu dùng) từ file hoặc Jenkins Credentials, không nằm trong repo.

---

## 4. Output – Bảng threat → mitigation đã cài đặt trong pipeline

| Threat | Mitigation đã cài đặt trong pipeline (repo hiện tại) |
|--------|------------------------------------------------------|
| **Secrets leakage** | (1) Sonar token không hardcode trong Jenkinsfile; đọc từ env hoặc file `sonar_token.txt` (Jenkinsfile: `SONAR_TOKEN` hoặc `cat sonar_token.txt`). (2) `.gitignore` có `sonar_token.txt` → không commit token. (3) Token chỉ tồn tại trên host/volume, không nằm trong SCM. |
| **Compromised CI runner** | (1) Jenkins chạy trong **container** (docker-compose), không trực tiếp trên host. (2) Image `jenkins/Dockerfile` chỉ cài Go, Python, Semgrep, sonar-scanner, Trivy – giảm surface. (3) Base image `jenkins/jenkins:lts-jdk17` (LTS), có thể cập nhật định kỳ. |
| **Malicious pipeline modification** | (1) **Jenkinsfile** nằm trong **SCM** (Git); thay đổi qua commit/merge. (2) Có thể bật branch protection và code review trước merge vào nhánh dùng cho pipeline. (3) Audit: Git log cho biết ai sửa Jenkinsfile, khi nào. |
| **Over-permissioned service account** | (1) **Demo:** mount docker.sock trong `docker-compose.yml` để pipeline build image (Trivy image scan). (2) **Đã ghi nhận trong tài liệu:** production nên dùng Kaniko hoặc BuildKit remote; không dùng docker.sock. (3) Trong repo không cấp thêm quyền host ngoài docker.sock. |
| **Supply chain attack** | (1) **Pin version** trong `jenkins/Dockerfile`: `SONAR_SCANNER_VERSION=5.0.1.3006`, `TRIVY_VERSION=0.52.0`. (2) Base image **official**: `jenkins/jenkins:lts-jdk17`. (3) Semgrep cài trong pipeline bằng `pip install semgrep` (có thể pin version trong Jenkinsfile nếu cần). (4) Có thể bổ sung: scan image Jenkins bằng Trivy trước khi deploy. |

---

## 5. Mô tả trong PDF

Trong báo cáo PDF (DevSecOps_CaseStudy_Report.pdf) nên gồm:

- **Đoạn mở đầu:** Pipeline (Jenkins + docker-compose, Task 1/2) là hệ thống cần bảo vệ; liệt kê 5 nhóm rủi ro (secrets, runner, pipeline modification, over-permission, supply chain).
- **Bảng Threat → Impact → Mitigation:** Như mục 2 (phân tích chung).
- **Bảng Threat → Mitigation đã cài đặt:** Như mục 4 – nêu rõ từng threat và biện pháp **đã áp dụng** trong repo (docker-compose, Jenkinsfile, .gitignore, jenkins/Dockerfile, quy ước không commit token).
- **Liên hệ demo:** Pipeline Task 1/2 chạy trong cùng môi trường; cách chạy: `docker compose up -d jenkins sonarqube init-sonar` → cấu hình job → Build Now; các mitigation trên áp dụng cho chính pipeline đó.

File tham chiếu: `docker-compose.yml`, `jenkins/Dockerfile`, `Jenkinsfile`, `.gitignore`, `README.md`.
