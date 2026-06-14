# PRD DỰ ÁN

# AI Trợ lý phân tích tài chính và lập báo cáo cho phòng tài chính

## 1. Tổng quan sản phẩm

AI Trợ lý phân tích tài chính và lập báo cáo cho phòng tài chính là một ứng dụng web hỗ trợ phòng tài chính của trường đại học tổng hợp, phân tích và báo cáo dữ liệu tài chính.

Hệ thống cho phép người dùng tải dữ liệu từ file Excel hoặc CSV, tự động xử lý dữ liệu, hiển thị dashboard, phát hiện khoản chi vượt ngân sách, hỗ trợ hỏi đáp bằng AI và tạo báo cáo tài chính nháp.

Sản phẩm tập trung vào việc hỗ trợ ra quyết định dựa trên dữ liệu, không thay thế vai trò kiểm tra và phê duyệt của nhân viên tài chính hoặc quản lý tài chính.

## 2. Mục tiêu sản phẩm

### 2.1. Mục tiêu tổng quát

Xây dựng một ứng dụng web hoàn chỉnh, có thể triển khai trực tuyến, giúp phòng tài chính phân tích dữ liệu thu, chi, ngân sách và dòng tiền, đồng thời hỗ trợ tạo báo cáo tài chính điều hành bằng AI.

### 2.2. Mục tiêu cụ thể

1. Cho phép người dùng đăng nhập và sử dụng hệ thống theo vai trò.
2. Cho phép tải dữ liệu tài chính từ file Excel hoặc CSV.
3. Tự động kiểm tra, chuẩn hóa và lưu dữ liệu tài chính.
4. Hiển thị dashboard tài chính với các chỉ số quan trọng.
5. Phân tích chênh lệch giữa ngân sách và số tiền thực tế.
6. Cảnh báo khoản chi vượt ngân sách hoặc biến động bất thường.
7. Cho phép người dùng hỏi AI về dữ liệu tài chính.
8. Tạo báo cáo tài chính nháp theo tháng hoặc quý.
9. Cho phép trưởng phòng tài chính kiểm tra và phê duyệt báo cáo.
10. Quản lý người dùng và phân quyền cơ bản.

## 3. Người dùng mục tiêu

### 3.1. Nhân viên phòng tài chính

Nhu cầu chính:

1. Upload dữ liệu tài chính.
2. Kiểm tra dữ liệu sau khi upload.
3. Xem dashboard tài chính.
4. Phát hiện khoản vượt ngân sách.
5. Tạo báo cáo nháp.

Quyền chính:

1. Upload dữ liệu.
2. Xem dashboard.
3. Hỏi AI.
4. Tạo báo cáo nháp.

### 3.2. Trưởng phòng tài chính

Nhu cầu chính:

1. Theo dõi tình hình ngân sách.
2. Xem cảnh báo tài chính.
3. Kiểm tra báo cáo nháp.
4. Phê duyệt hoặc yêu cầu chỉnh sửa báo cáo.

Quyền chính:

1. Xem dashboard.
2. Xem cảnh báo.
3. Hỏi AI.
4. Duyệt hoặc từ chối báo cáo.

### 3.3. Ban lãnh đạo

Nhu cầu chính:

1. Xem tổng quan tình hình tài chính.
2. Đọc báo cáo đã được phê duyệt.
3. Nắm nhanh các điểm cần chú ý.

Quyền chính:

1. Xem dashboard tổng quan.
2. Xem báo cáo đã phê duyệt.

### 3.4. Quản trị viên hệ thống

Nhu cầu chính:

1. Quản lý tài khoản.
2. Gán vai trò người dùng.
3. Khóa hoặc mở tài khoản.

Quyền chính:

1. Quản lý người dùng.
2. Xem toàn bộ hệ thống.
3. Cấu hình quyền truy cập.

## 4. Phạm vi MVP

### 4.1. Trong phạm vi MVP

