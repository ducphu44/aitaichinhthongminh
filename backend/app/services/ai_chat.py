import os
import json
from openai import OpenAI
from sqlalchemy import text
from app.database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INTENT_PROMPT = """Bạn là trợ lý AI chuyên phân tích tài chính. Nhiệm vụ của bạn là phân loại ý định câu hỏi của người dùng và trích xuất các tham số.
Chỉ trả về JSON hợp lệ với cấu trúc sau, không kèm bất kỳ giải thích nào:
{
  "intent": "summary" | "overspending" | "department_spending" | "program_spending" | "payment_analysis" | "unknown",
  "department_name": "Tên phòng ban nếu có, ví dụ 'Phòng CNTT', 'Phòng Marketing', hoặc null",
  "fiscal_year": số năm nếu có, ví dụ 2026, hoặc null
}

Ý nghĩa các intent:
- summary: Hỏi tổng quan về ngân sách, thực chi, số dư.
- overspending: Hỏi về các phòng/chương trình vượt ngân sách, xài lố.
- department_spending: Hỏi về chi tiêu, tỷ lệ sử dụng của một phòng ban cụ thể.
- program_spending: Hỏi về chi tiêu của các chương trình (chương trình nào cao nhất, thấp nhất).
- payment_analysis: Hỏi về đề nghị thanh toán (lớn, bất thường, trạng thái).
- unknown: Câu hỏi không liên quan đến dữ liệu tài chính (thời tiết, lập trình, linh tinh).
"""

ANSWER_PROMPT = """Bạn là trợ lý AI chuyên phân tích tài chính của công ty. Dựa vào câu hỏi của người dùng và dữ liệu (source_data) được cung cấp, hãy trả lời câu hỏi bằng tiếng Việt một cách chuyên nghiệp, dễ hiểu và ngắn gọn.
Lưu ý quan trọng:
- CHỈ dựa vào dữ liệu được cung cấp. Tuyệt đối KHÔNG tự bịa số liệu.
- Định dạng số tiền tệ rõ ràng (ví dụ: 100,000,000 VNĐ).
- Nếu dữ liệu rỗng, hãy báo rằng không tìm thấy thông tin phù hợp.
- KHÔNG giải thích về câu lệnh SQL.
"""

def get_department_id(db, dept_name: str):
    if not dept_name:
        return None
    # Basic fuzzy search
    result = db.execute(text("SELECT id FROM departments WHERE name LIKE :name"), {"name": f"%{dept_name}%"}).fetchone()
    return result[0] if result else None

