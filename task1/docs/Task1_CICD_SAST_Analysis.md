## 1. Vì sao chọn SAST tool Semgrep?

- **Dễ cài đặt & chạy local**: Semgrep nhẹ, chỉ cần Python/pip hoặc Docker, phù hợp cho mô hình chạy CI/CD local bằng `docker-compose`.
- **Rule tuỳ chỉnh, hỗ trợ nhiều ngôn ngữ**: Hỗ trợ Python, JS, Java, Go,... và dễ tự viết rule theo pattern code (ví dụ phát hiện `os.system` hoặc so sánh `==`).
- **Tích hợp CI/CD đơn giản**: Câu lệnh CLI rõ ràng (`semgrep --config ... --json --output ...`), dễ sinh report JSON để pipeline parse ra pass/fail.
- **Mã nguồn mở & cộng đồng lớn**: Có nhiều ruleset có sẵn theo OWASP / best practice, dễ mở rộng dần cho dự án thật.

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
  - Rule `python.os.system.command-injection` có severity `ERROR`.
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
   - Ở phần Pipeline:
     - Chọn **"Pipeline script from SCM"**.
     - SCM = **Git**, nhập URL GitHub repo.
     - Branch: `main` (hoặc phù hợp).
     - Script path: `Jenkinsfile`.
3. Bấm **Build Now** để chạy thử.

Pipeline sẽ chạy qua các stage:

1. **Build**: tạo virtualenv, cài dependency từ `app/requirements.txt`, byte-compile `.py`.
2. **Test**: chạy pytest trên thư mục `app/tests`.
3. **Security (SAST)**:
   - Chạy Semgrep với `.semgrep.yml`.
   - Sinh report JSON tại `reports/semgrep.json`.
   - Chạy `ci/evaluate_semgrep.py` để quyết định pass/fail dựa trên severity.
4. **Deploy mock**:
   - Chỉ chạy khi các stage trước `SUCCESS`.
   - In hướng dẫn deploy thật, trong demo là `docker compose up -d app`.

### 4.3. Diễn giải kết quả pipeline

- Nếu Semgrep phát hiện issue severity `ERROR`:
  - `ci/evaluate_semgrep.py` exit code 1.
  - Stage Security fail, toàn bộ pipeline trong Jenkins **FAIL**.
- Nếu chỉ có `WARNING` hoặc không có issue:
  - Script exit code 0.
  - Pipeline **SUCCESS**.
- File report:
  - `reports/semgrep.json` được archive trong build artifacts của Jenkins.

### 4.4. Demo Deploy mock app

- Từ máy host (ngoài Jenkins), chạy:

```bash
docker compose up -d app
```

- Truy cập:
  - `http://localhost:8000` để xem ứng dụng Flask chạy.
- Đây là bước deploy giả lập (mock), mô phỏng việc deploy sau khi pipeline đã Build/Test/Security thành công.

