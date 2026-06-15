from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from ..database import get_db
from ..models import BudgetItem, SpendingPlan, PaymentRequest, Department, Program
from ..auth import RoleChecker

router = APIRouter(
    prefix="/dashboard", 
    tags=["Dashboard"],
    dependencies=[Depends(RoleChecker(["finance_staff", "finance_manager", "leader"]))]
)


# ────────────────────────────────────────────────────────────────────────────
# GET /dashboard/summary
# ────────────────────────────────────────────────────────────────────────────
@router.get("/summary")
def get_summary(
    year: Optional[int] = Query(None, description="Năm tài chính"),
    quarter: Optional[int] = Query(None, description="Quý (1-4)"),
    department_id: Optional[int] = Query(None, description="ID phòng ban"),
    db: Session = Depends(get_db),
):
    # ── Tổng dự toán ngân sách (BudgetItem.estimated_amount)
    budget_q = db.query(func.coalesce(func.sum(BudgetItem.estimated_amount), 0))
    if year:
        budget_q = budget_q.filter(BudgetItem.fiscal_year == year)
    if quarter:
        budget_q = budget_q.filter(BudgetItem.quarter == quarter)
    if department_id:
        budget_q = budget_q.filter(BudgetItem.department_id == department_id)
    total_budget = float(budget_q.scalar() or 0)

    # ── Tổng kế hoạch chi tiêu (SpendingPlan.planned_amount)
    plan_q = db.query(func.coalesce(func.sum(SpendingPlan.planned_amount), 0))
    if year:
        plan_q = plan_q.filter(SpendingPlan.fiscal_year == year)
    if quarter:
        plan_q = plan_q.filter(SpendingPlan.quarter == quarter)
    if department_id:
        plan_q = plan_q.filter(SpendingPlan.department_id == department_id)
    total_planned = float(plan_q.scalar() or 0)

    # ── Tổng thực chi (SpendingPlan.actual_amount)
    actual_q = db.query(func.coalesce(func.sum(SpendingPlan.actual_amount), 0))
    if year:
        actual_q = actual_q.filter(SpendingPlan.fiscal_year == year)
    if quarter:
        actual_q = actual_q.filter(SpendingPlan.quarter == quarter)
    if department_id:
        actual_q = actual_q.filter(SpendingPlan.department_id == department_id)
    total_actual = float(actual_q.scalar() or 0)

    # ── Tổng đề nghị thanh toán (PaymentRequest.total_amount)
    payment_q = db.query(func.coalesce(func.sum(PaymentRequest.total_amount), 0))
    if year:
        payment_q = payment_q.filter(PaymentRequest.fiscal_year == year)
    if quarter:
        payment_q = payment_q.filter(PaymentRequest.quarter == quarter)
    if department_id:
        payment_q = payment_q.filter(PaymentRequest.department_id == department_id)
    total_payment_requests = float(payment_q.scalar() or 0)

    # ── Sử dụng kế hoạch nếu chưa có dự toán
    effective_budget = total_budget if total_budget > 0 else total_planned

    # ── Ngân sách còn lại
    remaining_budget = effective_budget - total_actual

    # ── Tỷ lệ sử dụng ngân sách (%)
    usage_rate = (total_actual / effective_budget * 100) if effective_budget > 0 else 0.0

    # ── Số khoản vượt kế hoạch (variance_amount > 0 → thực chi > kế hoạch)
    over_q = db.query(func.count(SpendingPlan.id)).filter(SpendingPlan.variance_amount > 0)
    if year:
        over_q = over_q.filter(SpendingPlan.fiscal_year == year)
    if quarter:
        over_q = over_q.filter(SpendingPlan.quarter == quarter)
    if department_id:
        over_q = over_q.filter(SpendingPlan.department_id == department_id)
    overspending_count = int(over_q.scalar() or 0)

    return {
        "total_budget": effective_budget,
        "total_planned": total_planned,
        "total_actual": total_actual,
        "total_payment_requests": total_payment_requests,
        "remaining_budget": remaining_budget,
        "usage_rate": round(usage_rate, 2),
        "overspending_count": overspending_count,
    }


