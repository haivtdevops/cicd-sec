# Phân tích SAST và chính sách pipeline

## 1. Vì sao chọn SAST tool Semgrep?

- **Rule có sẵn, không cần viết code**  
  Semgrep Registry cung cấp hàng nghìn rule (Go, Python, Java, …). Chạy `semgrep scan --config auto` sử dụng rule tự động theo ngôn ngữ phát hiện trong repo; không bắt buộc viết rule (có thể bổ sung `.semgrep/go.yml` nếu cần rule riêng).

- **Phù hợp với CI/CD local**  
  Cài đặt đơn giản (Python/pip hoặc container), chạy trong môi trường Docker + Jenkins mà không cần triển khai server riêng. Một lệnh CLI với `--config`, `--json`, `--output` đủ để sinh report và tích hợp pass/fail vào pipeline.

- **Đa ngôn ngữ và mở rộng**  
  Hỗ trợ Go, Python, Java, JavaScript/TypeScript, v.v., phù hợp đa tech stack. Rule dạng pattern-based, dễ bổ sung rule tùy chỉnh (ví dụ: `go.os.exec.command-injection` cho `exec.Command("sh", "-c", cmd)`).

- **Security in the Pipeline**  
  Thời gian chạy ngắn, có thể đặt trong mỗi build. Kết quả xuất JSON/SARIF, pipeline đọc và quyết định pass/fail.

Trong repo này Semgrep là **SAST chính**; SonarQube dùng cho **Quality (tùy chọn)**.

---

## 2. Chạy SAST ở stage nào? Vì sao?

Pipeline Jenkins được tổ chức theo thứ tự:

1. **Build (Go)**: build source, cài Semgrep trong container.  
2. **Test (Go)**: chạy `go test ./...`.  
3. **Quality (SonarQube)** *(tùy chọn)*: phân tích quality khi có sonar-scanner.  
4. **Security (Semgrep)**: chạy SAST, sinh report JSON và parse pass/fail.  
5. **Docker Build Image** *(tùy chọn)*: build Docker image.  
6. **Image Scan (Trivy)** *(tùy chọn)*: quét image bằng Trivy.

**SAST (Semgrep) đặt sau Build và Test, trước Docker Build và Image Scan**, vì:

- **Build trước**: đảm bảo code compile và dependency đầy đủ; nếu build lỗi thì scan bảo mật không cần thiết.  
- **Test trước**: code đã qua unit test, giảm nhiễu từ code chưa ổn định.  
- **Security sau Test**: đóng vai trò cổng kiểm soát bảo mật cho source code trước khi đóng gói image hoặc deploy.

Trong môi trường production có thể chạy quick SAST sớm (ví dụ tại merge request) và full SAST ở stage gần cuối hoặc nightly.

---

## 3. Chính sách block / warning cho issue SAST

Script `ci/evaluate_semgrep.py` đọc `reports/semgrep.json`, đếm finding theo severity (ERROR, WARNING, INFO, …), đặc biệt số lượng **ERROR** (blocking). Quyết định pass/fail theo biến môi trường `SAST_STRICT`.

### 3.1. Issue block pipeline

- **Severity: ERROR** và `SAST_STRICT=true` (mặc định).  
- Ví dụ: command injection, SQL injection, RCE, bypass auth, hard-coded secret.  
- Hành vi: `blocking > 0` và `SAST_STRICT=true` → in thông báo fail, `sys.exit(1)` → stage Security fail, pipeline **FAIL**.  
- **Lý do**: lỗi có khả năng dẫn đến tấn công trực tiếp hoặc rủi ro cao, không cho code đi tiếp build/deploy.

### 3.2. Issue chỉ cảnh báo (không block)

- **Severity: WARNING hoặc INFO**: code smell, pattern chưa tối ưu, thực hành chưa tốt; vẫn ghi vào report JSON, không fail pipeline.  
- **ERROR nhưng `SAST_STRICT=false`**: dùng khi mới tích hợp SAST hoặc số issue nhiều; vẫn in summary, không fail. Sau khi xử lý xong có thể bật lại `SAST_STRICT=true`.

**Lý do**: tránh pipeline bị chặn liên tục khi mới tích hợp; cho phép team xử lý dần theo report và siết lại chính sách sau.

---

## 4. Tóm tắt

| Nội dung | Kết luận |
|----------|----------|
| **Tool SAST** | Semgrep: nhẹ, dễ tích hợp, đa ngôn ngữ, xuất JSON/SARIF. |
| **Vị trí SAST** | Sau Build + Test, trước Docker/Image Scan; cổng bảo mật cho source code. |
| **Block** | ERROR và `SAST_STRICT=true` → block pipeline. |
| **Warning** | WARNING/INFO hoặc `SAST_STRICT=false` → chỉ cảnh báo, ghi report để xử lý dần. |
