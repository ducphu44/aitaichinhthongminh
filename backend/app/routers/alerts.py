from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from ..database import get_db
from ..services.financial_alerts import get_financial_alerts
from ..models import SpendingPlan, Department
from ..auth import RoleChecker

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
    dependencies=[Depends(RoleChecker(["finance_staff", "finance_manager", "leader"]))]
)

@router.get("")
def list_alerts(
    department_id: Optional[int] = Query(None, description="ID phòng ban để lọc"),
    severity: Optional[str] = Query(None, description="Độ nghiêm trọng để lọc (High, Medium, Low)"),
    db: Session = Depends(get_db)
):
    try:
        alerts = get_financial_alerts(db, department_id=department_id, severity_filter=severity)
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tính toán cảnh báo tài chính: {str(e)}"
        )