# ────────────────────────────────────────────────────────────────────────────
# GET /dashboard/monthly-trend
# ────────────────────────────────────────────────────────────────────────────
@router.get("/monthly-trend")
def get_monthly_trend(
    year: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(
        SpendingPlan.plan_month,
        func.coalesce(func.sum(SpendingPlan.planned_amount), 0).label("planned"),
        func.coalesce(func.sum(SpendingPlan.actual_amount), 0).label("actual"),
    ).group_by(SpendingPlan.plan_month).order_by(SpendingPlan.plan_month)

    if year:
        q = q.filter(SpendingPlan.fiscal_year == year)
    if department_id:
        q = q.filter(SpendingPlan.department_id == department_id)

    rows = q.all()

    # Đảm bảo 12 tháng đủ
    month_map = {row.plan_month: row for row in rows}
    result = []
    for m in range(1, 13):
        row = month_map.get(m)
        result.append({
            "month": m,
            "month_label": f"T{m}",
            "planned": float(row.planned) if row else 0.0,
            "actual": float(row.actual) if row else 0.0,
        })
    return result


# ────────────────────────────────────────────────────────────────────────────
# GET /dashboard/by-department
# ────────────────────────────────────────────────────────────────────────────
@router.get("/by-department")
def get_by_department(
    year: Optional[int] = Query(None),
    quarter: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = (
        db.query(
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            func.coalesce(func.sum(SpendingPlan.planned_amount), 0).label("planned"),
            func.coalesce(func.sum(SpendingPlan.actual_amount), 0).label("actual"),
        )
        .outerjoin(SpendingPlan, SpendingPlan.department_id == Department.id)
        .group_by(Department.id, Department.name)
        .order_by(func.coalesce(func.sum(SpendingPlan.actual_amount), 0).desc())
    )

    if year:
        q = q.filter((SpendingPlan.fiscal_year == year) | (SpendingPlan.fiscal_year == None))
    if quarter:
        q = q.filter((SpendingPlan.quarter == quarter) | (SpendingPlan.quarter == None))

    rows = q.all()
    return [
        {
            "department_id": row.department_id,
            "department_name": row.department_name,
            "planned": float(row.planned),
            "actual": float(row.actual),
        }
        for row in rows
    ]


# ────────────────────────────────────────────────────────────────────────────
# GET /dashboard/by-program
# ────────────────────────────────────────────────────────────────────────────
@router.get("/by-program")
def get_by_program(
    year: Optional[int] = Query(None),
    quarter: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = (
        db.query(
            Program.id.label("program_id"),
            Program.name.label("program_name"),
            func.coalesce(func.sum(BudgetItem.estimated_amount), 0).label("budget"),
            func.coalesce(func.sum(SpendingPlan.actual_amount), 0).label("actual"),
        )
        .outerjoin(BudgetItem, BudgetItem.program_id == Program.id)
        .outerjoin(SpendingPlan, SpendingPlan.department_id == Program.department_id)
        .group_by(Program.id, Program.name)
    )

    if year:
        q = q.filter((BudgetItem.fiscal_year == year) | (BudgetItem.fiscal_year == None))
    if quarter:
        q = q.filter((BudgetItem.quarter == quarter) | (BudgetItem.quarter == None))
    if department_id:
        q = q.filter(Program.department_id == department_id)

    q = q.order_by(func.coalesce(func.sum(BudgetItem.estimated_amount), 0).desc()).limit(5)

    rows = q.all()
    return [
        {
            "program_id": row.program_id,
            "program_name": row.program_name,
            "budget": float(row.budget),
            "actual": float(row.actual),
        }
        for row in rows
    ]


# ────────────────────────────────────────────────────────────────────────────
# GET /dashboard/overspending
# ────────────────────────────────────────────────────────────────────────────
@router.get("/overspending")
def get_overspending(
    year: Optional[int] = Query(None),
    quarter: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = (
        db.query(
            SpendingPlan.id,
            SpendingPlan.plan_month,
            SpendingPlan.fiscal_year,
            SpendingPlan.quarter,
            SpendingPlan.planned_amount,
            SpendingPlan.actual_amount,
            SpendingPlan.variance_amount,
            SpendingPlan.usage_rate,
            SpendingPlan.warning_status,
            Department.name.label("department_name"),
        )
        .join(Department, Department.id == SpendingPlan.department_id)
        .filter(SpendingPlan.variance_amount > 0)
    )

    if year:
        q = q.filter(SpendingPlan.fiscal_year == year)
    if quarter:
        q = q.filter(SpendingPlan.quarter == quarter)
    if department_id:
        q = q.filter(SpendingPlan.department_id == department_id)

    q = q.order_by(SpendingPlan.variance_amount.desc()).limit(5)

    rows = q.all()
    return [
        {
            "id": row.id,
            "department_name": row.department_name,
            "plan_month": row.plan_month,
            "fiscal_year": row.fiscal_year,
            "quarter": row.quarter,
            "planned_amount": float(row.planned_amount),
            "actual_amount": float(row.actual_amount),
            "variance_amount": float(row.variance_amount),
            "usage_rate": float(row.usage_rate or 0),
            "warning_status": row.warning_status,
        }
        for row in rows
    ]
