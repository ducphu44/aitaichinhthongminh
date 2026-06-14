from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from ..models import SpendingPlan, PaymentRequest, BudgetItem, Department, Program

def get_financial_alerts(db: Session, department_id: int = None, severity_filter: str = None) -> List[Dict[str, Any]]:
    alerts = []

    # Lấy thông tin phòng ban để map tên nhanh
    depts = db.query(Department).all()
    dept_map = {d.id: d.name for d in depts}

    # Lấy thông tin dự toán để map mã dự toán
    budget_codes = {b.budget_code for b in db.query(BudgetItem.budget_code).filter(BudgetItem.budget_code != None).all()}

    # -------------------------------------------------------------------------
    # RULE 1 & 2: Vượt kế hoạch (>5%) & Sử dụng ngân sách thấp (<80%)
    # Dựa trên dữ liệu kế hoạch chi tiêu (spending_plans)
    # -------------------------------------------------------------------------
    # Lấy thông tin chương trình để map tên nhanh
    progs = db.query(Program).all()
    prog_map = {p.id: p.name for p in progs}

    spending_query = db.query(SpendingPlan)
    if department_id:
        spending_query = spending_query.filter(SpendingPlan.department_id == department_id)
    
    spending_plans = spending_query.all()

    for plan in spending_plans:
        dept_name = dept_map.get(plan.department_id, f"Phòng ban #{plan.department_id}")
        program_name = prog_map.get(plan.program_id, "Tất cả chương trình")
        
        # Tránh chia cho 0
        planned = plan.planned_amount or 0.0
        actual = plan.actual_amount or 0.0

        if planned > 0:
            # Rule 1: Vượt kế hoạch (>5%)
            if actual > planned * 1.05:
                overspent = actual - planned
                alerts.append({
                    "alert_type": "Vượt kế hoạch",
                    "severity": "High",
                    "department_name": dept_name,
                    "program_name": program_name,
                    "amount": overspent,
                    "message": f"Tháng {plan.plan_month}/{plan.fiscal_year}: Thực chi ({actual:,.0f} ₫) vượt quá kế hoạch ({planned:,.0f} ₫) là {overspent:,.0f} ₫ (tỷ lệ {actual/planned*100:.1f}%).",
                    "recommendation": "Cần rà soát các khoản chi phát sinh ngoài dự kiến và điều chỉnh kế hoạch chi tiêu cho tháng tiếp theo."
                })
            # Rule 2: Sử dụng ngân sách thấp (<80%)
            elif actual < planned * 0.8:
                under_amount = planned - actual
                alerts.append({
                    "alert_type": "Sử dụng ngân sách thấp",
                    "severity": "Low",
                    "department_name": dept_name,
                    "program_name": program_name,
                    "amount": under_amount,
                    "message": f"Tháng {plan.plan_month}/{plan.fiscal_year}: Sử dụng ngân sách đạt tỷ lệ thấp {actual/planned*100:.1f}% (Thực chi: {actual:,.0f} ₫ / Kế hoạch: {planned:,.0f} ₫).",
                    "recommendation": "Đánh giá lại tiến độ thực hiện các hạng mục công việc hoặc xem xét phân bổ lại nguồn vốn dư thừa."
                })

    # -------------------------------------------------------------------------
    # RULE 3 & 5: Đề nghị thanh toán lớn (>=200tr) & Không có mã dự toán liên quan
    # Dựa trên dữ liệu đề nghị thanh toán (payment_requests)
    # -------------------------------------------------------------------------
    payment_query = db.query(PaymentRequest)
    if department_id:
        payment_query = payment_query.filter(PaymentRequest.department_id == department_id)
        
    payment_requests = payment_query.all()

    for pr in payment_requests:
        dept_name = dept_map.get(pr.department_id, f"Phòng ban #{pr.department_id}")
        program_name = "Thanh toán nhà cung cấp"
        
        # Rule 3: Đề nghị thanh toán lớn
        if pr.total_amount >= 200000000:
            alerts.append({
                "alert_type": "Đề nghị thanh toán lớn",
                "severity": "Medium",
                "department_name": dept_name,
                "program_name": program_name,
                "amount": pr.total_amount,
                "message": f"Yêu cầu thanh toán mã {pr.payment_code} có giá trị lớn: {pr.total_amount:,.0f} ₫ (Nội dung: {pr.payment_content}).",
                "recommendation": "Yêu cầu kiểm tra kỹ hồ sơ nghiệm thu, chứng từ đi kèm và phê duyệt cấp cao trước khi thực hiện thanh toán."
            })
            
        # Rule 5: Thanh toán không có mã dự toán liên quan
        related = (pr.related_budget_code or "").strip()
        if not related or related not in budget_codes:
            alerts.append({
                "alert_type": "Thanh toán không có mã dự toán liên quan",
                "severity": "High",
                "department_name": dept_name,
                "program_name": program_name,
                "amount": pr.total_amount,
                "message": f"Mã yêu cầu {pr.payment_code} trị giá {pr.total_amount:,.0f} ₫ sử dụng mã dự toán liên kết '{related or 'Trống'}' không tồn tại trong hệ thống.",
                "recommendation": "Từ chối phê duyệt thanh toán này và yêu cầu kế toán bổ sung hoặc làm rõ mã dự toán hợp lệ liên kết."
            })

    # -------------------------------------------------------------------------
    # RULE 4: Chi phí tăng bất thường (>30% so với tháng trước cùng phòng ban)
    # Dựa trên spending_plans của cùng phòng ban
    # -------------------------------------------------------------------------
    # Group spending_plans by (department_id, program_id, fiscal_year, plan_month)
    # Vì SQLite lưu plan_month dạng integer
    monthly_data = {}
    for plan in spending_plans:
        key = (plan.department_id, plan.program_id, plan.fiscal_year)
        if key not in monthly_data:
            monthly_data[key] = {}
        monthly_data[key][plan.plan_month] = plan.actual_amount or 0.0

    for key, months in monthly_data.items():
        dept_id, prog_id, year = key
        dept_name = dept_map.get(dept_id, f"Phòng ban #{dept_id}")
        program_name = prog_map.get(prog_id, "Tất cả chương trình")
        
        # Sắp xếp các tháng có dữ liệu thực tế
        sorted_months = sorted(months.keys())
        for i in range(1, len(sorted_months)):
            prev_m = sorted_months[i-1]
            curr_m = sorted_months[i]
            
            # Chỉ check nếu 2 tháng liên tiếp nhau (vd: T1 sang T2, hoặc T5 sang T6)
            if curr_m == prev_m + 1:
                prev_actual = months[prev_m]
                curr_actual = months[curr_m]
                
                # Chi phí tăng bất thường chỉ tính khi tháng trước có chi phí > 0
                if prev_actual > 0:
                    increase_rate = (curr_actual - prev_actual) / prev_actual
                    if increase_rate > 0.3:
                        increase_amount = curr_actual - prev_actual
                        alerts.append({
                            "alert_type": "Chi phí tăng bất thường",
                            "severity": "High",
                            "department_name": dept_name,
                            "program_name": program_name,
                            "amount": increase_amount,
                            "message": f"Thực chi của chương trình '{program_name}' trong tháng {curr_m}/{year} ({curr_actual:,.0f} ₫) tăng đột biến {increase_rate*100:.1f}% so với tháng {prev_m}/{year} ({prev_actual:,.0f} ₫).",
                            "recommendation": "Yêu cầu phòng ban giải trình chi tiết các hạng mục phát sinh đột biến làm tăng chi phí trong tháng này."
                        })

    # Lọc theo severity nếu được yêu cầu
    if severity_filter:
        alerts = [a for a in alerts if a["severity"].lower() == severity_filter.lower()]

    return alerts
