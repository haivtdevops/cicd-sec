# Task 3 – Policy Enforcement & Security Governance

## Scenario bắt buộc

Pipeline phát hiện: **1 Critical, 2 High, 2 Medium**.

---

## 1. Thiết kế policy enforcement

### 1.1. Điều kiện block / allow

| Điều kiện | Hành động |
|-----------|------------|
| Có ≥ 1 Critical | **BLOCK** pipeline |
| Có ≥ 2 High | **BLOCK** pipeline |
| Có ≥ 2 Medium (và không có exception) | **BLOCK** pipeline |
| Chỉ LOW / INFO | **ALLOW** (chỉ cảnh báo trong report, không fail pipeline) |

### 1.2. Exception: có cho phép không? Ai approve?

| Câu hỏi | Trả lời |
|---------|---------|
| **Exception có cho phép không?** | **Có.** Cho phép khi có lý do nghiệp vụ (release khẩn cấp, false positive đã xác nhận, hoặc kế hoạch fix trong thời hạn SLA). |
| **Ai approve?** | **CISO** hoặc **Security Lead**. Phê duyệt qua ticket (Jira/ServiceNow) kèm lý do và thời hạn xử lý. |
| **Cách áp dụng** | Ghi nhận exception trong pipeline: set env `POLICY_STRICT=false` cho build đó, hoặc whitelist theo CVE/ticket. Sau SLA (ví dụ 7 ngày) phải fix hoặc tái phê duyệt. |

### 1.3. Sơ đồ logic policy (text)

```
                    ┌─────────────────────────────────────┐
                    │  Aggregate findings (Semgrep +       │
                    │  Trivy) → Critical, High, Medium    │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  Có exception được approve?         │
                    │  (CISO/Security Lead, ticket)       │
                    └─────────────┬───────────┬───────────┘
                                  │ Yes       │ No
                                  ▼           ▼
                    ┌──────────────────┐  ┌─────────────────────────────────────┐
                    │  ALLOW (pass)    │  │  Critical >= 1 ?  OR  High >= 2 ?   │
                    │  Ghi log warning │  │  OR  Medium >= 2 ?                  │
                    └──────────────────┘  └─────────────┬───────────┬───────────┘
                                                        │ Yes       │ No
                                                        ▼           ▼
                    ┌──────────────────┐  ┌──────────────────┐
                    │  BLOCK (fail)    │  │  ALLOW (pass)     │
                    │  exit 1          │  │  exit 0           │
                    └──────────────────┘  └──────────────────┘
```

**Logic (pseudocode):**

```
IF có_exception_approved THEN
  pipeline PASS (log warning)
ELSE IF (Critical >= 1) OR (High >= 2) OR (Medium >= 2) THEN
  pipeline FAIL (exit 1)
ELSE
  pipeline PASS (exit 0)
END IF
```

---

## 2. Mô tả dashboard / reporting

### 2.1. CISO / BOD nhìn gì?

| Nội dung (mock) | Mô tả |
|-----------------|--------|
| **Tổng hợp severity** | Bảng/số: tổng findings theo Critical, High, Medium (theo tuần/tháng). |
| **Trend** | Biểu đồ xu hướng: số finding theo thời gian; số pipeline bị block. |
| **Exception** | Số exception đang mở; danh sách ticket (project, lý do, hạn xử lý). |
| **SLA breach** | Cảnh báo: Critical/High chưa fix đúng hạn (ví dụ > 7 ngày / > 14 ngày). |
| **Tổng quan rủi ro** | Số repo/service có finding Critical/High; so sánh với kỳ trước. |

*Mock:* Một trang dashboard gồm bảng tổng hợp severity, biểu đồ line/bar trend, danh sách exception, và bảng SLA breach.

### 2.2. Dev team nhìn gì?

| Nội dung (mock) | Mô tả |
|-----------------|--------|
| **Findings theo repo/service** | Danh sách findings gán cho repo của team; filter theo severity, nguồn (Semgrep/Trivy/Sonar). |
| **Link report** | Link tới file report (Semgrep JSON, Trivy JSON) hoặc trang SonarQube/Trivy UI. |
| **Hướng dẫn fix** | Message từ rule (Semgrep, Trivy); link CVE, remediation (FixedVersion, Resolution). |
| **Trạng thái pipeline** | Pass/Fail; lý do fail (ví dụ: "Blocking findings (ERROR): 1", "Policy: BLOCK – thresholds exceeded"). |
| **Lịch sử build** | Build gần nhất pass/fail; so sánh với build trước (số finding tăng/giảm). |

