## Task 1 – CI/CD Pipeline + SAST (Jenkins + Semgrep)

### Cấu trúc chính

- `docker-compose.yml`: chạy Jenkins và app demo.
- `jenkins/Dockerfile`: image Jenkins đã cài Python, pytest, Semgrep.
- `Jenkinsfile`: pipeline Jenkins (Build → Test → Quality & Security (SonarQube + Semgrep) → Deploy mock).
- `app/`: code Python demo (Flask + test + file vulnerable).
- `ci/`: Dockerfile, script pipeline local, script evaluate Semgrep report.
- `.semgrep.yml`: rule SAST cho Semgrep.
- `.semgrep/python.yml`: rule SAST cho Python (có thể thêm file cho Java/Node,...).
- `sonar-project.properties`: cấu hình SonarQube đa ngôn ngữ.
- `docs/Task1_CICD_SAST_Analysis.md`: phân tích, bạn export ra PDF nộp bài.

### Yêu cầu môi trường

- Docker Desktop / Docker Engine
- Docker Compose

### Khởi động Jenkins

```bash
docker compose build
docker compose up -d jenkins
```

Truy cập `http://localhost:8080` để cấu hình Jenkins.

### Cấu hình Jenkins Job từ GitHub

1. New Item → Pipeline.
2. Chọn "Pipeline script from SCM".
3. SCM = Git, nhập URL GitHub repo (public).
4. Branch: `main` (hoặc phù hợp repo).
5. Script path: `Jenkinsfile`.

Sau đó bấm **Build Now** để chạy pipeline.

### Chạy pipeline local (không qua Jenkins, tùy chọn)

```bash
docker build -t demo-ci -f ci/Dockerfile .
docker run --rm -v "%cd%":/workspace -w /workspace demo-ci bash ci/run_pipeline.sh
```

### Deploy mock app (chạy Flask)

```bash
docker compose up -d app
```

Truy cập `http://localhost:8000`.

