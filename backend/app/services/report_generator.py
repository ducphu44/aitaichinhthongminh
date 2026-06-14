import os
import json
from openai import OpenAI
from sqlalchemy import text
from app.database import SessionLocal
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_currency(value):
    if value is None:
        return "0 VNĐ"
    return f"{int(value):,} VNĐ"

def fetch_report_data(fiscal_year: int, department_id: int = None, quarter: int = None, month: int = None):
    db = SessionLocal()
    try:
        # Build conditions
        conditions = ["fiscal_year = :year"]
        params = {"year": fiscal_year}
        
        if department_id:
            conditions.append("department_id = :dept_id")
            params["dept_id"] = department_id
        if quarter:
            conditions.append("quarter = :quarter")
            params["quarter"] = quarter
        if month:
            conditions.append("plan_month = :month")
            params["month"] = month
            
        where_clause = " AND ".join(conditions)

        # 1. Budget Summary
        query_summary = f"""
            SELECT 
                SUM(planned_amount) as total_planned, 
                SUM(actual_amount) as total_actual
            FROM spending_plans
            WHERE {where_clause}
        """
        summary_res = db.execute(text(query_summary), params).fetchone()
        total_planned = summary_res[0] or 0
        total_actual = summary_res[1] or 0
        usage_rate = round((total_actual / total_planned) * 100, 2) if total_planned > 0 else 0

        # 2. Payments waiting
        payment_conditions = ["fiscal_year = :year"]
        if department_id:
            payment_conditions.append("department_id = :dept_id")
        if quarter:
            payment_conditions.append("quarter = :quarter")
            
        where_payment = " AND ".join(payment_conditions)
        query_pending = f"""
            SELECT COUNT(id) as pending_count, SUM(total_amount) as pending_amount
            FROM payment_requests
            WHERE {where_payment} AND payment_status = 'pending'
        """
        pending_res = db.execute(text(query_pending), params).fetchone()
        pending_count = pending_res[0] or 0
        pending_amount = pending_res[1] or 0

        # 3. Over budget programs
        query_over = f"""
            SELECT d.name as dept, p.name as program, s.planned_amount, s.actual_amount, s.usage_rate
            FROM spending_plans s
            JOIN departments d ON s.department_id = d.id
            LEFT JOIN programs p ON s.program_id = p.id
            WHERE {where_clause} AND s.actual_amount > s.planned_amount
            ORDER BY s.usage_rate DESC
            LIMIT 5
        """
        over_res = db.execute(text(query_over), params).fetchall()
        over_budget = [{"department": r[0], "program": r[1], "planned": r[2], "actual": r[3], "usage_rate_percent": round(r[4]*100, 2) if r[4] else 0} for r in over_res]

        # 4. Large payments
        query_large = f"""
            SELECT d.name as dept, pr.payment_code, pr.payment_content, pr.total_amount
            FROM payment_requests pr
            JOIN departments d ON pr.department_id = d.id
            WHERE {where_payment}
            ORDER BY pr.total_amount DESC
            LIMIT 5
        """
        large_res = db.execute(text(query_large), params).fetchall()
        large_payments = [{"department": r[0], "code": r[1], "content": r[2], "amount": r[3]} for r in large_res]

        # 5. Department Breakdown for Pie Chart
        query_dept = f"""
            SELECT d.name, SUM(s.planned_amount) as planned, SUM(s.actual_amount) as actual
            FROM spending_plans s
            JOIN departments d ON s.department_id = d.id
            WHERE {where_clause}
            GROUP BY d.name
        """
        dept_res = db.execute(text(query_dept), params).fetchall()
        department_budgets = [{"name": r[0], "planned": r[1] or 0, "actual": r[2] or 0} for r in dept_res]

        return {
            "summary": {
                "total_planned": total_planned,
                "total_actual": total_actual,
                "usage_rate_percent": usage_rate,
                "pending_payments_count": pending_count,
                "pending_payments_amount": pending_amount,
                "over_budget_count": len(over_budget)
            },
            "over_budget_programs": over_budget,
            "large_payments": large_payments,
            "department_budgets": department_budgets
        }
    finally:
        db.close()

