## Task 2 – SCA + Container / IaC Security (Demo)

Mục tiêu: dùng **Trivy** để chạy tối thiểu **2/3** nội dung sau (bài này triển khai đủ **3/3**):

- **SCA (Dependency scanning)**: scan thư viện vulnerable từ lockfile.
- **Container image scanning**: scan Docker image sau khi build.
- **IaC scanning**: scan `Dockerfile` / `docker-compose.yml` (misconfiguration).

Repo `task2/` được chuẩn bị để bạn chạy demo nhanh và xuất **report JSON** phục vụ viết phân tích + remediation.

### 1) Yêu cầu môi trường

- Docker Desktop / Docker Engine
- Trivy (khuyến nghị) hoặc chạy Trivy qua container `aquasec/trivy`

### 2) Chạy demo nhanh (không cần Jenkins)

Tại thư mục workspace `d:\\workplace\\CV\\concung`:

```bash
# (A) IaC scan (Dockerfile + docker-compose)
trivy config --format json --output task2/reports/iac.trivy.json task2

# (B) SCA scan (dependency từ filesystem)
trivy fs --scanners vuln --format json --output task2/reports/sca.trivy.json task2

# (C) Build image + image scan
docker build -t task2-node-vuln:demo -f task2/app/Dockerfile task2/app
trivy image --format json --output task2/reports/image.trivy.json task2-node-vuln:demo
```

Nếu bạn chưa cài Trivy trên máy, có thể dùng container:

```bash
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock -v "%cd%":/work -w /work aquasec/trivy:latest config --format json --output task2/reports/iac.trivy.json task2
docker run --rm -v "%cd%":/work -w /work aquasec/trivy:latest fs --scanners vuln --format json --output task2/reports/sca.trivy.json task2
docker build -t task2-node-vuln:demo -f task2/app/Dockerfile task2/app
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock -v "%cd%":/work -w /work aquasec/trivy:latest image --format json --output task2/reports/image.trivy.json task2-node-vuln:demo
```

### 3) Chạy demo bằng Jenkins (tận dụng Task1)

- Dùng `task2/docker-compose.yml` để chạy Jenkins (reuse pattern từ `task1/docker-compose.yml`).
- Tạo Jenkins pipeline trỏ tới `task2/Jenkinsfile`.
- Artifacts được lưu trong `task2/reports/**`.

### 4) Output

- `task2/reports/`: các file JSON của Trivy (SCA, Image, IaC).
- `task2/docs/REPORT.md`: report + phân tích root cause + remediation (có sẵn khung).

