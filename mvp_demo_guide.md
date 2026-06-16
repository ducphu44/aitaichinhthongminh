# Hướng dẫn quay Video MVP Demo (Kịch bản 3 phút End-to-End)

Tài liệu này cung cấp một kịch bản quay video (Storyboard) chi tiết từng giây giúp bạn giới thiệu trọn vẹn dự án **AI Trợ Lý Tài Chính** trong đúng **3 phút**.

---

## Chuẩn bị trước khi quay
1. **Dọn dẹp dữ liệu**: Đảm bảo cả máy chủ Frontend (Next.js) và Backend (FastAPI) đang chạy ổn định.
2. **File chuẩn bị**: 
   - 1 File Excel bị lỗi cấu trúc (để demo kiểm tra lỗi).
   - 1 File Excel chuẩn chỉnh (ví dụ: `Phong_CNTT_Quan_tri_ngan_sach_day_du.xlsx`).
3. **Công cụ quay màn hình**: Sử dụng OBS, Loom, Camtasia hoặc tính năng quay màn hình mặc định của Mac/Windows.
4. **Giọng nói/Thuyết minh**: Nói to, rõ ràng, tập trung vào giá trị tự động hóa bằng AI.

---

## KỊCH BẢN CHI TIẾT 3 PHÚT

### Phần 1: Giới thiệu & Tổng quan Dashboard (0:00 - 0:30)
* **Hình ảnh trên màn hình**: Trang chủ Dashboard (`http://localhost:3000/dashboard`). Rê chuột qua các biểu đồ tròn, biểu đồ cột và các thẻ KPI.
* **Lời thoại thuyết minh**: 
  > *"Xin chào thầy cô và các bạn, đây là hệ thống AI Trợ Lý Tài Chính & Lập Báo Cáo. Tại trang chủ Dashboard, phòng tài chính có thể theo dõi trực quan tổng dự toán ngân sách, thực chi và tỷ lệ sử dụng ngân sách của các phòng ban theo thời gian thực dựa trên các biểu đồ cột và biểu đồ cơ cấu chi tiêu."*

### Phần 2: Upload Excel & Tự động Kiểm tra Lỗi (0:30 - 1:15)
* **Hình ảnh trên màn hình**: Click chọn **Upload Excel** trên thanh Sidebar.
  1. Chọn **Phòng Đào Tạo** ở Dropdown, tải lên file của phòng Hành chính để hiển thị cảnh báo không khớp màu vàng. Nhấp nút đổi sang phòng Hành chính.
  2. Tải lên file lỗi -> Click **Validate** -> Chỉ vào bảng **Validation Log** màu đỏ chứa chi tiết lỗi dòng nào.
  3. Bấm "Tải file khác" -> Tải file chuẩn -> Click **Validate** (thành công) -> Click **Import** (hiển thị thông báo nạp thành công X dòng) -> Chỉ vào bảng **Lịch sử Upload** vừa được cập nhật.
* **Lời thoại thuyết minh**: 
  > *"Hệ thống hỗ trợ cơ chế nạp dữ liệu thông minh từ Excel. Khi tôi tải lên một file có tên không khớp phòng ban được chọn, hệ thống sẽ cảnh báo ngay lập tức. Nếu tệp Excel có lỗi cấu trúc, tính năng Validate sẽ hiển thị rõ ràng dòng bị lỗi để tránh nạp dữ liệu sai vào DB. Khi file hoàn toàn hợp lệ, tôi chỉ cần ấn nút Import để dữ liệu được đưa thẳng vào cơ sở dữ liệu."*

### Phần 3: Cảnh báo vượt chi tiêu & Alerts (1:15 - 1:45)
* **Hình ảnh trên màn hình**: Click chọn trang **Alerts** trên Sidebar. Cuộn chuột qua danh sách các khoản vượt kế hoạch được tô đỏ/vàng.
* **Lời thoại thuyết minh**: 
  > *"Sau khi dữ liệu được nạp, hệ thống sẽ tự động quét và đưa ra các cảnh báo tức thời tại mục Alerts đối với những khoản đề nghị thanh toán vượt hạn mức dự toán của từng phòng ban, giúp kiểm soát rủi ro tài chính hiệu quả."*

### Phần 4: Trải nghiệm Trợ lý Hỏi đáp AI & SQL Agent (1:45 - 2:30)
* **Hình ảnh trên màn hình**: Quay lại Dashboard, click vào **Nút Chatbot màu xanh** ở góc phải dưới. 
  1. Chọn câu hỏi mẫu *"Tổng ngân sách năm nay là bao nhiêu?"* -> Đợi AI phản hồi số liệu.
  2. Gõ câu hỏi phức tạp hơn: *"Liệt kê danh sách các nhà cung cấp trong hệ thống"* -> Show kết quả bảng dữ liệu Markdown hiển thị cực đẹp trong khung chat. Chỉ vào thẻ tool `execute_sql` được sử dụng dưới câu trả lời.
* **Lời thoại thuyết minh**: 
  > *"Điểm đặc biệt của dự án là Trợ lý AI tích hợp cơ chế SQL Agent. Khi người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên, AI sẽ tự động phân tích cấu trúc Database, sinh câu lệnh SQL chuẩn xác để truy vấn trực tiếp và trả về câu trả lời kèm bảng biểu trực quan ngay lập tức."*

### Phần 5: Tự động Lập Báo cáo Tài Chính & Xuất PDF (2:30 - 3:00)
* **Hình ảnh trên màn hình**: Click chọn trang **Reports** trên Sidebar.
  1. Chọn Năm tài chính -> Nhấp **Generate Report**.
  2. Chờ báo cáo xuất hiện (chứa các phân tích chi tiết của AI).
  3. Bấm nút **Xuất PDF** -> Mở nhanh file PDF vừa tải xuống hiển thị báo cáo chuẩn A4 cực kỳ chuyên nghiệp.
* **Lời thoại thuyết minh**: 
  > *"Cuối cùng, thay vì phải tự viết báo cáo, người dùng chỉ cần chọn năm và bấm Tạo báo cáo. AI sẽ tự động đọc dữ liệu chi tiêu trong năm, viết nhận xét chuyên môn và đưa ra khuyến nghị. Báo cáo này có thể được xuất thành file PDF A4 chuyên nghiệp chỉ với một cú click chuột. Cảm ơn mọi người đã theo dõi!"*