def generate_ai_insights(raw_data: dict) -> dict:
    prompt = f"""
    Bạn là một chuyên gia phân tích tài chính (Financial Analyst) cấp cao.
    Dựa vào các số liệu tài chính thô dưới đây, hãy viết 2 phần:
    1. Nhận xét AI: Đánh giá tổng quan về tình hình chi tiêu, mức độ an toàn ngân sách, các khoản chi nổi cộm.
    2. Khuyến nghị kiểm tra: Đưa ra các lời khuyên cho Ban Giám Hiệu/Giám đốc (Ví dụ: rà soát lại phòng A, kiểm tra khoản thanh toán B).
    
    YÊU CẦU QUAN TRỌNG:
    - KHÔNG ĐƯỢC bịa đặt bất kỳ con số nào. Chỉ dựa vào dữ liệu được cung cấp.
    - Trình bày ngắn gọn, chuyên nghiệp, gạch đầu dòng rõ ràng.
    - Trả về kết quả dưới định dạng JSON có 2 key: "comments" (chuỗi chứa markdown) và "recommendations" (chuỗi chứa markdown).

    Dữ liệu thô (JSON):
    {json.dumps(raw_data, ensure_ascii=False, indent=2)}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("AI Generation Error:", e)
        return {
            "comments": "Lỗi khi sinh nhận xét từ AI.",
            "recommendations": "Lỗi khi sinh khuyến nghị từ AI."
        }

def build_markdown_report(data: dict, ai_insights: dict, title: str, period_str: str) -> str:
    summary = data["summary"]
    remaining = summary["total_planned"] - summary["total_actual"]
    
    md = f"""# {title}

**Thời gian báo cáo:** {period_str}
**Ngày xuất báo cáo:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

---

## 1. Executive Summary (Tóm tắt điều hành)

| Chỉ số | Giá trị |
|--------|---------|
| Tổng ngân sách dự kiến | **{format_currency(summary['total_planned'])}** |
| Đã sử dụng (Thực chi) | **{format_currency(summary['total_actual'])}** |
| Ngân sách còn lại | **{format_currency(remaining)}** |
| Tỷ lệ sử dụng | **{summary['usage_rate_percent']}%** |
| Đề nghị thanh toán đang chờ | **{summary['pending_payments_count']}** đơn ({format_currency(summary['pending_payments_amount'])}) |
| Số chương trình vượt ngân sách | **{summary['over_budget_count']}** |

---

## 2. Các khoản vượt kế hoạch (Cần lưu ý)
"""
    if data["over_budget_programs"]:
        md += "\n| Phòng ban | Chương trình | Dự kiến | Thực chi | Tỷ lệ |\n|---|---|---|---|---|\n"
        for item in data["over_budget_programs"]:
            md += f"| {item['department']} | {item['program']} | {format_currency(item['planned'])} | {format_currency(item['actual'])} | {item['usage_rate_percent']}% |\n"
    else:
        md += "\n*Không có chương trình nào vượt ngân sách.* \n"

    md += """
---

## 3. Các khoản thanh toán lớn nhất
"""
    if data["large_payments"]:
        md += "\n| Phòng ban | Mã thanh toán | Nội dung | Số tiền |\n|---|---|---|---|\n"
        for item in data["large_payments"]:
            md += f"| {item['department']} | {item['code']} | {item['content']} | {format_currency(item['amount'])} |\n"
    else:
        md += "\n*Không có dữ liệu thanh toán.* \n"

    md += f"""
---

## 4. Nhận xét từ AI Financial Analyst
{ai_insights.get('comments', '')}

## 5. Khuyến nghị kiểm tra
{ai_insights.get('recommendations', '')}

---
> ⚠️ **Cảnh báo an toàn:** Báo cáo này do AI hỗ trợ tổng hợp dựa trên dữ liệu từ hệ thống. Vui lòng kiểm tra và đối chiếu lại với chứng từ gốc trước khi sử dụng cho các quyết định chính thức.
"""
    return md
