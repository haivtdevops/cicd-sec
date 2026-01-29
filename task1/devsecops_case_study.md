## Case Study – AppSec/DevSecOps Engineer

### Slide 1 – Tổng quan & bối cảnh

- **Bối cảnh hiện tại**
  - Các team đang có CI/CD riêng lẻ, khó quản lý tập trung.
  - Kiểm tra bảo mật chủ yếu thủ công, thường làm muộn ở cuối vòng đời.
- **Vấn đề**
  - Khó phát hiện sớm lỗ hổng, chi phí khắc phục cao.
  - Rủi ro vi phạm bảo mật & compliance tăng theo số lượng sản phẩm.
- **Mục tiêu DevSecOps**
  - Tích hợp bảo mật xuyên suốt từ design → code → build → deploy → vận hành.
  - Chuẩn hóa pipeline cho toàn công ty A, tự động hóa các kiểm soát bảo mật.
- **Nguyên tắc**
  - Security as Code, Policy as Code.
  - Tự động hoá tối đa, feedback nhanh, minh bạch cho Dev/QA/Operations.

---

### Slide 2 – Quy trình & kế hoạch chuẩn hoá

- **Những yếu tố cần chuẩn hóa**
  - **Quy trình phát triển**: flow nhánh Git (main/dev/feature), quy tắc PR & code review.
  - **Quy trình CI/CD**: các stage bắt buộc (build, test, security scan, deploy).
  - **Công cụ chuẩn**: hệ thống CI (ví dụ: GitLab CI), registry, secret management, logging.
  - **Chuẩn bảo mật**: loại scan bắt buộc (SAST, SCA, DAST, container), policy pass/fail.
- **Lộ trình triển khai**
  - **Phase 1 – Thiết kế & pilot**
    - Xây dựng pipeline template chuẩn cho web app.
    - Áp dụng thử trên 1–2 dự án đại diện, tinh chỉnh theo feedback.
  - **Phase 2 – Rollout**
    - Mở rộng template cho nhiều tech stack (Java/.NET/Node.js…).
    - Triển khai dần cho các dự án, kết hợp đào tạo Dev/QA/Ops.
  - **Phase 3 – Tối ưu**
    - Đặt KPI (vuln, MTTR, tỉ lệ scan) và theo dõi theo quý.
    - Tối ưu hiệu năng pipeline, giảm thời gian chạy, nâng tỉ lệ tự động hoá.
- **Governance**
  - Tổ DevSecOps/AppSec đóng vai trò Center of Excellence.
  - Quản lý repo template/pipeline, review định kỳ policy & công cụ.

---

### Slide 3 – Thiết kế CI/CD pipeline chuẩn cho web app

- **CI – Stages chính**
  - **Code → Commit**
    - Pre-commit: linting, unit test nhanh, secret scan nhẹ.
  - **Build**
    - Compile, chạy test cơ bản, build artifact/container image.
  - **Test**
    - Unit test, integration test, API test tự động.
  - **Security scan**
    - SAST trên source code.
    - SCA trên dependency.
    - Container image scan (nếu dùng Docker/K8s).
  - **Publish**
    - Push artifact/image lên registry (nếu pass tất cả gates).
- **CD – Stages chính**
  - **Deploy Staging**
    - Triển khai tự động lên môi trường Staging.
    - Chạy smoke test + DAST tự động.
  - **Approval**
    - Kiểm tra kết quả test & security, phê duyệt nếu đạt.
  - **Deploy Production**
    - Triển khai blue/green hoặc canary, có rollback dự phòng.
- **Hạ tầng & IaC**
  - Dùng Terraform/Ansible/Helm để mô tả hạ tầng.
  - Scan IaC trước khi apply (tfsec/Checkov).

---

### Slide 4 – Security gates trong pipeline

- **SAST**
  - Chạy sau build, trước khi publish artifact.
  - Công cụ ví dụ: SonarQube, Checkmarx, Bandit, ESLint security rules.
  - Mục tiêu: phát hiện SQLi, XSS, hard-coded secrets, insecure API usage.