1. Đăng nhập.
2. Phân quyền cơ bản.
3. Upload file Excel hoặc CSV.
4. Kiểm tra định dạng file.
5. Lưu dữ liệu tài chính vào database.
6. Dashboard tài chính.
7. Phân tích ngân sách và chi thực tế.
8. Cảnh báo vượt ngân sách.
9. Cảnh báo biến động bất thường theo quy tắc.
10. AI hỏi đáp dữ liệu tài chính.
11. Tạo báo cáo tài chính nháp.
12. Phê duyệt hoặc từ chối báo cáo.
13. Quản lý người dùng cơ bản.
14. Triển khai trực tuyến.

### 4.2. Ngoài phạm vi MVP

1. Kết nối hệ thống kế toán thật.
2. Tích hợp ngân hàng.
3. Ký số.
4. Dự báo tài chính dài hạn bằng mô hình phức tạp.
5. Quy trình phê duyệt nhiều cấp.
6. Kiểm toán nội bộ tự động.
7. Tự động gửi báo cáo chính thức cho lãnh đạo khi chưa được kiểm tra.
8. Sử dụng dữ liệu tài chính thật trong bản demo.

## 5. Yêu cầu chức năng

### 5.1. Đăng nhập và phân quyền

Mô tả:

Người dùng có thể đăng nhập bằng email và mật khẩu. Sau khi đăng nhập, hệ thống hiển thị menu và chức năng phù hợp với vai trò của người dùng.

Vai trò người dùng:

1. admin
2. finance_staff
3. finance_manager
4. leader

Acceptance criteria:

1. Người dùng đăng nhập được bằng tài khoản hợp lệ.
2. Người dùng không đăng nhập được nếu sai email hoặc mật khẩu.
3. Người dùng chỉ nhìn thấy menu phù hợp với vai trò.
4. API nội bộ bị chặn nếu không có token hợp lệ.
5. Người dùng có thể logout.

### 5.2. Upload dữ liệu tài chính

Mô tả:

Nhân viên tài chính có thể upload file Excel hoặc CSV. Hệ thống kiểm tra định dạng file, kiểm tra cột bắt buộc, đọc dữ liệu, chuẩn hóa dữ liệu và lưu vào database.

Cột dữ liệu bắt buộc:

1. transaction_id
2. date
3. month
4. department
5. category
6. transaction_type
7. budget_amount
8. actual_amount
9. description

Acceptance criteria:

1. Upload được file CSV.
2. Upload được file Excel.
3. Hệ thống báo lỗi nếu file sai định dạng.
4. Hệ thống báo lỗi nếu thiếu cột bắt buộc.
5. Hệ thống hiển thị preview dữ liệu.
6. Dữ liệu hợp lệ được lưu vào database.
7. Hệ thống trả về số dòng đã import và số cảnh báo phát hiện được.

### 5.3. Dashboard tài chính

Mô tả:

Dashboard hiển thị tình hình tài chính tổng quan dựa trên dữ liệu đã upload.

Chỉ số cần hiển thị:

1. Tổng thu.
2. Tổng chi.
3. Tổng ngân sách.
4. Ngân sách đã sử dụng.
5. Ngân sách còn lại.
6. Tỷ lệ sử dụng ngân sách.
7. Số cảnh báo.
8. Đơn vị có tổng chi cao nhất.
9. Khoản mục vượt ngân sách nhiều nhất.

Thành phần giao diện:

1. KPI cards.
2. Biểu đồ thu chi theo tháng.
3. Biểu đồ chi phí theo phòng ban.
4. Bảng khoản vượt ngân sách.
5. Danh sách cảnh báo bất thường.
6. Bộ lọc theo tháng và phòng ban.

Acceptance criteria:

1. Dashboard hiển thị dữ liệu từ database.
2. Số liệu tổng thu và tổng chi được tính đúng.
3. Biểu đồ hiển thị được xu hướng theo tháng.
4. Bảng vượt ngân sách hiển thị đúng các khoản có actual_amount lớn hơn budget_amount.
5. Bộ lọc tháng và phòng ban hoạt động.

### 5.4. Phân tích chênh lệch ngân sách

Mô tả:

Hệ thống tự động tính chênh lệch giữa ngân sách và số tiền thực tế.

Công thức:

variance_amount = actual_amount trừ budget_amount

