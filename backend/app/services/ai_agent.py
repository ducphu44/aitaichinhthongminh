import os
import json
from openai import OpenAI
from sqlalchemy import text
from app.database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------- SQL Query Tools -----------------

def get_budget_summary(fiscal_year: int) -> str:
    db = SessionLocal()
    try:
        query = """
            SELECT SUM(planned_amount) as total_planned, SUM(actual_amount) as total_actual, SUM(variance_amount) as total_variance
            FROM spending_plans
            WHERE fiscal_year = :year
        """
        result = db.execute(text(query), {"year": fiscal_year}).fetchone()
        if not result or result[0] is None:
            return json.dumps({"error": f"No data found for year {fiscal_year}"})
        
        return json.dumps({
            "total_planned": result[0],
            "total_actual": result[1],
            "total_variance": result[2],
            "usage_rate_percent": round((result[1] / result[0]) * 100, 2) if result[0] > 0 else 0
        })
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()

def get_department_spending(fiscal_year: int, department_name: str) -> str:
    db = SessionLocal()
    try:
        query = """
            SELECT p.name as program, s.planned_amount, s.actual_amount, s.usage_rate
            FROM spending_plans s
            LEFT JOIN programs p ON s.program_id = p.id
            JOIN departments d ON s.department_id = d.id
            WHERE s.fiscal_year = :year AND d.name LIKE :dept_name
        """
        result = db.execute(text(query), {"year": fiscal_year, "dept_name": f"%{department_name}%"}).fetchall()
        if not result:
            return json.dumps({"error": f"No department matching {department_name} found in {fiscal_year}."})
        
        data = [dict(r._mapping) for r in result]
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()

def get_top_over_budget_programs(fiscal_year: int, limit: int = 10) -> str:
    db = SessionLocal()
    try:
        query = """
            SELECT d.name as department, p.name as program, s.planned_amount, s.actual_amount, s.usage_rate
            FROM spending_plans s
            JOIN departments d ON s.department_id = d.id
            LEFT JOIN programs p ON s.program_id = p.id
            WHERE s.fiscal_year = :year AND s.actual_amount > s.planned_amount
            ORDER BY s.usage_rate DESC
            LIMIT :limit
        """
        result = db.execute(text(query), {"year": fiscal_year, "limit": limit}).fetchall()
        data = [{"department": r[0], "program": r[1], "planned": r[2], "actual": r[3], "usage_rate_percent": round(r[4]*100, 2) if r[4] else 0} for r in result]
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()

def get_top_programs_spending(fiscal_year: int, limit: int = 10) -> str:
    db = SessionLocal()
    try:
        query = """
            SELECT p.name as program, d.name as department, SUM(s.planned_amount) as planned, SUM(s.actual_amount) as actual
            FROM spending_plans s
            JOIN programs p ON s.program_id = p.id
            JOIN departments d ON s.department_id = d.id
            WHERE s.fiscal_year = :year
            GROUP BY p.name, d.name
            ORDER BY actual DESC
            LIMIT :limit
        """
        result = db.execute(text(query), {"year": fiscal_year, "limit": limit}).fetchall()
        data = [dict(r._mapping) for r in result]
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()

def get_large_payment_requests(fiscal_year: int, limit: int = 10) -> str:
    db = SessionLocal()
    try:
        query = """
            SELECT p.payment_code, d.name as department, v.vendor_name, p.total_amount, p.payment_content, p.payment_status
            FROM payment_requests p
            JOIN departments d ON p.department_id = d.id
            LEFT JOIN vendors v ON p.vendor_id = v.id
            WHERE p.fiscal_year = :year
            ORDER BY p.total_amount DESC
            LIMIT :limit
        """
        result = db.execute(text(query), {"year": fiscal_year, "limit": limit}).fetchall()
        data = [dict(r._mapping) for r in result]
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()

