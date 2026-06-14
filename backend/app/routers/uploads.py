from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import os
import shutil
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import UploadedFile, ImportError, Department
from ..services.excel_validator import validate_excel_file
from ..services.data_importer import import_excel_data

from ..auth import RoleChecker

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
    dependencies=[Depends(RoleChecker(["finance_staff"]))]
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 0. GET /uploads — Lịch sử upload
@router.get("")
def list_uploads(db: Session = Depends(get_db)):
    files = (
        db.query(UploadedFile, Department.name.label("dept_name"))
        .outerjoin(Department, Department.id == UploadedFile.department_id)
        .order_by(UploadedFile.uploaded_at.desc())
        .all()
    )
    return [
        {
            "id": f.id,
            "file_name": f.file_name,
            "file_type": f.file_type,
            "department_name": dept_name,
            "import_status": f.import_status,
            "total_rows": f.total_rows,
            "valid_rows": f.valid_rows,
            "error_rows": f.error_rows,
            "uploaded_at": (f.uploaded_at.isoformat() + "Z") if f.uploaded_at else None,
        }
        for f, dept_name in files
    ]

# 1. POST /uploads
@router.post("", status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = File(...),
    department_id: int = Form(1),
    db: Session = Depends(get_db)
):
    # Verify department exists
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with ID {department_id} does not exist."
        )

    # Save file to disk
    file_extension = os.path.splitext(file.filename)[1]
    # Standardize name with timestamp to avoid collisions
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )

    # Create DB entry
    db_file = UploadedFile(
        file_name=file.filename,
        file_type=file.content_type or file_extension,
        file_path=file_path,
        department_id=department_id,
        uploaded_by=None,
        import_status="pending",
        total_rows=0,
        valid_rows=0,
        error_rows=0
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "id": db_file.id,
        "file_name": db_file.file_name,
        "import_status": db_file.import_status,
        "department_id": db_file.department_id,
        "uploaded_at": db_file.uploaded_at
    }

# 2. POST /uploads/{upload_id}/validate
@router.post("/{upload_id}/validate")
def validate_file(upload_id: int, db: Session = Depends(get_db)):
    # Fetch file record
    db_file = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload with ID {upload_id} not found."
        )

    if not os.path.exists(db_file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server disk."
        )

    # Clear previous errors for this upload
    db.query(ImportError).filter(ImportError.upload_id == upload_id).delete()
    db.commit()

    # Perform validation
    is_valid = validate_excel_file(db_file.file_path, upload_id, db)
    
    # Reload record to get updated statistics
    db.refresh(db_file)

    return {
        "id": db_file.id,
        "file_name": db_file.file_name,
        "import_status": db_file.import_status,
        "total_rows": db_file.total_rows,
        "valid_rows": db_file.valid_rows,
        "error_rows": db_file.error_rows,
        "is_valid": is_valid
    }

# 3. GET /uploads/{upload_id}/errors
@router.get("/{upload_id}/errors")
def get_upload_errors(upload_id: int, db: Session = Depends(get_db)):
    # Verify upload exists
    db_file = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload with ID {upload_id} not found."
        )

    errors = db.query(ImportError).filter(ImportError.upload_id == upload_id).all()
    return [
        {
            "id": err.id,
            "row_index": err.row_index,
            "error_message": err.error_message,
            "raw_data": err.raw_data
        }
        for err in errors
    ]

# 4. POST /uploads/{upload_id}/import
@router.post("/{upload_id}/import")
def import_file(upload_id: int, db: Session = Depends(get_db)):
    # Verify file upload record exists
    db_file = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload with ID {upload_id} not found."
        )

    # Only import if status is Validated
    if db_file.import_status != "Validated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chỉ cho phép import file có trạng thái 'Validated'. Trạng thái hiện tại: '{db_file.import_status}'."
        )

    # Do not import if there are row-level errors
    if db_file.error_rows > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể import file vì còn tồn tại {db_file.error_rows} dòng lỗi."
        )

    # Perform importing
    try:
        imported_count = import_excel_data(db_file.file_path, upload_id, db_file.department_id, db)
        return {
            "id": db_file.id,
            "file_name": db_file.file_name,
            "import_status": "Imported",
            "imported_rows": imported_count,
            "message": "Dữ liệu đã được nạp thành công vào cơ sở dữ liệu."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