variance_percent = variance_amount chia budget_amount nhân 100

Quy tắc trạng thái:

1. normal nếu chưa phát hiện vấn đề.
2. over_budget nếu actual_amount lớn hơn budget_amount.
3. unusual nếu variance_percent lớn hơn 20%.

Acceptance criteria:

1. Hệ thống tính đúng variance_amount.
2. Hệ thống tính đúng variance_percent.
3. Hệ thống gắn trạng thái đúng cho từng giao dịch.
4. Kết quả được lưu vào database.

### 5.5. Cảnh báo bất thường

Mô tả:

Hệ thống phát hiện các tình huống cần chú ý dựa trên quy tắc đơn giản.

Loại cảnh báo:

1. over_budget: chi thực tế vượt ngân sách.
2. high_variance: tỷ lệ chênh lệch lớn hơn 20%.
3. unusual_increase: chi phí tăng hơn 20% so với tháng trước.
4. fast_budget_usage: tỷ lệ sử dụng ngân sách lớn hơn 80%.

Mức độ cảnh báo:

1. low
2. medium
3. high

Acceptance criteria:

1. Cảnh báo được tạo sau khi upload dữ liệu.
2. Dashboard hiển thị danh sách cảnh báo.
3. Người dùng có quyền phù hợp có thể đánh dấu cảnh báo là đã xử lý.
4. Cảnh báo được lưu trong database.

### 5.6. AI hỏi đáp dữ liệu tài chính

Mô tả:

Người dùng có thể hỏi hệ thống bằng ngôn ngữ tự nhiên. Backend lấy dữ liệu liên quan từ database trước, sau đó AI diễn giải kết quả.

Ví dụ câu hỏi:

1. Khoản mục nào vượt ngân sách nhiều nhất?
2. Đơn vị nào có tổng chi cao nhất?
3. Chi phí nào tăng bất thường trong tháng này?
4. Tóm tắt tình hình tài chính quý này.
5. Những điểm nào cần lãnh đạo lưu ý?

Nguyên tắc:

1. AI không được tự bịa số liệu.
2. AI chỉ trả lời dựa trên dữ liệu đã có.
3. Nếu không có dữ liệu, AI phải nói rõ chưa có dữ liệu phù hợp.
4. Câu trả lời cần có ghi chú rằng người dùng cần kiểm tra lại.

Acceptance criteria:

1. Người dùng nhập được câu hỏi.
2. AI trả lời dựa trên dữ liệu trong database.
3. Câu trả lời có số liệu nếu dữ liệu có.
4. Lịch sử hỏi đáp được lưu.
5. Có cảnh báo cần kiểm tra lại câu trả lời.

### 5.7. Tạo báo cáo tài chính nháp

Mô tả:

Người dùng có thể tạo báo cáo tài chính nháp theo tháng hoặc quý. Báo cáo được tạo dựa trên KPI, xu hướng, cảnh báo và các khoản vượt ngân sách.

Cấu trúc báo cáo:

1. Tóm tắt tổng quan.
2. Tình hình thu chi.
3. Tình hình sử dụng ngân sách.
4. Các khoản vượt ngân sách.
5. Biến động bất thường.
6. Điểm cần lãnh đạo lưu ý.
7. Ghi chú kiểm chứng.

Trạng thái báo cáo:

1. draft
2. reviewed
3. approved
4. rejected

Acceptance criteria:

1. Người dùng tạo được báo cáo nháp.
2. Báo cáo được lưu vào database.
3. Trưởng phòng tài chính có thể approve hoặc reject.
4. Ban lãnh đạo chỉ xem báo cáo đã approved.
5. Báo cáo có ghi chú cần kiểm tra trước khi sử dụng.

### 5.8. Quản lý người dùng

Mô tả:

Admin có thể xem danh sách người dùng, thêm người dùng, chỉnh sửa vai trò và khóa tài khoản.

Acceptance criteria:

1. Admin xem được danh sách người dùng.
2. Admin thêm được người dùng.
3. Admin cập nhật được vai trò.
4. Admin khóa hoặc mở tài khoản.
5. Người dùng không phải admin không truy cập được trang quản lý người dùng.

