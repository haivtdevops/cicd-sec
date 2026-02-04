# Task 5 – Secure-by-Design & Threat Modeling

## System description (hệ thống khác với các task trên)

Hệ thống mô tả **không phải** ứng dụng Go trong Task 1/2/3, mà là kiến trúc:

- **Web App** (frontend) – giao diện người dùng, gọi API, chuyển hướng thanh toán.
- **API** (backend) – xác thực, xử lý nghiệp vụ, truy vấn DB, nhận callback từ Payment.
- **Database** – lưu user, session, giao dịch.
- **External Payment Service** – xử lý thanh toán; gửi callback/webhook về API.

---

## 1. Yêu cầu: Vẽ sơ đồ DFD (Data Flow Diagram)

**DFD – Level 0 (context):**

```
                    HTTPS (request/response)
    ┌──────────┐ ◄────────────────────────────► ┌──────────┐
    │   User   │                                │ Web App  │
    │ (Browser)│                                │(Frontend)│
    └──────────┘                                └────┬─────┘
                                                     │ HTTPS
                                                     ▼
    ┌──────────────┐     HTTPS (API calls)     ┌──────────┐
    │  External   │ ◄────────────────────────►│   API    │
    │  Payment    │   callback/webhook        │(Backend) │
    │  Service    │ ────────────────────────► │          │
    └──────────────┘                           └────┬─────┘
                                                     │ SQL/TLS
                                                     ▼
                                               ┌──────────┐
                                               │ Database │
                                               │   (DB)   │
                                               └──────────┘

    Trust boundary (ví dụ):
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    [ Internet ]    [ DMZ / App tier ]    [ Internal ]
         User            Web App, API          DB
                         Payment callback ◄──► API
```

**Thành phần:**

| Ký hiệu | Ý nghĩa |
|---------|---------|
| **User** | External entity – người dùng trình duyệt. |
| **Web App** | Process – frontend, nhận input, gọi API, redirect thanh toán. |
| **API** | Process – backend, auth, logic, truy vấn DB, xử lý callback Payment. |
| **Database** | Data store – lưu trữ user, session, transaction. |
| **External Payment Service** | External entity – dịch vụ thanh toán bên ngoài; gửi callback về API. |
| **Data flow** | HTTPS (User ↔ Web App, Web App ↔ API); callback (Payment → API); SQL/TLS (API ↔ DB). |

---

## 2. Yêu cầu: Xác định 3 mối đe dọa chính (ít nhất 1 liên quan API/auth)

### Bảng threat

| # | Threat | Mô tả | Liên quan |
|---|--------|--------|-----------|
| **T1** | **Broken Authentication / Session hijack** | API/auth dùng token hoặc session yếu, lộ hoặc không hết hạn → attacker giả mạo user, truy cập dữ liệu hoặc thực hiện giao dịch thay user. | **API / Auth** |
| **T2** | **SQL Injection / Insecure Direct Object Reference (IDOR)** | Input từ Web App/API không được sanitize → truy vấn SQL bị inject hoặc IDOR cho phép truy cập tài nguyên của user khác. | API → DB |
| **T3** | **Payment callback manipulation / Replay** | Attacker giả mạo hoặc replay callback từ Payment Service → API chấp nhận “payment success” giả, cập nhật order/balance sai. | API ↔ External Payment |

*Đáp ứng:* Cả 3 threat đều liên quan API; **T1** trực tiếp **API/auth**.

---

## 3. Yêu cầu: Mapping

### 3.1. Threat → Design control

| Threat | Design control |
|--------|----------------|
| **T1** (Broken Auth / Session hijack) | (1) Auth: JWT/OAuth, short-lived token, secure cookie (HttpOnly, SameSite). (2) Rate limit login; MFA cho thao tác nhạy cảm. (3) Log và monitor failed auth; lock account sau N lần thất bại. |
| **T2** (SQLi / IDOR) | (1) Prepared statement / ORM; không nối SQL từ input. (2) Authorization check mỗi request: user chỉ truy cập resource của mình. (3) Input validation và output encoding. |
| **T3** (Payment callback / Replay) | (1) Verify signature/HMAC của callback từ Payment Service. (2) Idempotency key / nonce chống replay. (3) Validate amount, order id, status trước khi cập nhật DB. |

### 3.2. Design control → CI/CD security check

| Design control (tóm tắt) | CI/CD security check |
|---------------------------|------------------------|
| Auth (token, session, MFA) | **SAST** (Semgrep/CodeQL): rule hardcoded secret, weak crypto, insecure session. **SCA** (Trivy/Dependency-Check): thư viện auth có CVE. |
| Prepared statement, authorization, validation | **SAST**: rule SQL injection, command injection, path traversal. **Code review**; **DAST** (optional) cho API endpoint. |
| Signature/HMAC callback, idempotency, validate payload | **SAST**: rule hardcoded key, thiếu kiểm tra chữ ký. **Secret scan**: không lưu payment secret trong code. **Pipeline test**: unit/integration test callback với signed payload. |

---

## 4. Output – Tóm tắt cho PDF

| Output | Nội dung trong tài liệu / PDF |
|--------|-------------------------------|
| **DFD** | Sơ đồ DFD mục 1 – User, Web App, API, Database, External Payment Service; luồng dữ liệu HTTPS, callback, SQL/TLS; trust boundary. |
| **Bảng threat** | Bảng mục 2 – 3 threat: T1 (API/Auth), T2 (SQLi/IDOR), T3 (Payment callback); cột Threat, Mô tả, Liên quan. |
| **Mapping** | Mục 3.1: Threat → Design control. Mục 3.2: Design control → CI/CD security check (SAST, SCA, secret scan, test). |
| **Mô tả trong PDF** | Mô tả chung với các task khác trong **DevSecOps_CaseStudy_Report.pdf**: hệ thống (Web App + API + DB + External Payment), DFD, 3 threat, hai bảng mapping; có thể thêm 1 đoạn ngắn liên hệ với pipeline Task 1/2 (SAST Semgrep, SCA Trivy, secret scan) như ví dụ CI/CD check. |
