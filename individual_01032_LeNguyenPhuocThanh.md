# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| Họ và tên | Lê Nguyễn Phước Thành |
| MSSV | 2A202601032 |
| Khóa/Lớp | K4 |
| Vai trò chính | Data Agent Developer (Customer Agent & OrderProduct Agent) |
| Ngày hoàn thành | 2026-08-05 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| Customer Agent | `CustomerAgent.analyze()` | `order_id`, `olist_customers_dataset.csv` | `customer_unique_id`, `related_order_ids`, `repeat_customer` | Hoàn thành |
| Order & Product Agent | `OrderProductAgent.analyze()` | `order_id`, item/product CSVs | `item_ids`, `seller_ids`, `product_ids`, `category_names` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| Tích hợp ngành hàng | Lê Kim Tính (Logistics/Delivery) | Cung cấp danh sách `seller_id` chuẩn để kiểm tra SLA bàn giao |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Truy vết lịch sử khách hàng | `CustomerAgent` | Tìm kiếm các order khác cùng `customer_unique_id` | Test case `repeat_customer` |
| Bóc tách dữ liệu sản phẩm | `OrderProductAgent` | Trích xuất ngành hàng từ `olist_products_dataset.csv` | Output JSON `product_context` |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Một khách hàng trong Olist được định danh qua `customer_id` theo từng đơn hàng. Để nhận diện khách hàng quay lại (`repeat_customer`), phải join qua `customer_unique_id`. Đồng thời, một đơn hàng có thể có nhiều mặt hàng, nhiều seller và nhiều ngành hàng khác nhau.

### Cách triển khai

- `CustomerAgent`: Dùng `customer_id` để lấy `customer_unique_id`, sau đó tra cứu tất cả đơn hàng thuộc `customer_unique_id` đó để lấy danh sách `related_order_ids` (tối đa 5 đơn).
- `OrderProductAgent`: Trích xuất danh sách `order_item_id`, `seller_id`, `product_id` và tra cứu danh mục ngành hàng từ `olist_products_dataset.csv`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Xử lý danh mục ngành hàng bị thiếu (`NaN`) trong file sản phẩm.
- **Phương án đã chọn:** Bỏ qua các giá trị `NaN`, chỉ giữ lại các ngành hàng hợp lệ và duy nhất (unique), tối đa 5 ngành hàng.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Cột `product_category_name` trả về dạng float `nan` làm lỗi hàm ghép chuỗi.
- **Cách xử lý:** Thêm câu lệnh kiểm tra `not pd.isna(p_row.iloc[0]['product_category_name'])`.

---

## 7. Hiểu biết về luồng end-to-end

Customer Agent và OrderProduct Agent đóng vai trò thu thập thông tin gốc về khách hàng và sản phẩm từ các bảng CSV, tạo tiền đề dữ liệu cho Payment Agent và Policy Agent phân tích.

---

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.

**Họ và tên:** Lê Nguyễn Phước Thành  
**Ngày xác nhận:** 2026-08-05

<!-- Last verified by Le Nguyen Phuoc Thanh -->

<!-- Verified by Le Nguyen Phuoc Thanh (01032) at 2026-08-05 15:29:59 -->

<!-- Latest update by Le Nguyen Phuoc Thanh (01032) at 2026-08-05 16:11:08 -->