## 6. Yêu cầu phi chức năng

### 6.1. Giao diện

1. Giao diện rõ ràng, dễ sử dụng.
2. Có bố cục phù hợp với người dùng phòng tài chính.
3. Có trạng thái loading khi hệ thống xử lý.
4. Có thông báo lỗi rõ ràng.
5. Có trạng thái khi chưa có dữ liệu.
6. Có thể sử dụng trên màn hình laptop.

### 6.2. Bảo mật

1. Có đăng nhập.
2. Có phân quyền theo vai trò.
3. Không hiển thị chức năng không đúng quyền.
4. Không dùng dữ liệu tài chính thật trong demo.
5. Không để AI tự ý thay đổi dữ liệu gốc.
6. Có cảnh báo người dùng kiểm tra kết quả AI.

### 6.3. Hiệu năng

1. Hệ thống xử lý được file mẫu khoảng 200 đến 500 dòng.
2. Dashboard tải trong thời gian chấp nhận được cho bản demo.
3. API trả kết quả ổn định khi dùng dữ liệu mẫu.

### 6.4. Khả năng triển khai

1. Frontend được triển khai trực tuyến.
2. Backend được triển khai trực tuyến.
3. Có đường dẫn truy cập sản phẩm.
4. Có tài khoản demo cho từng vai trò.

## 7. Kiến trúc hệ thống đề xuất

### 7.1. Frontend

Công nghệ đề xuất:

1. Next.js.
2. TypeScript.
3. Tailwind CSS.
4. Recharts hoặc Chart.js.

Trang chính:

1. Login.
2. Dashboard.
3. Upload Data.
4. AI Assistant.
5. Reports.
6. User Management.

### 7.2. Backend

Công nghệ đề xuất:

1. FastAPI.
2. Python.
3. pandas.
4. openpyxl.
5. SQLAlchemy.
6. JWT authentication.

Nhóm API chính:

1. Auth API.
2. User API.
3. File Upload API.
4. Dashboard API.
5. Alert API.
6. AI API.
7. Report API.

### 7.3. Database

Công nghệ đề xuất:

SQLite cho MVP demo. PostgreSQL nếu triển khai nghiêm túc hơn.

Bảng dữ liệu chính:

1. users.
2. uploaded_files.
3. financial_transactions.
4. financial_alerts.
5. ai_queries.
6. reports.

## 8. Luồng sử dụng chính

### 8.1. Luồng upload và phân tích dữ liệu

1. Người dùng đăng nhập.
2. Nhân viên tài chính vào trang Upload Data.
3. Người dùng chọn file CSV hoặc Excel.
4. Hệ thống kiểm tra định dạng và cột bắt buộc.
5. Hệ thống đọc dữ liệu.
6. Hệ thống tính chênh lệch ngân sách.
7. Hệ thống tạo cảnh báo nếu có bất thường.
8. Dữ liệu được lưu vào database.
9. Người dùng chuyển sang Dashboard để xem kết quả.

### 8.2. Luồng hỏi AI

1. Người dùng vào trang AI Assistant.
2. Người dùng nhập câu hỏi.
3. Backend xác định dữ liệu liên quan.
4. Backend lấy số liệu từ database.
5. AI diễn giải kết quả.
6. Câu trả lời hiển thị trên giao diện.
7. Lịch sử hỏi đáp được lưu lại.

### 8.3. Luồng tạo báo cáo

1. Người dùng vào trang Reports.
2. Người dùng chọn tháng hoặc quý.
3. Người dùng bấm Generate Report.
4. Backend lấy KPI, xu hướng và cảnh báo.
5. AI tạo báo cáo nháp.
6. Báo cáo được lưu với trạng thái draft.
7. Trưởng phòng tài chính kiểm tra.
8. Báo cáo được approved hoặc rejected.
9. Ban lãnh đạo xem báo cáo đã approved.

## 9. Dữ liệu mẫu

File dữ liệu mẫu cần có khoảng 200 dòng dữ liệu giả lập.

Cột bắt buộc:

1. transaction_id
2. date
3. month
4. department
5. category
6. transaction_type
7. budget_amount
8. actual_amount
9. description