- **SCA**
  - Scan dependency (Maven, NPM, pip, NuGet...) với OWASP Dependency-Check, Snyk, Trivy.
  - Phát hiện CVE trong thư viện bên thứ ba, kiểm tra license.
- **Container Image Scanning**
  - Scan image trước khi push lên registry hoặc trước deploy.
  - Phát hiện lỗ hổng trong OS/base image & package hệ thống.
- **DAST**
  - OWASP ZAP/Burp automation trên môi trường Staging.
  - Kiểm tra runtime issues: auth, session, input validation, misconfig, v.v.
- **Secret & Config Scanning**
  - Gitleaks/TruffleHog trên repo và lịch sử commit.
  - Kiểm tra config hạ tầng (open port, insecure protocol, v.v.).

---

### Slide 5 – Policy enforcement & ví dụ

- **Policy as Code**
  - Mô tả rule bằng code (YAML/Rego…), lưu trong repo.
  - Tự động thực thi trong pipeline, không phụ thuộc con người.
- **Ví dụ – Block build bởi vulnerability**
  - Nếu SAST/SCA/container scan phát hiện:
    - **Any Critical** → fail pipeline ngay, không cho build tiếp.
    - **High** mà không có exception được phê duyệt → fail.
    - Medium/Low → cho pass nhưng tự động tạo ticket để xử lý sau.
- **Ví dụ – Quality gate**
  - Không cho merge nếu:
    - Code coverage < 80%.
    - Có security hotspot chưa review.
- **Exception Management**
  - Cơ chế approve exception có thời hạn (time-bound).
  - Chỉ AppSec/Tech Lead được quyền chấp thuận.

---

### Slide 6 – Secure-by-design & threat modeling

- **Secure-by-design**
  - Định nghĩa sẵn các security requirement cho web app:
    - Authentication/authorization chuẩn, logging/auditing, data encryption.
  - Dùng kiến trúc tham chiếu (reference architecture) an toàn:
    - TLS end-to-end, network segmentation, least privilege.
  - Coding guideline theo OWASP ASVS & secure coding practices.
- **Threat modeling**
  - Thực hiện ở giai đoạn design cho feature lớn:
    - Sử dụng STRIDE để xác định threat (Spoofing, Tampering, Repudiation…).
    - Xác định tài sản (assets), trust boundaries, entry points.
  - Kết quả:
    - Sinh backlog task/requirement bảo mật trong Jira.
    - Mapping threat High → control tương ứng (SAST rule, DAST test, config rule).
- **Tích hợp với pipeline**
  - Yêu cầu PR cho feature quan trọng phải attach threat model summary.
  - Checklist trong review: feature đã có test & scan tương ứng với threat hay chưa.

---

### Slide 7 – KPI/metrics cho BOD

- **KPI về lỗ hổng**
  - % High/Critical vulnerabilities được fix trong vòng X ngày.
  - Mean Time To Remediate (MTTR) cho High/Critical.
- **KPI về adoption & chất lượng**
  - % dự án sử dụng pipeline chuẩn hóa DevSecOps.
  - % release pass toàn bộ security gates (SAST, SCA, DAST, container).
- **KPI về tốc độ**
  - Lead time for change: từ commit đến deploy production.
  - Tần suất release sau khi áp dụng DevSecOps (weekly/bi-weekly…).

---

### Slide 8 – Kết luận & roadmap

- **Lợi ích chính**
  - Giảm rủi ro bảo mật, tránh incident lớn & tổn hại uy tín.
  - Tăng tốc độ ra sản phẩm nhưng vẫn đảm bảo an toàn & compliance.
- **Roadmap đề xuất**
  - 0–3 tháng: thiết kế template, chọn tool, pilot.
  - 3–6 tháng: rollout dần, đào tạo, chỉnh policy.
  - 6–12 tháng: tối ưu KPI, bổ sung tính năng nâng cao (runtime security, bug bounty).
- **Thông điệp cuối**
  - DevSecOps là thay đổi về văn hóa: Dev, Sec, Ops cùng chịu trách nhiệm.
  - Mục tiêu: “secure by default, secure by design” cho mọi sản phẩm.