def execute_intent_query(intent: str, dept_id: int, fiscal_year: int):
    db = SessionLocal()
    try:
        data = []
        
        # Default to 2026 if not specified
        year = fiscal_year if fiscal_year else 2026

        if intent == "summary":
            query = """
                SELECT d.name as department, SUM(s.planned_amount) as total_planned, SUM(s.actual_amount) as total_actual, SUM(s.variance_amount) as total_variance
                FROM spending_plans s
                JOIN departments d ON s.department_id = d.id
                WHERE s.fiscal_year = :year
                GROUP BY d.name
            """
            result = db.execute(text(query), {"year": year}).fetchall()
            data = [{"department": r[0], "total_planned": r[1], "total_actual": r[2], "total_variance": r[3]} for r in result]
            
        elif intent == "overspending":
            query = """
                SELECT d.name as department, p.name as program, s.planned_amount, s.actual_amount, s.usage_rate
                FROM spending_plans s
                JOIN departments d ON s.department_id = d.id
                LEFT JOIN programs p ON s.program_id = p.id
                WHERE s.fiscal_year = :year AND s.actual_amount > s.planned_amount
                ORDER BY s.usage_rate DESC
                LIMIT 10
            """
            result = db.execute(text(query), {"year": year}).fetchall()
            data = [{"department": r[0], "program": r[1], "planned": r[2], "actual": r[3], "usage_rate_percent": round(r[4]*100, 2) if r[4] else 0} for r in result]

        elif intent == "department_spending":
            if dept_id:
                query = """
                    SELECT p.name as program, s.planned_amount, s.actual_amount, s.usage_rate
                    FROM spending_plans s
                    LEFT JOIN programs p ON s.program_id = p.id
                    WHERE s.fiscal_year = :year AND s.department_id = :dept_id
                """
                result = db.execute(text(query), {"year": year, "dept_id": dept_id}).fetchall()
            else:
                query = """
                    SELECT d.name as department, SUM(s.planned_amount) as planned, SUM(s.actual_amount) as actual
                    FROM spending_plans s
                    JOIN departments d ON s.department_id = d.id
                    WHERE s.fiscal_year = :year
                    GROUP BY d.name
                """
                result = db.execute(text(query), {"year": year}).fetchall()
            data = [dict(r._mapping) for r in result]

        elif intent == "program_spending":
            query = """
                SELECT p.name as program, d.name as department, SUM(s.planned_amount) as planned, SUM(s.actual_amount) as actual
                FROM spending_plans s
                JOIN programs p ON s.program_id = p.id
                JOIN departments d ON s.department_id = d.id
                WHERE s.fiscal_year = :year
                GROUP BY p.name, d.name
                ORDER BY actual DESC
                LIMIT 10
            """
            result = db.execute(text(query), {"year": year}).fetchall()
            data = [dict(r._mapping) for r in result]

        elif intent == "payment_analysis":
            query = """
                SELECT p.payment_code, d.name as department, v.vendor_name, p.total_amount, p.payment_content, p.payment_status
                FROM payment_requests p
                JOIN departments d ON p.department_id = d.id
                LEFT JOIN vendors v ON p.vendor_id = v.id
                WHERE p.fiscal_year = :year
                ORDER BY p.total_amount DESC
                LIMIT 10
            """
            result = db.execute(text(query), {"year": year}).fetchall()
            data = [dict(r._mapping) for r in result]
            
        return data
    except Exception as e:
        print("DB Error:", e)
        return []
    finally:
        db.close()

def process_chat(question: str, user_dept_id: int = None, user_year: int = None):
    # Step 1: Classify intent
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": question}
            ],
            response_format={ "type": "json_object" },
            temperature=0
        )
        
        intent_data = json.loads(response.choices[0].message.content)
        intent = intent_data.get("intent", "unknown")
        dept_name = intent_data.get("department_name")
        fiscal_year = intent_data.get("fiscal_year") or user_year
        
    except Exception as e:
        print("Intent Error:", e)
        return {
            "answer": "Xin lỗi, hệ thống AI đang gặp sự cố kết nối. Vui lòng thử lại sau.",
            "source_data": []
        }

    if intent == "unknown":
        return {
            "answer": "Xin lỗi, tôi chỉ có thể giúp bạn giải đáp các câu hỏi liên quan đến dữ liệu tài chính (ngân sách, chi tiêu, thanh toán, v.v.). Vui lòng hỏi lại một câu hỏi về tài chính nhé.",
            "source_data": []
        }

    # Step 2: Extract department ID if name is provided
    db = SessionLocal()
    target_dept_id = user_dept_id
    if dept_name:
        extracted_id = get_department_id(db, dept_name)
        if extracted_id:
            target_dept_id = extracted_id
    db.close()

    # Step 3: Execute query
    source_data = execute_intent_query(intent, target_dept_id, fiscal_year)

    # Step 4: Generate natural language answer
    try:
        answer_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ANSWER_PROMPT},
                {"role": "user", "content": f"Câu hỏi: {question}\n\nDữ liệu tìm thấy (JSON):\n{json.dumps(source_data, ensure_ascii=False)}"}
            ],
            temperature=0.3
        )
        final_answer = answer_response.choices[0].message.content
    except Exception as e:
        print("Answer Error:", e)
        final_answer = "Xin lỗi, tôi đã tìm thấy dữ liệu nhưng gặp lỗi khi tạo câu trả lời. Bạn có thể xem bảng dữ liệu thô bên dưới."

    return {
        "answer": final_answer,
        "source_data": source_data
    }
