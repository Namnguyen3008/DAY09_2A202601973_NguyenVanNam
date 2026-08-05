# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| Họ và tên | Lê Kim Tính |
| MSSV | 2A202601560 |
| Khóa/Lớp | K4 |
| Vai trò chính | Logistics & Payment Agent Developer (Payment Agent & Delivery Agent) |
| Ngày hoàn thành | 2026-08-05 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| Payment Agent | `PaymentAgent.analyze()` | `order_id`, payments CSV | `payment_total_brl`, `expected_total_brl`, `reconciled` | Hoàn thành |
| Delivery Agent | `DeliveryAgent.analyze()` | `order_id`, orders CSV | `delivery_variance_hours`, `late_handoff_seller_ids` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Kiểm tra tài chính | Nguyễn Văn Nam (Policy Agent) | Cung cấp dữ liệu cước phí vận chuyển `freight_total_brl` chuẩn xác |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Đối soát tài chính | `PaymentAgent` | So sánh tổng payment với (item + freight) trong sai số 0.10 BRL | Case `valid_split_payment` |
| Phân tích SLA Logistics | `DeliveryAgent` | Tính toán chính xác thời gian trễ giao hàng và trễ bàn giao seller | `delivery_analysis` output |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Cần tính toán chênh lệch thời gian giao hàng thực tế so với thời gian dự kiến (`delivery_variance_hours`), kiểm tra thời điểm seller bàn giao hàng cho đơn vị vận chuyển (`shipping_limit_date` vs `carrier_handoff_date`), và tính tổng tiền thanh toán để đối soát với sai số <= 0.10 BRL.

### Cách triển khai

- `PaymentAgent`: Tính tổng `payment_value` của tất cả các dòng thanh toán, tính `expected_total_brl = sum(price) + sum(freight)`, kiểm tra điều kiện `abs(payment_total - expected_total) <= 0.10`.
- `DeliveryAgent`: Chuyển đổi timestamp thành đối tượng `datetime`, tính chênh lệch giờ `(delivered_customer_date - estimated_delivery_date)`. Đối với từng seller, lấy `shipping_limit_date` sớm nhất và so sánh với `delivered_carrier_date`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Quy đổi thời gian trễ ra số giờ (`hours`).
- **Phương án đã chọn:** Sử dụng công thức `(d1 - d2).total_seconds() / 3600.0` và làm tròn 2 chữ số thập phân (`round(val, 2)`).

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Đơn hàng không có ngày giao hàng thực tế (`order_delivered_customer_date` bị null) làm phát sinh ngoại lệ `strptime`.
- **Cách xử lý:** Trả về `None` (`null`) cho `delivery_variance_hours` khi dữ liệu timestamp bị missing.

---

## 7. Hiểu biết về luồng end-to-end

Payment Agent và Delivery Agent cung cấp 2 trụ cột bằng chứng quan trọng nhất (Tài chính & Logistics) giúp Policy Agent đưa ra phán quyết hoàn tiền đúng đắn.

---

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.

**Họ và tên:** Lê Kim Tính  
**Ngày xác nhận:** 2026-08-05

<!-- Last verified by Le Kim Tinh -->