---

### Script nói 10 phút (tham khảo)

**Slide 1 – Tổng quan & bối cảnh**

Hôm nay em sẽ trình bày đề xuất DevSecOps cho công ty A.  
Hiện tại, các dự án đang có CI/CD khá rời rạc, mỗi team tự triển khai, nên rất khó kiểm soát thống nhất. Các hoạt động bảo mật chủ yếu làm thủ công, thường diễn ra muộn ở cuối vòng đời phát triển, dẫn tới việc phát hiện lỗ hổng trễ, chi phí khắc phục cao và tiềm ẩn rủi ro lớn cho doanh nghiệp.  
Mục tiêu của đề xuất này là chuẩn hóa một quy trình CI/CD chung, tích hợp bảo mật xuyên suốt – từ giai đoạn design, coding cho đến deploy và vận hành – theo mô hình DevSecOps. Em sẽ tập trung vào 3 ý chính: chuẩn hóa quy trình, thiết kế pipeline mẫu cho web app, và cách nhúng các security gate, policy và KPI để đo lường hiệu quả.

**Slide 2 – Quy trình & kế hoạch chuẩn hoá**

Đầu tiên là phần chuẩn hóa quy trình.  
Về yếu tố cần chuẩn hóa, chúng ta cần thống nhất flow phát triển: cách dùng nhánh Git, quy tắc tạo Pull Request, yêu cầu code review. Kế tiếp là chuẩn hóa các stage trong CI/CD, ví dụ mọi dự án web đều phải có build, test, security scan và deploy. Đồng thời, công ty cần chọn một bộ công cụ chuẩn – như GitLab/GitHub, hệ thống CI, registry và cơ chế quản lý secret – để dễ vận hành và hỗ trợ.  
Kế hoạch triển khai chia làm 3 phase: thiết kế pipeline template và pilot trên vài dự án đại diện; sau đó rollout dần cho các dự án còn lại kèm đào tạo; cuối cùng là giai đoạn tối ưu, theo dõi KPI và cải tiến. Để đảm bảo bền vững, chúng ta cần một nhóm DevSecOps hoặc AppSec đóng vai trò Center of Excellence, quản lý các template và policy dùng chung.

**Slide 3 – Thiết kế CI/CD pipeline chuẩn cho web app**

Với một ứng dụng web điển hình, pipeline chuẩn sẽ gồm các bước như sau.  
Khi developer commit code lên Git, CI pipeline được kích hoạt. Đầu tiên là stage build – compile code, chạy unit test nhanh, build artifact hoặc container image. Sau đó là stage test, nơi chúng ta chạy unit test đầy đủ, integration test hoặc API test.  
Tiếp theo là security scan: chạy SAST trên mã nguồn, SCA trên dependency, và container scan trên image nếu có. Chỉ khi tất cả bước này pass thì artifact hoặc image mới được publish lên registry.  
Ở phần CD, chúng ta tự động deploy lên Staging, chạy smoke test và DAST. Nếu mọi thứ ổn và đáp ứng tiêu chí bảo mật, pipeline sẽ cho phép deploy sang Production bằng chiến lược an toàn như blue/green hoặc canary, luôn sẵn rollback. Hạ tầng nên được mô tả bằng IaC để đảm bảo consistency và có thể scan bảo mật hạ tầng trước khi apply.

**Slide 4 – Security gates trong pipeline**

Phần quan trọng nhất là các security gate.  
Đầu tiên là SAST – phân tích tĩnh mã nguồn, để phát hiện các lỗi như SQL injection, XSS, hard-coded secret. Công cụ có thể là SonarQube, Checkmarx hoặc các tool open-source tương đương.  
Thứ hai là SCA – phân tích dependency để tìm các thư viện có CVE đã biết, dùng các công cụ như Snyk, OWASP Dependency-Check hoặc Trivy.  
Thứ ba là container scanning – kiểm tra image để phát hiện lỗ hổng trong hệ điều hành và package nền.  
Sau khi deploy lên Staging, chúng ta dùng DAST – ví dụ OWASP ZAP – để kiểm tra hành vi ứng dụng chạy thực tế.  
Ngoài ra, chúng ta kiểm tra secret và cấu hình với các tool như Gitleaks, đảm bảo không có credential bị commit nhầm hoặc config nguy hiểm.

