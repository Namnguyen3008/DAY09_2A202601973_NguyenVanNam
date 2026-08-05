# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| Họ và tên | Nguyễn Văn Nam |
| MSSV | 2A202601973 |
| Khóa/Lớp | K4 |
| Vai trò chính | Multi-Agent Architecture & Business Policy Engine Developer |
| Ngày hoàn thành | 2026-08-05 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| Multi-Agent Orchestrator Framework | `multi_agent_system.py` / `CoordinatorAgent` | `input/EC_*.json`, `data/*.csv` | Output JSON 50 cases, `trace.jsonl`, `metadata.json` | Hoàn thành |
| Business Policy Engine | `PolicyAgent.analyze()` | Agent handoff payloads | `primary_issue`, `secondary_issues`, `root_cause`, `refund` | Hoàn thành |
| Schema Verifier & Audit | `VerifierAgent.verify()` | Output draft dictionary | Structural verification pass/fail status | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Tích hợp luồng logging | Logging Module | Tạo ra định dạng JSONL tiêu chuẩn cho `trace.jsonl` ghi nhận lịch sử tương tác A2A |
| Kiểm thử và Validation | QA & Audit Module | Xây dựng script `validate_outputs.py` kiểm tra tự động 50 file JSON đầu ra |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Triển khai 7 Agent chuyên biệt | `multi_agent_system.py` | Framework 7 agents (Customer, OrderProduct, Payment, Delivery, Policy, Verifier, Coordinator) | Python runtime output & `trace.jsonl` |
| Xây dựng tài liệu kiến trúc | `architecture.md` | Sơ đồ hệ thống, vai trò, ma trận quyền truy cập dữ liệu và luồng handoff | File `architecture.md` tại root repo |
| Chạy batch & sinh 50 JSON | `output/EC_001.json` -> `output/EC_050.json` | 50 file JSON kết quả theo đúng chuẩn `EC_POLICY_V2` | `python validate_outputs.py` |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Trong xử lý khiếu nại thương mại điện tử, một đơn hàng khiếu nại có thể chứa nhiều bất đồng dữ liệu (trễ giao hàng, trễ bàn giao seller, sai lệch thanh toán, đơn hủy sau khi thanh toán, đơn nhiều seller/nhiều sản phẩm). Cần có một hệ thống phân công chuyên biệt cho từng domain dữ liệu (Khách hàng, Đơn hàng/Sản phẩm, Thanh toán, Vận chuyển) và một Policy Agent tổng hợp đưa ra kết luận công bằng, chính xác theo đúng quy tắc kinh doanh.

### Cách triển khai

Hệ thống được thiết kế dưới dạng 7 sub-agents:
1. `CustomerAgent`: Truy vấn lịch sử `customer_unique_id`, các đơn hàng liên quan để nhận diện khách hàng thân thiết (`repeat_customer`).
2. `OrderProductAgent`: Trích xuất thông tin các item, sản phẩm, ngành hàng và nhận diện đơn nhiều item, nhiều seller, nhiều category.
3. `PaymentAgent`: Tính tổng tiền thanh toán (`order_payments`), tổng giá trị đơn (`price + freight`) và kiểm tra điều kiện đối soát `abs(difference) <= 0.10 BRL`.
4. `DeliveryAgent`: Phân tích SLA giao hàng (`delivered_at - estimated_at`) và SLA bàn giao của seller (`carrier_handoff_at - shipping_limit_at`).
5. `PolicyAgent`: Đánh giá 6 quy tắc `EC_POLICY_V2` theo thứ tự ưu tiên nghiêm ngặt (1. Canceled paid -> 2. Unavailable paid -> 3. Late seller -> 4. Late logistics -> 5. Valid split payment -> 6. Unsupported late claim).
6. `VerifierAgent`: Kiểm định độ dài mảng (max 5 order, item, payment, product, category; max 3 seller, root cause, responsible party; max 20 evidence), kiểu dữ liệu và null handling.
7. `CoordinatorAgent`: Điều phối luồng làm việc, ghi nhận nhật ký A2A vào `trace.jsonl` và ghi nhận file output.

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| Input | JSON case request (`input/EC_xxx.json`) & Olist CSV datasets |
| Output | Output JSON (`output/EC_xxx.json`), `trace.jsonl`, `metadata.json` |
| Module phụ thuộc | `pandas`, `json`, `datetime` |
| Module sử dụng output | Automated Evaluator / Leaderboard Scoring |
| Điều kiện lỗi cần xử lý | Đơn hàng không có item row (`unavailable`), thời gian giao hàng thiếu/null, sai số làm tròn số tiền |

