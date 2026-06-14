import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import ReportGenerateRequest, ReportResponse
from app.services.report_generator import fetch_report_data, generate_ai_insights, build_markdown_report
from app.database import get_db
from app.models import GeneratedReport

from app.auth import RoleChecker

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(RoleChecker(["finance_staff", "finance_manager", "leader"]))]
)

@router.post("/generate", response_model=ReportResponse)
def generate_report(request: ReportGenerateRequest, db: Session = Depends(get_db)):
    try:
        # 1. Fetch raw data
        raw_data = fetch_report_data(
            fiscal_year=request.fiscal_year,
            department_id=request.department_id,
            quarter=request.quarter,
            month=request.month
        )
        
        # 2. Let AI generate insights based on raw data
        ai_insights = generate_ai_insights(raw_data)
        
        # 3. Build Markdown content
        period_str = f"Năm {request.fiscal_year}"
        if request.quarter:
            period_str += f", Quý {request.quarter}"
        if request.month:
            period_str += f", Tháng {request.month}"
            
        title = f"Executive Financial Dashboard - {period_str}"
        
        content_markdown = build_markdown_report(raw_data, ai_insights, title, period_str)
        
        # 4. Save to Database
        new_report = GeneratedReport(
            title=title,
            report_type=request.report_type,
            fiscal_year=request.fiscal_year,
            quarter=request.quarter,
            month=request.month,
            department_id=request.department_id,
            content_markdown=content_markdown,
            raw_data_json=json.dumps(raw_data, ensure_ascii=False)
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        return new_report
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("", response_model=list[ReportResponse])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(GeneratedReport).order_by(GeneratedReport.created_at.desc()).all()
    return reports

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