Yêu cầu dữ liệu:

1. Có dữ liệu trong ít nhất 6 tháng.
2. Có ít nhất 5 phòng ban.
3. Có ít nhất 6 khoản mục tài chính.
4. Có giao dịch thu và chi.
5. Có một số khoản vượt ngân sách.
6. Có một số khoản tăng bất thường để demo cảnh báo.

## 10. API đề xuất

### 10.1. Auth

POST /auth/login

GET /auth/me

### 10.2. Users

GET /users

POST /users

PUT /users/{user_id}

DELETE /users/{user_id}

### 10.3. Files

POST /files/upload

GET /files

GET /files/{file_id}

### 10.4. Dashboard

GET /dashboard/summary

GET /dashboard/monthly-trend

GET /dashboard/department-expense

GET /dashboard/over-budget

### 10.5. Alerts

GET /alerts

POST /alerts/{alert_id}/resolve

### 10.6. AI

POST /ai/ask

POST /ai/generate-report

### 10.7. Reports

GET /reports

GET /reports/{report_id}

POST /reports/{report_id}/approve

POST /reports/{report_id}/reject

## 11. Tiêu chí nghiệm thu MVP

1. Người dùng đăng nhập được bằng tài khoản demo.
2. Mỗi vai trò có menu và quyền phù hợp.
3. Người dùng upload được file CSV hoặc Excel.
4. Hệ thống kiểm tra được file sai định dạng hoặc thiếu cột.
5. Dữ liệu tài chính được lưu vào database.
6. Dashboard hiển thị các KPI chính.
7. Dashboard có biểu đồ và bảng vượt ngân sách.
8. Hệ thống tạo được cảnh báo tài chính.
9. Người dùng hỏi được AI về dữ liệu tài chính.
10. AI trả lời dựa trên dữ liệu đã có.
11. Người dùng tạo được báo cáo tài chính nháp.
12. Trưởng phòng tài chính phê duyệt hoặc từ chối báo cáo.
13. Ban lãnh đạo xem được báo cáo đã phê duyệt.
14. Admin quản lý được người dùng.
15. Web app được triển khai trực tuyến và có URL truy cập.

## 12. Yêu cầu nộp bài

1. Link web app đã triển khai trực tuyến.
2. Tài khoản demo cho các vai trò.
3. Link GitHub hoặc kho mã nguồn.
4. File dữ liệu tài chính mẫu.
5. README hướng dẫn cài đặt và sử dụng.
6. Slide trình bày sản phẩm.
7. Video demo luồng sử dụng chính.
8. Kịch bản demo 3 đến 5 phút.
9. Danh sách chức năng đã hoàn thành.
10. Danh sách hạn chế của MVP.
11. Mô tả cơ chế kiểm soát AI và kiểm chứng số liệu.

## 13. Rủi ro và cách kiểm soát

| Rủi ro | Cách kiểm soát |
|---|---|
| AI trả lời sai số liệu | Backend phải lấy số liệu từ database trước, AI chỉ diễn giải dữ liệu đã được cung cấp |
| Người dùng tin tuyệt đối vào báo cáo AI | Báo cáo luôn có trạng thái draft và ghi chú cần kiểm tra trước khi sử dụng |
| Dữ liệu tài chính nhạy cảm bị lộ | Chỉ dùng dữ liệu giả lập trong demo, có đăng nhập và phân quyền |
| Sản phẩm quá rộng, không kịp hoàn thành | Tập trung vào luồng chính: đăng nhập, upload dữ liệu, dashboard, cảnh báo, hỏi AI và tạo báo cáo nháp |

## 14. Kết luận

MVP của sản phẩm cần chứng minh được một luồng sử dụng hoàn chỉnh: người dùng đăng nhập, upload dữ liệu tài chính, xem dashboard, phát hiện khoản vượt ngân sách, hỏi AI để phân tích sâu hơn và tạo báo cáo tài chính nháp.

Đây là phạm vi phù hợp để hoàn thành trong thời gian ngắn, đồng thời thể hiện rõ giá trị của AI trong hỗ trợ phòng tài chính.