### Cách xác minh

```bash
python multi_agent_system.py
python validate_outputs.py
```

- **Kết quả mong đợi:** 50 file JSON được tạo ra thành công, tất cả kiểm tra validation đều đạt status PASS.
- **Kết quả thực tế:** 50/50 cases xử lý thành công, 0 lỗi validation, `trace.jsonl` ghi nhận đủ các bước handoff.
- **Artifact/log:** `output/EC_*.json`, `trace.jsonl`, `metadata.json`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Xử lý trường hợp đơn hàng trạng thái `unavailable` không có dòng thông tin item nào trong `olist_order_items_dataset.csv`.
- **Các phương án đã cân nhắc:**
  1. Phương án A: Trả về giá trị 0.0 cho `item_total_brl`, `freight_total_brl`, `expected_total_brl`, `difference_brl` và `False` cho `reconciled`.
  2. Phương án B (Áp dụng): Đặt `item_total_brl`, `freight_total_brl`, `expected_total_brl`, `difference_brl`, `reconciled` thành `null` (`None`), đồng thời để các mảng item, seller, product, category, seller handoff thành mảng rỗng `[]`.
- **Phương án đã chọn:** Phương án B.
- **Lý do:** Đảm bảo tính chính xác theo đúng quy tắc nghiệp vụ trong `README.md` Section 4: *"Với order không có item row, expected_total_brl, difference_brl và reconciled phải là null; item, seller, product, category và seller handoff để mảng rỗng."*
- **Bằng chứng quyết định phù hợp:** Kiểm thử trên các case `unavailable` (như `EC_012`, `EC_031`, `EC_033`, `EC_034`, `EC_035`, `EC_043`) thu được định dạng schema khớp 100% yêu cầu đề bài.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version.`
- **Lệnh hoặc bước tái hiện:** `python multi_agent_system.py`
- **Nguyên nhân gốc:** Hàm `datetime.utcnow()` trong Python 3.12 bị deprecated, cần sử dụng timezone-aware object `datetime.now(timezone.utc)`.
- **Cách xử lý:** Cập nhật import `from datetime import datetime, timezone` và thay thế `datetime.utcnow()` bằng `datetime.now(timezone.utc)`.
- **Cách xác minh sau khi sửa:** Chạy lại `python multi_agent_system.py`, cảnh báo biến mất hoàn toàn và timestamp vẫn đạt chuẩn ISO 8601 UTC string (`YYYY-MM-DDTHH:MM:SSZ`).

---

## 7. Hiểu biết về luồng end-to-end

1. Dữ liệu từ yêu cầu khiếu nại (`input/EC_xxx.json`) chứa `claimed_order_id` được truyền vào Coordinator Agent để khởi tạo phiên làm việc.
2. Coordinator Agent phân công nhiệm vụ cho Customer Agent, OrderProduct Agent, Payment Agent và Delivery Agent thu thập bằng chứng từ các file CSV dữ liệu nguồn Olist.
3. Thông tin từ các agent được handoff đến Policy Agent để đối chiếu với tập quy tắc ưu tiên trong `EC_POLICY_V2`, xác định nguyên nhân gốc, trách nhiệm thuộc về ai (Seller, Carrier, hay Platform) và số tiền hoàn phí.
4. Mọi thông tin được chuyển qua Verifier Agent để kiểm tra các giới hạn số lượng phần tử mảng, tính hợp lệ của evidence ID và kiểu dữ liệu trước khi hoàn tất JSON.
5. Coordinator Agent xuất kết quả ra thư mục `output/`, đồng thời lưu lại trace tương tác A2A trong `trace.jsonl` và khai báo thông số mô hình trong `metadata.json`.

---

## 8. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Văn Nam  
**Ngày xác nhận:** 2026-08-05

<!-- Last verified by Nguyen Van Nam -->
