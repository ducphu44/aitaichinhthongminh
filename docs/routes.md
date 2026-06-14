# Cấu trúc Routes và API Endpoints

## 1. Frontend Routes (Next.js)

Dưới đây là cấu trúc các trang hiển thị trên trình duyệt.

| Route | Quyền truy cập (Role) | Chức năng chính |
|---|---|---|
| `/login` | `All` | Đăng nhập vào hệ thống |
| `/dashboard` | `admin`, `finance_staff`, `finance_manager`, `leader` | Xem các biểu đồ và chỉ số tổng quan |
| `/upload` | `admin`, `finance_staff` | Upload file dữ liệu tài chính (CSV, Excel) |
| `/ai-assistant` | `admin`, `finance_staff`, `finance_manager` | Giao diện chat hỏi đáp với AI về số liệu |
| `/reports` | `admin`, `finance_staff`, `finance_manager`, `leader` | Danh sách báo cáo. (Leader chỉ xem báo cáo approved) |
| `/users` | `admin` | Quản lý, cấp quyền và khóa tài khoản |

---

## 2. Backend API Endpoints (FastAPI)

Các API nội bộ được sử dụng để frontend gọi dữ liệu.

### Auth API
- `POST /auth/login`: Xác thực và trả về JWT token.
- `GET /auth/me`: Lấy thông tin user hiện tại.

### Users API
- `GET /users`: Lấy danh sách users (Admin only).
- `POST /users`: Tạo user mới.
- `PUT /users/{user_id}`: Cập nhật thông tin/role user.

### Upload API
- `POST /files/upload`: Xử lý upload file Excel/CSV, phân tích và lưu vào DB.

### Dashboard API
- `GET /dashboard/summary`: Lấy tổng thu, chi, ngân sách.
- `GET /dashboard/monthly-trend`: Dữ liệu biểu đồ theo tháng.
- `GET /dashboard/over-budget`: Danh sách các khoản chi vượt ngân sách.

### AI Assistant API
- `POST /ai/ask`: Nhận câu hỏi từ user, phân tích data và trả về câu trả lời của AI.
- `POST /ai/generate-report`: Yêu cầu AI tổng hợp dữ liệu thành một báo cáo nháp.

### Reports API
- `GET /reports`: Danh sách báo cáo.
- `GET /reports/{report_id}`: Xem chi tiết một báo cáo.
- `POST /reports/{report_id}/approve`: Trưởng phòng phê duyệt báo cáo.
- `POST /reports/{report_id}/reject`: Trưởng phòng từ chối báo cáo.
