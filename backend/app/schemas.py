from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TransactionBase(BaseModel):
    transaction_id: str
    date: datetime
    month: str
    department: str
    category: str
    transaction_type: str
    budget_amount: float
    actual_amount: float
    description: Optional[str] = None

    class Config:
        from_attributes = True

# Department Schemas
class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True

# Program Schemas
class ProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: int

class ProgramCreate(ProgramBase):
    pass

class ProgramResponse(ProgramBase):
    id: int

    class Config:
        from_attributes = True

# Category (BudgetCategory) Schemas
class CategoryResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True

# Vendor Schemas
class VendorBase(BaseModel):
    vendor_name: str
    tax_code: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorResponse(VendorBase):
    id: int

    class Config:
        from_attributes = True

# AI Chat Schemas
class ChatRequest(BaseModel):
    question: str
    department_id: Optional[int] = None
    fiscal_year: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    source_data: Optional[list] = None

class AIAskRequest(BaseModel):
    question: str
    fiscal_year: Optional[int] = None

class AIAskResponse(BaseModel):
    answer_markdown: str
    used_tools: list[str] = []

# Report Schemas
class ReportGenerateRequest(BaseModel):
    fiscal_year: int
    report_type: str  # monthly, quarterly, yearly
    department_id: Optional[int] = None
    quarter: Optional[int] = None
    month: Optional[int] = None

class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    fiscal_year: int
    quarter: Optional[int] = None
    month: Optional[int] = None
    department_id: Optional[int] = None
    content_markdown: str
    raw_data_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

