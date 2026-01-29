## Phân tích lựa chọn SAST và policy cho pipeline

### 1. Vì sao chọn SAST tool Semgrep?

- **Phù hợp cho demo CI/CD local**  
  - Semgrep cài đặt đơn giản (chỉ cần Python/pip hoặc container), chạy tốt trong môi trường Docker + Jenkins mà không cần dựng thêm server riêng như SonarQube.
  - Dễ tích hợp vào script shell/Jenkinsfile: chỉ một lệnh CLI với `--config`, `--json`, `--output` là đủ để sinh report và parse tiếp.

- **Hỗ trợ đa ngôn ngữ và rule tuỳ chỉnh**  
  - Hỗ trợ Go, Python, Java, JavaScript/TypeScript, v.v. → phù hợp với bối cảnh doanh nghiệp nhiều techstack.
  - Rule viết theo **mẫu code (pattern-based)** nên rất dễ mô phỏng/vẽ ra các tình huống demo, ví dụ:
    - Rule `go.os.exec.command-injection` để bắt `exec.Command("sh", "-c", cmd)`.

- **Rất hợp với mục tiêu “Security in the Pipeline”**  
  - Chạy nhanh, có thể đặt ngay trong pipeline Jenkins ở mỗi build.
  - Kết quả có thể xuất dưới dạng **JSON/SARIF**, thuận tiện để pipeline đọc và quyết định pass/fail.

Trong bài này, Semgrep được dùng làm **SAST chính**; SonarQube được giữ ở mức **Quality (optional)** do việc cài `sonar-scanner` CLI trong image demo bị giới hạn bởi môi trường.

### 2. Chạy SAST ở stage nào? Vì sao?

Pipeline Jenkins hiện tại được tổ chức như sau:

1. **Build (Go)**: build source, cài Semgrep trong container Jenkins.
2. **Test (Go)**: chạy `go test ./...` để kiểm tra logic.
3. **Quality (SonarQube)** *(optional)*: chạy phân tích quality (nếu có `sonar-scanner`).
4. **Security (Semgrep)**: chạy SAST, sinh JSON report và parse thành pass/fail.
5. **Docker Build Image** *(optional)*: build Docker image cho app.
6. **Image Scan (Trivy mock)** *(optional)*: scan image nếu có Trivy.

**SAST (Semgrep) được đặt sau Build + Test nhưng trước Docker Build/Image Scan**, vì:

- **Build trước**: đảm bảo code compile được, dependency đầy đủ. Nếu build đã lỗi thì việc scan bảo mật là thừa.
- **Test trước**: code đã qua kiểm tra unit test cơ bản → giảm noise từ code “chưa chạy được”.
- **Security sau Test**: đóng vai trò cổng kiểm soát bảo mật cuối cùng cho source code trước khi đóng gói thành image hoặc deploy (dù chỉ là deploy mock).

Trong môi trường production thật, có thể:

- Chạy **quick SAST** sớm (ví dụ khi mở merge request) để feedback nhanh.
- Chạy **full SAST** ở stage gần cuối hoặc nightly, tương tự cách bài này đang minh hoạ.

### 3. Chính sách block / warning cho issue SAST

Trong script `ci/evaluate_semgrep.py`, pipeline đọc JSON `reports/semgrep.json` và phân loại theo severity:

- Đếm số finding theo từng mức severity (ERROR, WARNING, INFO, ...).
- Đặc biệt chú ý số lượng **ERROR** (`blocking`).

```text
ERROR: N
Blocking findings (ERROR): N
```

Sau đó, quyết định pass/fail dựa trên biến môi trường `SAST_STRICT`:

#### 3.1. Issue nên block pipeline

- **Severity: ERROR** và `SAST_STRICT=true` (mặc định):
  - Ví dụ: command injection, SQL injection, RCE, bypass auth, hard-coded secret quan trọng, v.v.
  - Trong demo Go:
    - Nếu tồn tại rule `go.os.exec.command-injection` match `exec.Command("sh", "-c", cmd)` thì được xem là **blocking issue**.
  - Hành vi:
    - Nếu `blocking > 0` và `SAST_STRICT=true`:
      - In: `Pipeline FAILED due to blocking (ERROR) SAST issues.`
      - `sys.exit(1)` → stage SAST fail, toàn pipeline **FAIL**.

**Lý do**: đây là các lỗi có khả năng dẫn đến tấn công trực tiếp hoặc rủi ro rất cao, nên không cho phép code đi tiếp vào các bước build/deploy.

#### 3.2. Issue chỉ cảnh báo (warning, không block)

- **Severity: WARNING hoặc INFO**, hoặc muốn tạm thời không block lỗi ERROR (chế độ demo):
  - Ví dụ: code smell, pattern chưa tối ưu, thực hành chưa tốt, hoặc các lỗi cần thêm context để xác định mức độ rủi ro.
  - Có thể đặt `SAST_STRICT=false` để:
    - Không fail pipeline ngay cả khi có ERROR.
    - Vẫn log đầy đủ summary:

      ```text
      ERROR: N
      Blocking findings (ERROR): N
      WARNING: Có SAST findings severity ERROR, nhưng SAST_STRICT=false nên không block pipeline.
      ```

**Lý do**:

- Tránh “nghẽn” pipeline khi mới tích hợp SAST mà số lượng issue quá nhiều.
- Cho phép team dev/security dần dần dọn sạch technical debt: xem report JSON, ưu tiên xử lý các lỗi nghiêm trọng trước, sau đó siết lại `SAST_STRICT` về `true`.

### 4. Tóm tắt

- **Tool SAST chọn**: Semgrep, vì:
  - Nhẹ, dễ tích hợp CI/CD local.
  - Hỗ trợ đa ngôn ngữ, rule tuỳ chỉnh.
  - Xuất report JSON/SARIF, dễ parse trong pipeline.
- **Vị trí SAST trong pipeline**: sau Build + Test, trước Docker/image scan, đóng vai trò cổng bảo mật cho source code.
- **Chính sách block/warning**:
  - **ERROR + SAST_STRICT=true** → block pipeline.
  - **ERROR + SAST_STRICT=false** hoặc WARNING/INFO → chỉ cảnh báo, không block, nhưng vẫn ghi nhận trong JSON report để xử lý dần.

