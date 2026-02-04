## 1. Vì sao chọn SAST tool Semgrep?

- **Rule có sẵn, không cần viết code**: Semgrep Registry cung cấp hàng nghìn rule. Chạy `semgrep scan --config auto` sử dụng rule tự động theo ngôn ngữ; không bắt buộc viết rule (có thể bổ sung `.semgrep/*.yml` nếu cần rule riêng).
- **Dễ cài đặt và chạy local**: Semgrep nhẹ, chỉ cần Python/pip hoặc Docker, phù hợp CI/CD local với docker-compose.
- **Rule tùy chỉnh, đa ngôn ngữ**: Hỗ trợ Python, JS, Java, Go; có thể viết rule theo pattern (ví dụ phát hiện `os.system` hoặc so sánh không an toàn).
- **Tích hợp CI/CD đơn giản**: Một lệnh CLI (`semgrep --config ... --json --output ...`) sinh report JSON để pipeline parse pass/fail.
- **Mã nguồn mở, cộng đồng lớn**: Nhiều ruleset theo OWASP và best practice, dễ mở rộng.

## 2. Chạy SAST ở stage nào? Vì sao?

- SAST được chạy ở stage **Security**, sau các stage:
  - **Build**: cài đặt dependency, đảm bảo project build được.
  - **Test**: chạy unit test để code ở trạng thái ổn định hơn.
- Lý do:
  - Nếu build hoặc unit test đã fail, thường developer phải sửa code, nên chưa cần tốn thời gian chạy SAST.
  - Khi code đã build & test pass, stage Security đóng vai trò **cổng kiểm soát bảo mật** trước khi merge/deploy.
  - Ở môi trường thực tế có thể:
    - Chạy quick SAST sớm (ví dụ trên mỗi commit) để feedback nhanh.
    - Chạy full SAST ở stage gần cuối hoặc nightly build.

## 3. Những loại issue nào nên block pipeline, loại nào chỉ warning?

### 3.1. Blocking (fail pipeline)

- Các issue severity **ERROR**, ví dụ:
  - Command injection (`os.system` với input không được kiểm soát).
  - SQL injection, RCE, authentication bypass, hard-coded secret,...
- Tiêu chí:
  - Có khả năng dẫn đến **rủi ro bảo mật nghiêm trọng** hoặc dễ bị khai thác trực tiếp.
- Trong repo demo:
  - Rule `go.os.exec.command-injection` (Semgrep) có severity `ERROR`.
  - Khi Semgrep phát hiện, script `ci/evaluate_semgrep.py` trả về exit code 1 → pipeline **FAIL**.

### 3.2. Non-blocking (chỉ warning)

- Các issue severity **WARNING** hoặc **INFO**, ví dụ:
  - Code smell, style issue, practice chưa tốt.
  - Rủi ro tiềm ẩn nhưng cần thêm context để kết luận (ví dụ: so sánh `==` trong một số trường hợp).
- Chính sách:
  - Không chặn pipeline (script evaluate trả exit code 0).
  - Vẫn được log trong report JSON (`reports/semgrep.json`) để team lên kế hoạch xử lý dần (security backlog / tech debt).

### 3.3. Lợi ích của việc phân loại

- Tránh tình trạng mọi issue đều block khiến developer bị "ngợp" và bỏ qua cảnh báo.
- Tập trung nguồn lực vào việc xử lý những lỗ hổng nghiêm trọng trước.

## 4. Hướng dẫn chạy demo

### 4.1. Chạy Jenkins bằng Docker Compose

1. Build và start Jenkins:

```bash
docker compose build
docker compose up -d jenkins
```

2. Truy cập `http://localhost:8080`, lấy admin password từ log container:

```bash
docker logs jenkins-ci
```

3. Hoàn tất wizard setup Jenkins (plugin mặc định).

### 4.2. Tạo Jenkins pipeline từ GitHub

1. Tạo repo public trên GitHub, push toàn bộ mã nguồn này lên.
2. Trong Jenkins:
   - New Item → nhập tên job → chọn **Pipeline**.
   - Pipeline: chọn **Pipeline script from SCM** → SCM: **Git**, URL repository, branch `main`.
   - Script path: **`Jenkinsfile`** (một pipeline cho Task 1, 2, 3).
3. **Build Now** để chạy pipeline.

Pipeline sẽ chạy qua các stage:

1. **Build (Go)**: `cd /workspace/app`, `go mod tidy`, `go build ./...`; cài Semgrep (pip).
2. **Test (Go)**: `go test ./...` trong `app/`.
3. **Quality (SonarQube)** *(optional)*: sonar-scanner nếu có token; evaluate_sonar.py.
4. **Security (SAST)**: Semgrep với rule có sẵn (`--config auto`), sinh `reports/semgrep.json`, `ci/evaluate_semgrep.py` → pass/fail theo severity (ERROR = block). Không cần viết rule.
5. **Docker Build Image** *(optional)*: build image từ `app/Dockerfile`.
6. **Image Scan (Trivy)** *(optional)*: Trivy scan image, `ci/evaluate_trivy.py`.
7. **Deploy mock**: `docker compose up -d app` (Go app, port 8000).

### 4.3. Diễn giải kết quả pipeline

- Nếu Semgrep phát hiện issue severity `ERROR`:
  - `ci/evaluate_semgrep.py` exit code 1.
  - Stage Security fail, toàn bộ pipeline trong Jenkins **FAIL**.
- Nếu chỉ có `WARNING` hoặc không có issue:
  - Script exit code 0.
  - Pipeline **SUCCESS**.
- File report:
  - `reports/semgrep.json` được archive trong build artifacts của Jenkins.
- **Bản mẫu SAST report**: File `docs/sample_semgrep_report.json` (1 finding ERROR – command injection trong `app/main.go`). Khi chạy Task 1, pipeline có thể fail ở stage Security và sinh `reports/semgrep.json` tương tự; bản mẫu dùng để tham khảo format khi không chạy Jenkins.

### 4.4. Deploy ứng dụng (mock)

- Từ máy host (ngoài Jenkins):

```bash
docker compose up -d app
```

- Truy cập:
  - `http://localhost:8000` để xem ứng dụng Go chạy.
- Đây là bước deploy giả lập (mock), mô phỏng việc deploy sau khi pipeline đã Build/Test/Security thành công.