# ----------------- AI Agent Tools Definition -----------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_budget_summary",
            "description": "Lấy tổng quan ngân sách của toàn công ty trong một năm cụ thể.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fiscal_year": {"type": "integer", "description": "Năm tài chính (VD: 2026)"}
                },
                "required": ["fiscal_year"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_department_spending",
            "description": "Lấy thông tin chi tiết chi tiêu của một phòng ban.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fiscal_year": {"type": "integer", "description": "Năm tài chính (VD: 2026)"},
                    "department_name": {"type": "string", "description": "Tên phòng ban cần tra cứu (VD: 'Phòng CNTT')"}
                },
                "required": ["fiscal_year", "department_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_over_budget_programs",
            "description": "Tìm các phòng ban hoặc chương trình đang vượt ngân sách (chi tiêu nhiều hơn dự kiến).",
            "parameters": {
                "type": "object",
                "properties": {
                    "fiscal_year": {"type": "integer", "description": "Năm tài chính (VD: 2026)"},
                    "limit": {"type": "integer", "description": "Số lượng kết quả trả về (mặc định 10)"}
                },
                "required": ["fiscal_year"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_programs_spending",
            "description": "Lấy danh sách các chương trình tiêu tốn nhiều ngân sách nhất.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fiscal_year": {"type": "integer", "description": "Năm tài chính (VD: 2026)"},
                    "limit": {"type": "integer", "description": "Số lượng kết quả trả về (mặc định 10)"}
                },
                "required": ["fiscal_year"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_large_payment_requests",
            "description": "Tìm các khoản đề nghị thanh toán có số tiền lớn nhất hoặc bất thường.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fiscal_year": {"type": "integer", "description": "Năm tài chính (VD: 2026)"},
                    "limit": {"type": "integer", "description": "Số lượng kết quả trả về (mặc định 10)"}
                },
                "required": ["fiscal_year"]
            }
        }
    }
]

available_functions = {
    "get_budget_summary": get_budget_summary,
    "get_department_spending": get_department_spending,
    "get_top_over_budget_programs": get_top_over_budget_programs,
    "get_top_programs_spending": get_top_programs_spending,
    "get_large_payment_requests": get_large_payment_requests,
}

SYSTEM_PROMPT = """Bạn là trợ lý AI phân tích tài chính chuyên nghiệp. Nhiệm vụ của bạn là sử dụng các công cụ (tools) được cung cấp để truy vấn dữ liệu từ database, sau đó tổng hợp thành câu trả lời Tiếng Việt dễ hiểu, chuyên nghiệp dưới dạng Markdown.
Luôn định dạng số tiền VND rõ ràng (VD: 100,000,000 VNĐ). Trình bày thông tin trực quan bằng danh sách (bullets) hoặc bảng markdown (tables) nếu có nhiều dữ liệu.
Tuyệt đối KHÔNG tự bịa dữ liệu nếu tools trả về kết quả rỗng. Nếu câu hỏi không liên quan đến tài chính, hãy từ chối một cách lịch sự."""

def ask_question(question: str, default_year: int = 2026) -> dict:
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\nNăm hiện tại mặc định là {default_year} nếu người dùng không nhắc đến."},
        {"role": "user", "content": question}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0
        )
        
        response_message = response.choices[0].message
        
        # Nếu AI quyết định gọi Tool
        if response_message.tool_calls:
            messages.append(response_message)  # extend conversation with assistant's reply
            used_tools = []
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                used_tools.append(function_name)
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                # Gọi hàm python nội bộ
                function_response = function_to_call(
                    fiscal_year=function_args.get("fiscal_year", default_year),
                    **{k:v for k,v in function_args.items() if k != "fiscal_year"}
                )
                
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            
            # Gửi lại kết quả của Tool cho OpenAI để tổng hợp câu trả lời cuối
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3
            )
            return {
                "answer_markdown": second_response.choices[0].message.content,
                "used_tools": used_tools
            }
        
        else:
            # AI có thể trả lời trực tiếp mà không cần dùng tool
            return {
                "answer_markdown": response_message.content,
                "used_tools": []
            }

    except Exception as e:
        print("AI Agent Error:", e)
        return {
            "answer_markdown": "Xin lỗi, hệ thống AI đang gặp sự cố. Vui lòng thử lại sau.",
            "used_tools": []
        }