*Mock:* Trang "My findings" với bảng findings (repo, file, severity, rule, link), nút xem report, và trạng thái pipeline của branch.

---

## 3. Quy trình xử lý

| Yêu cầu | Nội dung |
|---------|----------|
| **Ai chịu trách nhiệm fix?** | **Dev / owner repo** (code + dependency). **DevOps / SRE** nếu là config/IaC (Dockerfile, compose, pipeline). Security hỗ trợ đánh giá và remediation. |
| **SLA cho Critical/High?** | **Critical:** fix trong **7 ngày** (hoặc exception có thời hạn, sau đó phải fix hoặc tái phê duyệt). **High:** fix trong **14 ngày**. Medium theo backlog. |
| **Giao tiếp với Product như thế nào?** | Security gửi summary (severity, link report, đề xuất ưu tiên) qua ticket/email. Product ưu tiên sprint; **release bị block** cho đến khi pass policy hoặc exception được CISO/Security Lead approve. Thông báo khi có Critical/High để điều chỉnh kế hoạch release. |

---

## 4. Output – Hướng dẫn chạy demo (step-by-step)

### Step 1: Khởi động môi trường

Từ thư mục gốc repository:

```bash
docker compose build
docker compose up -d jenkins sonarqube init-sonar
```

Đợi Jenkins và SonarQube sẵn sàng (ví dụ 1–2 phút).

### Step 2: Truy cập Jenkins

- Mở trình duyệt: `http://localhost:8080`.
- Lần đầu: lấy mật khẩu admin bằng `docker logs jenkins-ci`; hoàn tất setup wizard nếu có.

### Step 3: Tạo Pipeline job (Task 3)

- **New Item** → nhập tên (ví dụ: `Task3-Policy`) → chọn **Pipeline** → OK.
- **Pipeline**: chọn **Pipeline script from SCM**.
- **SCM**: Git; Repository URL = URL repo (public); Branch: `main`.
- **Script path**: `Jenkinsfile` (pipeline duy nhất có stage Policy).

### Step 4: Chạy pipeline

- Bấm **Build Now**.
- Pipeline chạy: Build (Go) → Test → Quality (SonarQube) → Security (Semgrep) → Docker Build → Image Scan (Trivy) → **Policy (Task 3)**.

### Step 5: Kết quả Policy (Task 3)

- Stage **Policy (Task 3)** đọc `reports/policy_summary.json` (mock: `{"CRITICAL":1,"HIGH":2,"MEDIUM":2}`) hoặc aggregate từ Semgrep + Trivy.
- Script `ci/evaluate_policy.py` áp dụng điều kiện: Critical≥1 hoặc High≥2 hoặc Medium≥2 → **BLOCK** → pipeline **FAIL**.
- Trong console output: in "Policy: BLOCK – pipeline FAILED"; exit 1.
- Report lưu trong **Build Artifacts** (thư mục `reports/`).

### Step 6 (tùy chọn): Chạy policy script local

```bash
echo '{"CRITICAL":1,"HIGH":2,"MEDIUM":2}' > reports/policy_summary.json
python ci/evaluate_policy.py --input reports/policy_summary.json --policy task3_demo
# Kỳ vọng: exit 1 (BLOCK)
```

Để pipeline pass khi dùng mock: đặt `{"CRITICAL":0,"HIGH":0,"MEDIUM":0}` hoặc set env **POLICY_STRICT=false** (chỉ cảnh báo, không block).

---

## Tóm tắt Output (cho PDF)

| Output | Nội dung trong tài liệu |
|--------|---------------------------|
| **Sơ đồ logic policy** | Mục 1.3 – sơ đồ text + pseudocode (block/allow, exception). |
| **Mô tả dashboard** | Mục 2 – CISO/BOD (tổng hợp, trend, exception, SLA breach); Dev team (findings theo repo, link report, trạng thái pipeline). |
| **Hướng dẫn chạy demo** | Mục 4 – step-by-step: khởi động → Jenkins → tạo job → Build Now → xem kết quả Policy; chạy script local (tùy chọn). |
