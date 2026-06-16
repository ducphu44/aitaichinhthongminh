# Hướng dẫn Kiểm thử Thủ công & Tài liệu Minh chứng (Manual Test Cases & Eval Evidences)

Tài liệu này hướng dẫn chi tiết cách thực hiện **5 Test Case kiểm thử thủ công** để thu thập minh chứng đánh giá dự án (Evaluation Evidences) đối với các tính năng cốt lõi.

---

## Mẫu Báo cáo Kết quả Kiểm thử (Test Report Template)

Bạn có thể chụp ảnh màn hình giao diện thực tế tương ứng với từng bước dưới đây để chèn vào báo cáo của mình làm minh chứng (Evidences).

---

### TEST CASE 1: Tải lên tệp Excel có lỗi dữ liệu (Validation Error)
* **Mục tiêu**: Đảm bảo hệ thống phát hiện chính xác các dòng lỗi và hiển thị chi tiết lỗi ở giao diện Log.
* **Các bước thực hiện**:
  1. Truy cập trang **Upload Excel** (`http://localhost:3000/upload`).
  2. Chọn phòng ban bất kỳ ở dropdown (ví dụ: *Phòng CNTT*).
  3. Kéo thả hoặc chọn một file Excel bị lỗi định dạng (ví dụ: thiếu cột bắt buộc, hoặc sai định dạng số tiền, mã code trùng).
  4. Nhấn **"Tải lên máy chủ"**.
  5. Khi nút kiểm tra xuất hiện, nhấn **"Kiểm tra file (Validate)"**.
* **Kết quả thực tế (Output thực tế)**:
  - Hệ thống đổi trạng thái file thành **LỖI (Failed)** màu đỏ.
  - Phần thống kê hiển thị: Dòng lỗi > 0.
  - Bảng **Nhật ký kiểm tra (Validation Log)** hiển thị chi tiết: Cột **Dòng** chỉ rõ dòng bị lỗi, cột **Nội dung lỗi** mô tả chi tiết lỗi (ví dụ: *"Cột 'budget_code' không được để trống"*), và cột **Dữ liệu nguồn** hiển thị dòng dữ liệu thô.
  - Nút **"Nạp vào Database"** hoàn toàn bị ẩn đi.

---

### TEST CASE 2: Tải lên tệp Excel hợp lệ & Nạp dữ liệu thành công (Import Success)
* **Mục tiêu**: Đảm bảo tệp Excel đúng chuẩn được kiểm tra thành công và dữ liệu được nạp vào DB, cập nhật lịch sử.
* **Các bước thực hiện**:
  1. Tại trang **Upload Excel**, nhấn **"Tải file khác"**.
  2. Chọn phòng ban tương ứng (ví dụ: *Phòng CNTT*).
  3. Chọn tệp Excel chuẩn dữ liệu (ví dụ file `Phong_CNTT_Quan_tri_ngan_sach_day_du.xlsx`).
  4. Nhấn **"Tải lên máy chủ"** -> Nhấn **"Kiểm tra file (Validate)"**.
  5. Sau khi kiểm tra thành công, nhấn tiếp nút **"Nạp vào Database (Import)"**.
* **Kết quả thực tế (Output thực tế)**:
  - Sau bước Validate: File hiển thị trạng thái **HỢP LỆ (Validated)** màu xanh lá cây, số dòng lỗi bằng 0. Nút **"Nạp vào Database (Import)"** xuất hiện.
  - Sau khi bấm Import: Xuất hiện hộp thông báo màu xanh lá: *"Đã nạp thành công X dòng dữ liệu vào cơ sở dữ liệu!"*.
  - Bảng **Lịch sử Upload** ở phía dưới tự động cập nhật một dòng mới ghi nhận tên file vừa nạp với trạng thái **Đã nhập DB** kèm số lượng dòng hợp lệ.

---

### TEST CASE 3: Tự động cảnh báo khi chọn sai phòng ban (Department Mismatch)
* **Mục tiêu**: Đảm bảo hệ thống phát hiện sự không khớp giữa phòng ban đã chọn và phòng ban trong tên tệp.
* **Các bước thực hiện**:
  1. Tại trang **Upload Excel**, chọn phòng ban trên Dropdown là **Phòng Đào Tạo**.
  2. Tải lên tệp có tên chứa thông tin phòng ban khác, ví dụ: `Phong_Hanh_Chinh_Quy_1.xlsx`.
* **Kết quả thực tế (Output thực tế)**:
  - Phía trên form xuất hiện một thanh thông báo màu vàng nổi bật với tiêu đề: **"Phát hiện không khớp phòng ban!"**
  - Nội dung cảnh báo rõ ràng: *"File bạn chọn có vẻ thuộc Phòng Hành chính, nhưng bạn đang chọn phòng ban khác..."*
  - Xuất hiện nút **"Đổi sang phòng Hành chính"** màu vàng. Khi click vào nút này, dropdown chọn phòng ban tự động chuyển giá trị về **Phòng Hành chính (HC01)** và thanh cảnh báo biến mất.

---

### TEST CASE 4: Hỏi đáp dữ liệu tài chính với Chatbot nổi trên Dashboard
* **Mục tiêu**: Đảm bảo nút chatbot nổi trên Dashboard hoạt động, tương tác tốt với API và trả về kết quả chính xác.
* **Các bước thực hiện**:
  1. Truy cập trang chủ **Dashboard** (`http://localhost:3000/dashboard`).
  2. Nhấn vào **biểu tượng Chatbot hình tròn màu xanh** ở góc dưới cùng bên phải.
  3. Nhập câu hỏi vào ô chat: `"Tổng dự toán ngân sách năm nay là bao nhiêu?"` và bấm gửi (hoặc click chọn câu hỏi gợi ý nhanh dưới khung chat).
* **Kết quả thực tế (Output thực tế)**:
  - Khung chat hiển thị hiệu ứng *"Đang truy vấn cơ sở dữ liệu..."*.
  - Trợ lý AI trả về câu trả lời hiển thị rõ ràng tổng số tiền (ví dụ: *"Tổng dự toán ngân sách năm nay là 7,265,784,000 ₫"*). 
  - Số liệu trả về trùng khớp hoàn toàn với số liệu hiển thị trên thẻ KPI **"Tổng dự toán ngân sách"** ở phía trên màn hình Dashboard.

---

### TEST CASE 5: Chatbot tự động tạo bảng kết quả truy vấn phức tạp (Markdown Table)
* **Mục tiêu**: Kiểm tra khả năng sinh câu lệnh SQL và hiển thị kết quả dạng bảng dữ liệu của chatbot.
* **Các bước thực hiện**:
  1. Mở cửa sổ chatbot trên Dashboard.
  2. Gõ câu hỏi phức tạp: `"Liệt kê danh sách các nhà cung cấp (vendors) trong hệ thống"` và nhấn gửi.
* **Kết quả thực tế (Output thực tế)**:
  - AI Agent nhận diện câu hỏi, gọi công cụ `execute_sql` để lấy dữ liệu từ bảng `vendors`.
  - Câu trả lời của AI tự động tạo và hiển thị một **Bảng Markdown** cực kỳ đẹp mắt, căn chỉnh lề ngay ngắn gồm các cột: **Tên nhà cung cấp (Vendor Name)**, **Mã số thuế (Tax Code)**, **Địa chỉ**, v.v.
  - Phía dưới bảng hiển thị danh sách các công cụ đã được dùng (ví dụ: thẻ ghi chú nhỏ `execute_sql` màu tím).
