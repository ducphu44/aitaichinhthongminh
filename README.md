# AI Trợ Lý Phân Tích Tài Chính & Lập Báo Cáo Cho Phòng Tài Chính (AI20K-046)

Hệ thống AI Assistant được thiết kế đặc thù cho Phòng Tài chính, giúp tự động hóa quá trình nhập liệu, cảnh báo tài chính, hỏi đáp AI và xuất báo cáo tự động bằng sức mạnh của LLM.

## 1. Mục tiêu dự án
- **Tự động hóa báo cáo:** Tự động tổng hợp dữ liệu chi tiêu và dùng AI để nhận xét, đưa ra khuyến nghị.
- **Theo dõi & Cảnh báo:** Hệ thống giúp phòng tài chính giám sát các khoản vượt ngân sách hoặc sắp đến hạn thanh toán.
- **Hỏi đáp thông minh (AI Chat):** Người dùng có thể hỏi trực tiếp AI về các thông số ngân sách bằng ngôn ngữ tự nhiên.

## 2. Tech Stack
- **Frontend:** Next.js 16 (App Router), TailwindCSS, Recharts (Vẽ biểu đồ), React Markdown.
- **Backend:** FastAPI (Python), SQLAlchemy (ORM), SQLite (Cơ sở dữ liệu), OpenAI API.
- **Môi trường:** Node.js, Python 3.10+, Virtualenv.

## 3. Cấu trúc thư mục
```
.
├── backend/                  # Chứa toàn bộ API và logic Python
│   ├── app/
│   │   ├── routers/          # Các endpoint API (dashboard, reports, chat...)
│   │   ├── services/         # Logic xử lý nghiệp vụ (AI, import Excel...)
│   │   ├── models.py         # Định nghĩa các bảng Database
│   │   └── main.py           # Điểm vào của FastAPI (chạy tại cổng 8000)
│   ├── tests/                # Unit Tests (Pytest)
│   └── requirements.txt      # Thư viện Python cần cài đặt
├── frontend/                 # Giao diện người dùng Next.js
│   ├── src/
│   │   ├── app/              # Các trang (Dashboard, Upload, AI Chat...)
│   │   ├── components/       # Các UI Component (Sidebar, Chart...)
│   │   └── lib/              # Cấu hình gọi API
│   └── package.json          # Thư viện NPM
└── README.md                 # Tài liệu dự án
```

## 4. Hướng dẫn chạy Backend
1. Di chuyển vào thư mục backend: `cd backend`
2. Tạo môi trường ảo: `python3 -m venv venv`
3. Kích hoạt môi trường ảo:
   - Mac/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Cài đặt thư viện: `pip install -r requirements.txt`
5. Tạo file `.env` (bạn cần có `OPENAI_API_KEY` của mình)
   ```env
   DATABASE_URL=sqlite:///./sql_app.db
   OPENAI_API_KEY=sk-xxxxx...
   ```
6. Khởi chạy server: `uvicorn app.main:app --reload`
   - API sẽ chạy tại: `http://localhost:8000`

> **Lưu ý:** Ở lần khởi chạy đầu tiên, hệ thống sẽ tự động tạo cơ sở dữ liệu `sql_app.db` và **nạp một số dữ liệu mẫu (Mock data)** để bạn có thể xem Dashboard ngay.

## 5. Hướng dẫn chạy Frontend
1. Di chuyển vào thư mục frontend: `cd frontend`
2. Cài đặt các gói NPM: `npm install`
3. Cấu hình file `.env.local` (nếu cần đổi URL backend):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Chạy dự án: `npm run dev`
   - Giao diện chạy tại: `http://localhost:3000`

## 6. Luồng Demo Đề xuất (Demo Flow)

