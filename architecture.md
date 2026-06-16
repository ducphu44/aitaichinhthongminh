# Sơ đồ Kiến trúc & Luồng dữ liệu (Architecture & Data Flow)

Hệ thống được thiết kế theo kiến trúc tách biệt hoàn toàn giữa **Frontend (Next.js)** và **Backend (FastAPI)**, giao tiếp thông qua **RESTful API** và tích hợp sức mạnh của **LLM (OpenAI API)** thông qua cơ chế **Function Calling (SQL Agent)**.

---

## 1. Sơ đồ các Thành phần (Component Diagram)

```mermaid
graph TD
    %% Frontend Components
    subgraph Frontend [Next.js Web Client]
        UI[User Interface - Dashboard/Upload/AI Chat]
        CW[ChatWidget - Floating Chatbot]
        API[API Client - src/lib/api.ts]
        UI --> API
        CW --> API
    end

    %% Backend Components
    subgraph Backend [FastAPI Server]
        R_U[Uploads Router]
        R_D[Dashboard Router]
        R_AI[Ask/Chat Router]
        
        V_EX[Excel Validator Service]
        I_EX[Data Importer Service]
        AI_AG[AI SQL Agent Service]
        
        R_U --> V_EX
        R_U --> I_EX
        R_AI --> AI_AG
    end

    %% External & Database Components
    subgraph Storage [Database & External Services]
        DB[(SQLite Database)]
        O_AI[OpenAI LLM API]
    end

    %% Giao tiếp giữa các thành phần
    API -->|REST API Requests| Backend
    V_EX -->|Ghi log lỗi cấu trúc| DB
    I_EX -->|Import Budget/Spending/Payments| DB
    R_D -->|Truy vấn số liệu| DB
    AI_AG <-->|Function Calling / Schema| O_AI
    AI_AG -->|Chạy SQL truy vấn động| DB
```

---

## 2. Luồng dữ liệu Chi tiết (Detailed Data Flows)

### A. Luồng Tải lên và Nạp dữ liệu Excel (Excel Upload & Import Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng
    participant FE as Frontend Client
    participant BE as FastAPI Backend
    participant DB as SQLite Database

    User->>FE: Chọn file Excel & Phòng ban, bấm "Tải lên"
    FE->>BE: POST /uploads (Multipart File)
    Note over BE: Lưu file vào thư mục /uploads/<br/>Tạo bản ghi ở trạng thái 'pending'
    BE-->>FE: Trả về upload_id
    
    User->>FE: Bấm "Kiểm tra file (Validate)"
    FE->>BE: POST /uploads/{upload_id}/validate
    Note over BE: Chạy excel_validator.py:<br/>Kiểm tra định dạng cột, kiểm tra dữ liệu trống
    BE->>DB: Lưu danh sách lỗi vào bảng import_errors (nếu có)
    BE-->>FE: Trả về trạng thái (Validated hoặc Failed) & Thống kê số dòng
    
    alt Không có lỗi (Error Rows = 0)
        User->>FE: Bấm "Nạp vào Database (Import)"
        FE->>BE: POST /uploads/{upload_id}/import
        Note over BE: Chạy data_importer.py:<br/>Đọc dữ liệu 3 sheet<br/>Kiểm tra trùng budget_code & payment_code
        BE->>DB: Trích xuất dữ liệu ghi vào budget_items, spending_plans, payment_requests
        BE->>DB: Cập nhật uploaded_files.import_status = 'Imported'
        BE-->>FE: Trả về số dòng đã import thành công
        FE-->>User: Hiển thị thông báo thành công và làm mới Lịch sử
    else Có lỗi (Error Rows > 0)
        FE-->>User: Hiển thị danh sách dòng lỗi (Validation Log) để sửa đổi
    end
```

### B. Luồng Hỏi đáp Dữ liệu bằng AI (AI Chat & SQL Tool Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng
    participant FE as ChatWidget / AI Chat UI
    participant BE as FastAPI Backend
    participant LLM as OpenAI (GPT model)
    participant DB as SQLite Database

    User->>FE: Nhập câu hỏi (Ví dụ: "Phòng CNTT chi tiêu thế nào năm nay?")
    FE->>BE: POST /ai/ask (Dữ liệu câu hỏi)
    BE->>LLM: Gửi câu hỏi kèm mô tả schema database và danh sách Tools (Hàm chạy SQL)
    Note over LLM: Phân tích câu hỏi và sinh ra câu lệnh SQL<br/>Yêu cầu gọi Tool: execute_sql(sql_query)
    LLM-->>BE: Yêu cầu gọi hàm execute_sql(query)
    BE->>DB: Thực thi câu lệnh SQL động do LLM sinh ra
    DB-->>BE: Trả về kết quả bảng dữ liệu thô (Raw Data)
    BE->>LLM: Gửi trả kết quả bảng dữ liệu thô cho OpenAI
    Note over LLM: Đọc bảng số liệu, phân tích nhận xét<br/>Tổng hợp câu trả lời dạng Markdown
    LLM-->>BE: Trả về câu trả lời hoàn chỉnh (Markdown chứa bảng)
    BE-->>FE: Trả về câu trả lời (answer_markdown) & danh sách công cụ đã dùng
    Note over FE: Render Markdown thành bảng trực quan và văn bản đẹp mắt
    FE-->>User: Hiển thị kết quả trong khung chat
```
