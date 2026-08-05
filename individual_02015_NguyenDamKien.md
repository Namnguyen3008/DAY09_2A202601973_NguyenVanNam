# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| Họ và tên | Nguyễn Đàm Kiên |
| MSSV | 2A202602015 |
| Khóa/Lớp | K4 |
| Vai trò chính | Leader & Multi-Agent Orchestrator Developer (Coordinator & Verifier) |
| Ngày hoàn thành | 2026-08-05 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| Multi-Agent Orchestrator | `multi_agent_system.py` (`CoordinatorAgent`) | `input/EC_*.json` | Luồng điều phối A2A, `trace.jsonl` | Hoàn thành |
| Structural Verifier | `multi_agent_system.py` (`VerifierAgent`) | Output draft JSON | Pass/Fail status | Hoàn thành |
| System Architecture Doc | `architecture.md` | Thiết kế tổng thể hệ thống | Sơ đồ Mermaid & Ma trận truy cập dữ liệu | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Tích hợp A2A Contract | Nguyễn Văn Nam (Policy Agent) | Thống nhất dữ liệu handoff đầu vào cho Policy Engine |
| Review Code | Cả nhóm | Đảm bảo tuân thủ tiêu chuẩn code và không chứa API secret |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Xây dựng Coordinator Agent | `CoordinatorAgent.process_case()` | Luồng gọi tuần tự 7 agents và ghi nhận log | `python multi_agent_system.py` |
| Triển khai Verifier Agent | `VerifierAgent.verify()` | Kiểm tra giới hạn mảng (max 5/3/20) và kiểu dữ liệu | Automated verification script |
| Viết kiến trúc hệ thống | `architecture.md` | Tài liệu kiến trúc hoàn chỉnh tại root repo | Review file `architecture.md` |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Điều phối hoạt động giữa các agent chuyên biệt (Customer, Product, Payment, Delivery, Policy) sao cho dữ liệu được luân chuyển chính xác, không bị thất thoát thông tin và đảm bảo kết quả đầu ra tuân thủ nghiêm ngặt định dạng JSON schema.

### Cách triển khai

Triển khai `CoordinatorAgent` đóng vai trò trung tâm khởi tạo từng case, gọi tuần tự các agent và truyền payload dữ liệu thông qua cơ chế handoff. Triển khai `VerifierAgent` ở bước cuối cùng trước khi lưu file để kiểm tra các hard boundary (array length constraints, non-null values, confidence bounds).

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| Input | `input/EC_xxx.json` |
| Output | `output/EC_xxx.json`, `trace.jsonl`, `architecture.md` |
| Module phụ thuộc | `multi_agent_system.py` |
| Module sử dụng output | Evaluation Script |
| Điều kiện lỗi cần xử lý | Lỗi vượt quá giới hạn phần tử mảng (array limits), lỗi định dạng schema |

### Cách xác minh

```bash
python multi_agent_system.py
```

- **Kết quả mong đợi:** Hệ thống chạy thành công 50 cases, tạo ra `trace.jsonl` và 50 file JSON trong `output/`.
- **Kết quả thực tế:** 50/50 cases hoàn thành không có lỗi.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn mô hình kiến trúc điều phối giữa Centralized Coordinator vs Peer-to-Peer Agent Chain.
- **Các phương án đã cân nhắc:**
  1. Phương án A (Peer-to-Peer): Agent này gọi trực tiếp Agent tiếp theo trong chuỗi.
  2. Phương án B (Centralized Coordinator): `CoordinatorAgent` quản lý toàn bộ vòng đời và thu thập trace.
- **Phương án đã chọn:** Phương án B.
- **Lý do:** Giúp việc ghi nhật ký `trace.jsonl` diễn ra tập trung, dễ theo dõi và hỗ trợ Verifier Agent kiểm định dữ liệu trước khi hoàn tất ghi file output.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Mảng `evidence_ids` vượt quá giới hạn 20 phần tử khi đơn hàng có nhiều item và payment rows.
- **Cách xử lý:** Thêm logic cắt mảng `evidence_ids = evidence_ids[:20]` trong `VerifierAgent` và `PolicyAgent`.
- **Cách xác minh sau khi sửa:** Chạy lại `validate_outputs.py`, 0 file vi phạm giới hạn mảng.

---

## 7. Hiểu biết về luồng end-to-end

1. Input JSON chứa `claimed_order_id` được tiếp nhận bởi Coordinator Agent.
2. Coordinator Agent gọi các agent dữ liệu (Customer, OrderProduct, Payment, Delivery) để trích xuất bằng chứng từ CSV.
3. Policy Agent tổng hợp bằng chứng, đối chiếu `EC_POLICY_V2` để quyết định phương án hoàn tiền.
4. Verifier Agent kiểm tra tính toàn vẹn của kết quả.
5. Coordinator Agent ghi nhận kết quả ra `output/` và ghi nhật ký A2A vào `trace.jsonl`.

---

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Báo cáo không chứa secret hay API key.

**Họ và tên:** Nguyễn Đàm Kiên  
**Ngày xác nhận:** 2026-08-05
