from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)

class Program(Base):
    __tablename__ = "programs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String, nullable=False)
    tax_code = Column(String, nullable=True)
    address = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="finance_staff")
    is_active = Column(Integer, default=1)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    import_status = Column(String, default="pending", nullable=False)
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    inserted_rows = Column(Integer, default=0)
    updated_rows = Column(Integer, default=0)
    preview_details = Column(Text, nullable=True)

class BudgetItem(Base):
    __tablename__ = "budget_items"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    budget_code = Column(String, nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=True)
    item_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String, nullable=True)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0.0)
    estimated_amount = Column(Float, default=0.0)
    priority = Column(String, nullable=True)
    status = Column(String, default="draft")
    upload_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)

class SpendingPlan(Base):
    __tablename__ = "spending_plans"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    plan_month = Column(Integer, nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    planned_amount = Column(Float, default=0.0)
    actual_amount = Column(Float, default=0.0)
    variance_amount = Column(Float, default=0.0)
    usage_rate = Column(Float, default=0.0)
    warning_status = Column(String, nullable=True)
    upload_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)

class PaymentRequest(Base):
    __tablename__ = "payment_requests"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    payment_code = Column(String, nullable=False)
    request_date = Column(DateTime, nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    payment_content = Column(Text, nullable=False)
    amount_before_vat = Column(Float, default=0.0)
    vat_rate = Column(Float, default=0.0)
    vat_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String, default="pending")
    priority = Column(String, nullable=True)
    related_budget_code = Column(String, nullable=True)
    upload_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)

class ImportError(Base):
    __tablename__ = "import_errors"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)
    row_index = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=False)
    raw_data = Column(Text, nullable=True)

class AIQuery(Base):
    __tablename__ = "ai_queries"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    content_markdown = Column(Text, nullable=False)
    raw_data_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