1. **Dashboard:** Mở `http://localhost:3000`. Ngay lập tức, bạn sẽ thấy Sidebar với mã đề tài **AI20K-046**. Tại màn hình Dashboard, dữ liệu ngân sách, các biểu đồ cột và tròn sẽ hiển thị dựa trên Mock Data.
2. **Upload Excel:** Chuyển sang menu **Upload Excel**. Bạn có thể tải lên một file Excel chứa dữ liệu dự toán (nếu chưa có file chuẩn, bạn có thể tạo một file có các cột `Mã phòng ban`, `Mã ngân sách`, `Số tiền`). Sau khi Validate, hệ thống sẽ Import vào Database.
3. **Alerts (Cảnh báo):** Chuyển sang menu **Alerts** để xem hệ thống tự động lọc ra những khoản chi "Overbudget" (Vượt ngân sách).
4. **AI Chat:** Vào mục **AI Chat** hoặc bấm vào nút Chatbot ở góc phải bên dưới Dashboard để đặt câu hỏi trực tiếp cho AI.
5. **Reports (Báo cáo):** Vào mục **Reports**, chọn "Năm 2026" và ấn **Generate Report**. Chờ khoảng 10 giây để AI phân tích số liệu và tự động viết nhận xét.
6. **Xuất PDF:** Sau khi AI viết xong báo cáo (có Markdown hiển thị đẹp mắt), hãy ấn nút **Xuất PDF** để in hoặc lưu lại thành bản báo cáo chuẩn A4.

## 7. Các câu hỏi mẫu cho Trợ lý AI (Sample Queries)

Dưới đây là một số câu hỏi mẫu bằng tiếng Việt và tiếng Anh bạn có thể hỏi Trợ lý ảo (AI Assistant) để kiểm tra khả năng truy vấn SQL tự động:

- **Về ngân sách & chi tiêu:**
  - *"Tổng dự toán ngân sách năm nay là bao nhiêu?"*
  - *"Tỷ lệ sử dụng ngân sách của phòng Đào tạo là bao nhiêu?"*
  - *"Có phòng ban nào chi tiêu vượt hạn mức kế hoạch không?"*
- **Về danh sách chi tiết:**
  - *"Xem 5 khoản chi lớn nhất gần đây"*
  - *"Liệt kê danh sách các nhà cung cấp (vendors) trong hệ thống"*
- **Truy vấn phức tạp:**
  - *"Phòng ban nào có số tiền đề nghị thanh toán lớn nhất?"*
  - *"Hãy phân tích cơ cấu chi tiêu theo từng quý của phòng CNTT"*

## 8. Hướng dẫn Deploy (Vercel & Render)

Hệ thống được thiết kế hoàn hảo để phân tách Frontend và Backend, giúp bạn dễ dàng đưa ứng dụng lên Internet hoàn toàn miễn phí.

### Bước 1: Chuẩn bị Github
Hãy đảm bảo bạn đã đẩy (push) toàn bộ mã nguồn của mình lên Github (nhánh `main`).

### Bước 2: Deploy Backend lên Render.com (Miễn phí)
1. Truy cập [Render.com](https://render.com) và đăng nhập bằng Github.
2. Chọn **New +** -> **Web Service**.
3. Chọn kho chứa code (Repository) Github của bạn.
4. Cấu hình ứng dụng:
   - **Name:** Tùy ý (ví dụ: `ai-finance-backend`)
   - **Language:** Python
   - **Branch:** `main`
   - **Root Directory:** `backend` (RẤT QUAN TRỌNG: Phải trỏ đúng vào thư mục `backend`)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Cuộn xuống phần **Environment Variables**, thêm biến:
   - `OPENAI_API_KEY`: Điền key OpenAI của bạn vào đây.
6. Bấm **Create Web Service**. Chờ khoảng 2-3 phút, Render sẽ cung cấp cho bạn một đường link backend, ví dụ: `https://ai-finance-backend.onrender.com`. Hãy copy link này lại.

### Bước 3: Deploy Frontend lên Vercel.com (Miễn phí)
1. Truy cập [Vercel.com](https://vercel.com) và đăng nhập bằng Github.
2. Bấm **Add New...** -> **Project**.
3. Import kho chứa code (Repository) Github của bạn.
4. Cấu hình Project:
   - **Framework Preset:** Next.js
   - **Root Directory:** Bấm nút **Edit** và chọn thư mục `frontend`.
5. Mở tab **Environment Variables**, thêm biến:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** Điền đường link Backend mà Render vừa cấp cho bạn ở Bước 2 (Ví dụ: `https://ai-finance-backend.onrender.com` - *Lưu ý: Không có dấu `/` ở cuối*).
6. Bấm **Deploy**. Chờ khoảng 1 phút, Vercel sẽ cấp cho bạn một đường link (Ví dụ: `https://ai-finance.vercel.app`).

**Chúc mừng! 🎉 Hệ thống AI của bạn đã hoàn toàn hoạt động trực tuyến.** Bạn có thể chia sẻ link của Vercel cho bất kỳ ai để demo.
