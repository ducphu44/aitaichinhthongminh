# User Flow: AI Financial Analyst Assistant

Tài liệu này mô tả chi tiết hành trình sử dụng hệ thống của 4 nhóm vai trò chính: **Admin**, **Finance Staff**, **Finance Manager**, và **Leader**.

## Luồng hệ thống chung (Core Flow)
`Login` → `Upload Data` → `Dashboard` → `AI Assistant` → `Generate Report` → `Review/Approve Report`

---

## 1. Vai trò: Finance Staff (Nhân viên tài chính)
*Nhiệm vụ chính: Cập nhật dữ liệu, theo dõi cảnh báo và tạo báo cáo nháp.*

1. **Login:** Đăng nhập vào hệ thống.
2. **Upload Data:** Tải file Excel/CSV báo cáo thu chi lên hệ thống. Hệ thống tự động kiểm tra định dạng và chuẩn hóa dữ liệu.
3. **Dashboard:** Xem bảng điều khiển để nắm bắt tổng quan, kiểm tra xem số liệu vừa upload có khớp với thực tế không. Xem các cảnh báo vượt ngân sách.
4. **AI Assistant:** Truy cập trợ lý AI để đặt câu hỏi phân tích dữ liệu (ví dụ: "Tại sao phòng Marketing lại vượt ngân sách?").
5. **Generate Report:** Vào trang Reports để yêu cầu AI tạo báo cáo tài chính nháp theo tháng/quý. Báo cáo được tạo sẽ ở trạng thái `draft`.

## 2. Vai trò: Finance Manager (Trưởng phòng tài chính)
*Nhiệm vụ chính: Giám sát ngân sách, kiểm tra và phê duyệt các báo cáo nháp.*

1. **Login:** Đăng nhập vào hệ thống.
2. **Dashboard:** Xem tổng quan ngân sách và chú ý đến các cảnh báo rủi ro cao (over-budget, unusual-increase).
3. **AI Assistant:** Dùng AI để phân tích sâu hơn về các khoản chi bất thường trước khi đưa ra quyết định.
4. **Review/Approve Report:**
   - Vào trang Reports để đọc các báo cáo `draft` do nhân viên tạo.
   - Nếu số liệu chính xác: Nhấn `Approve` (Báo cáo chuyển sang trạng thái `approved` và hiển thị cho Leader).
   - Nếu số liệu sai: Nhấn `Reject` hoặc yêu cầu chỉnh sửa lại (Báo cáo quay về trạng thái `rejected`).

## 3. Vai trò: Leader (Ban lãnh đạo)
*Nhiệm vụ chính: Xem báo cáo đã được phê duyệt để nắm bắt tình hình tài chính.*

1. **Login:** Đăng nhập vào hệ thống.
2. **Dashboard:** Xem tổng quan các chỉ số tài chính cốt lõi (tổng thu, tổng chi, tỷ lệ sử dụng ngân sách).
3. **Reports:** Chỉ xem được các báo cáo có trạng thái `approved`. Đọc để đưa ra các quyết định chiến lược hoặc điều chỉnh ngân sách cho tháng sau.

## 4. Vai trò: Admin (Quản trị viên)
*Nhiệm vụ chính: Quản trị hệ thống và người dùng.*

1. **Login:** Đăng nhập vào hệ thống.
2. **User Management:**
   - Xem danh sách toàn bộ người dùng trong hệ thống.
   - Thêm tài khoản mới và gán vai trò (`role`).
   - Khóa hoặc mở khóa tài khoản người dùng nếu cần thiết.
3. *Admin có quyền truy cập vào tất cả các trang khác để kiểm tra hệ thống.*
