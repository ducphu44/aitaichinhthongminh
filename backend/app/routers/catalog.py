from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Department, Program, BudgetCategory, Vendor
from ..schemas import (
    DepartmentResponse,
    ProgramCreate,
    ProgramResponse,
    CategoryResponse,
    VendorCreate,
    VendorResponse
)

router = APIRouter(
    prefix="",
    tags=["Catalog"],
)

# 1. GET /departments
@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    try:
        departments = db.query(Department).all()
        return departments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving departments: {str(e)}"
        )

# 2. GET /programs
@router.get("/programs", response_model=List[ProgramResponse])
def get_programs(db: Session = Depends(get_db)):
    try:
        programs = db.query(Program).all()
        return programs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving programs: {str(e)}"
        )

# 3. GET /categories (using BudgetCategory model)
@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    try:
        categories = db.query(BudgetCategory).all()
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving categories: {str(e)}"
        )

# 4. GET /vendors
@router.get("/vendors", response_model=List[VendorResponse])
def get_vendors(db: Session = Depends(get_db)):
    try:
        vendors = db.query(Vendor).all()
        return vendors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving vendors: {str(e)}"
        )

# 5. POST /vendors
@router.post("/vendors", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(vendor_in: VendorCreate, db: Session = Depends(get_db)):
    try:
        # Check if vendor with the same tax code already exists (if tax code is provided)
        if vendor_in.tax_code:
            existing = db.query(Vendor).filter(Vendor.tax_code == vendor_in.tax_code).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vendor with tax code {vendor_in.tax_code} already exists."
                )

        new_vendor = Vendor(
            vendor_name=vendor_in.vendor_name,
            tax_code=vendor_in.tax_code,
            address=vendor_in.address,
            contact_person=vendor_in.contact_person,
            phone=vendor_in.phone,
            email=vendor_in.email
        )
        db.add(new_vendor)
        db.commit()
        db.refresh(new_vendor)
        return new_vendor
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating vendor: {str(e)}"
        )

# 6. POST /programs
@router.post("/programs", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(program_in: ProgramCreate, db: Session = Depends(get_db)):
    try:
        # Check if the department exists
        dept = db.query(Department).filter(Department.id == program_in.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with ID {program_in.department_id} does not exist."
            )

        new_program = Program(
            name=program_in.name,
            description=program_in.description,
            department_id=program_in.department_id
        )
        db.add(new_program)
        db.commit()
        db.refresh(new_program)
        return new_program
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating program: {str(e)}"
        )