**Slide 5 – Policy enforcement & ví dụ**

Để các bước kiểm tra này thực sự có hiệu lực, chúng ta cần policy as code.  
Thay vì chỉ là guideline, các policy sẽ được mô tả bằng code và thực thi tự động trong pipeline. Ví dụ, với kết quả SAST/SCA/container scan, pipeline sẽ tự động fail nếu xuất hiện bất kỳ lỗ hổng Critical, hoặc lỗ hổng High mà chưa được cấp exception. Các lỗ hổng Medium/Low có thể cho phép pass nhưng sẽ tự động tạo ticket để theo dõi và xử lý sau.  
Tương tự, chúng ta có thể đặt quality gate cho code coverage – ví dụ yêu cầu tối thiểu 80%, hoặc không cho merge nếu còn security hotspot chưa được review.  
Với các trường hợp cần ngoại lệ, chúng ta có cơ chế exception management rõ ràng: chỉ AppSec hoặc Tech Lead được quyền approve, có thời hạn và được ghi log để audit.

**Slide 6 – Secure-by-design & threat modeling**

DevSecOps không chỉ là thêm tool vào pipeline, mà bắt đầu từ thiết kế.  
Về secure-by-design, công ty cần định nghĩa sẵn các yêu cầu bảo mật cho ứng dụng web: cơ chế xác thực/ủy quyền chuẩn, logging/auditing, mã hóa dữ liệu nhạy cảm, và kiến trúc mạng an toàn.  
Ở giai đoạn design, cho mỗi feature quan trọng, team thực hiện threat modeling – dùng framework như STRIDE để xác định các mối đe dọa, asset quan trọng và boundary. Kết quả threat model sẽ được chuyển thành backlog item, test case, và rule trong SAST/DAST hoặc policy hạ tầng.  
Trong quy trình, các Pull Request lớn cần đính kèm tóm tắt threat model và cách xử lý. Như vậy, pipeline không chỉ kiểm tra code, mà còn đảm bảo mỗi rủi ro đã có control tương ứng.

**Slide 7 – KPI/metrics cho BOD**

Để báo cáo hiệu quả DevSecOps lên Ban Giám đốc, chúng ta cần những KPI rõ ràng.  
Nhóm thứ nhất là KPI về lỗ hổng: tỷ lệ High/Critical được xử lý trong một khoảng thời gian nhất định, và thời gian trung bình từ khi phát hiện đến khi khắc phục – MTTR.  
Nhóm thứ hai là KPI về adoption và chất lượng: tỷ lệ dự án sử dụng pipeline chuẩn DevSecOps, tỷ lệ release pass toàn bộ security gates.  
Nhóm thứ ba là KPI về tốc độ: lead time từ commit đến deploy production, tần suất release sau khi áp dụng DevSecOps. Các số liệu này giúp BOD thấy rằng bảo mật không làm chậm lại, mà giúp quy trình trở nên có kiểm soát và ổn định hơn.

**Slide 8 – Kết luận & roadmap**

Kết lại, việc chuẩn hóa pipeline DevSecOps sẽ giúp công ty A giảm đáng kể rủi ro bảo mật, đồng thời nâng cao tốc độ và độ ổn định khi release.  
Em đề xuất roadmap 6–12 tháng: vài tháng đầu tập trung thiết kế và pilot; sau đó rollout và đào tạo; cuối cùng là tối ưu KPI và bổ sung các lớp bảo vệ nâng cao như runtime security hoặc chương trình bug bounty.  
Quan trọng hơn cả, DevSecOps là thay đổi về văn hóa: thay vì “bảo mật là việc của team Security”, thì Dev, Sec, và Ops cùng chịu trách nhiệm. Mục tiêu cuối cùng là mọi sản phẩm của công ty đều “secure by default” và “secure by design”.

