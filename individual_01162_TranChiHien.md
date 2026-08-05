# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| Họ và tên | Trần Chí Hiển |
| MSSV | 2A202601162 |
| Khóa/Lớp | K4 |
| Vai trò chính | QA, Validation & Audit Logging Specialist |
| Ngày hoàn thành | 2026-08-05 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| Automated Output Validator | `validate_outputs.py` | `output/*.json` | Validation Pass/Fail report cho 50 cases | Hoàn thành |
| Audit Logging & Metadata | `trace.jsonl`, `metadata.json` | Agent trace events | JSONL trace log & model metadata | Hoàn thành |
| Packaging & Final Submission | `output.zip` | `output/*.json` | `output.zip` đúng 50 JSON files | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Kiểm định dữ liệu | Cả nhóm | Phát hiện và báo cáo các lỗi vi phạm schema trong quá trình phát triển |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Xây dựng Validator Script | `validate_outputs.py` | Script kiểm tra tự động 12 tiêu chí bắt buộc của JSON schema | `python validate_outputs.py` |
| Quản lý Trace & Metadata | `trace.jsonl`, `metadata.json` | Lưu vết đầy đủ 50 cases và cấu hình mô hình `Qwen2.5-7B-Instruct` | Inspection file `trace.jsonl` |
| Nén bài nộp | `output.zip` | File zip chứa đúng 50 file JSON không chứa file rác | Zip structure inspection |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Đảm bảo 100% kết quả đầu ra tuân thủ các quy định chấm điểm tự động (Hard Gates), không bị 0 điểm do sai tên file, thiếu trường, vượt giới hạn số phần tử mảng hoặc chứa file lạ trong zip.

### Cách triển khai

- Xây dựng `validate_outputs.py` kiểm tra từng file JSON: `case_id`, `primary_issue` hợp lệ, thứ tự `secondary_issues`, giới hạn mảng (max 5 order/item/payment/product/category, max 3 seller/root cause/responsible party, max 20 evidence), định dạng tiền tệ `"BRL"`, và định dạng tiền tố `evidence_ids`.
- Thiết lập định dạng nhật ký `trace.jsonl` lưu theo chuẩn JSON lines ghi lại thời gian, sender, receiver, event_type và payload.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Vị trí lưu trữ file `trace.jsonl` và `metadata.json`.
- **Phương án đã chọn:** Lưu song song tại root repo (`/`) và thư mục `logging/`.
- **Lý do:** Đảm bảo dù hệ thống chấm điểm tự động tìm kiếm ở root repo hay thư mục `logging/` thì các file tài liệu audit vẫn luôn hiện diện.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** File `output.zip` ban đầu chứa cả thư mục con `output/` gây lỗi cấu trúc khi giải nén.
- **Cách xử lý:** Sử dụng lệnh PowerShell `Compress-Archive -Path 'output\EC_*.json' -DestinationPath 'output.zip' -Force` để đóng gói trực tiếp 50 file JSON vào root của file zip.

---

## 7. Hiểu biết về luồng end-to-end

QA & Validation Specialist kiểm định toàn bộ sản phẩm đầu ra của các agent, đảm bảo tính tuân thủ tiêu chuẩn trước khi tạo bản nộp cuối cùng `output.zip`.

---

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.

**Họ và tên:** Trần Chí Hiển  
**Ngày xác nhận:** 2026-08-05
