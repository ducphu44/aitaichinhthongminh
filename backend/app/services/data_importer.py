import pandas as pd
import json
import re
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import (
    UploadedFile,
    ImportError,
    BudgetItem,
    SpendingPlan,
    PaymentRequest,
    Department,
    Program,
    BudgetCategory,
    Vendor
)
from .data_cleaning import clean_dataframe, clean_numeric, clean_text, clean_date

REQUIRED_SHEETS = ["Du_toan_ngan_sach", "Ke_hoach_chi_tieu", "De_nghi_thanh_toan"]

# Same aliases as excel_validator — maps "(VND)" variants to canonical names
COL_ALIASES = {
    "Đơn giá (VND)": "Đơn giá",
    "Thành tiền (VND)": "Thành tiền",
    "Ngân sách kế hoạch (VND)": "Ngân sách kế hoạch",
    "Thực chi (VND)": "Thực chi",
    "Chênh lệch (VND)": "Chênh lệch",
    "Giá trị trước VAT (VND)": "Giá trị trước VAT",
    "Tổng thanh toán (VND)": "Tổng thanh toán",
    "VAT 10%": "VAT",
}

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and apply column aliases."""
    df.columns = [str(c).strip() for c in df.columns]
    return df.rename(columns=COL_ALIASES)

def extract_month(val) -> int:
    """Extract month number from Tháng column (may be int or datetime)."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 1
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.month
    try:
        return int(clean_numeric(val))
    except Exception:
        return 1

def extract_year_from_date(val, fallback: int = None) -> int:
    """Extract year from a date/datetime value."""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.year
    if fallback:
        return fallback
    return datetime.now().year



def slugify_category_code(name: str) -> str:
    # Convert Vietnamese accents to unsigned English characters
    s1 = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', name.lower())
    s1 = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s1)
    s1 = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s1)
    s1 = re.sub(r'[ùúụủũưừứựửữ]', 'u', s1)
    s1 = re.sub(r'[ìíịỉĩ]', 'i', s1)
    s1 = re.sub(r'[ỳýỵỷỹ]', 'y', s1)
    s1 = re.sub(r'[đ]', 'd', s1)
    # Remove special chars and replace spaces with underscore
    s1 = re.sub(r'[^a-z0-9\s]', '', s1)
    s1 = re.sub(r'\s+', '_', s1).upper()
    return f"CP_{s1}"

def import_excel_data(file_path: str, upload_id: int, department_id: int, db: Session):
    try:
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
    except Exception as e:
        raise ValueError(f"Không thể đọc file Excel: {str(e)}")

    # Map required sheets
    sheet_mapping = {}
    for req_sheet in REQUIRED_SHEETS:
        matches = [s for s in sheet_names if s == req_sheet]
        if not matches:
            matches = [s for s in sheet_names if req_sheet.lower() in s.lower() or s.lower().endswith(req_sheet.lower())]
        if matches:
            sheet_mapping[req_sheet] = matches[0]
        else:
            raise ValueError(f"Thiếu sheet bắt buộc để thực hiện import: {req_sheet}")

    total_imported = 0
    
    # Track codes locally to prevent intra-file duplicates
    local_budget_codes = set()
    local_payment_codes = set()

    # We use a sub-transaction (nested transaction) so we can rollback if anything fails catastrophically
    try:
        # 1. PROCESS SHEET: Du_toan_ngan_sach -> budget_items
        df_dutoan = pd.read_excel(xl, sheet_name=sheet_mapping["Du_toan_ngan_sach"])
        df_dutoan = normalize_df(df_dutoan)  # rename (VND) columns
        df_dutoan = df_dutoan.dropna(how='all')
        df_dutoan = clean_dataframe(df_dutoan, "Du_toan_ngan_sach")

        for idx, row in df_dutoan.iterrows():
            budget_code = clean_text(row.get("Mã dự toán"))
            if not budget_code:
                continue
            
            # Check for duplicate in DB or current batch
            db_dup = db.query(BudgetItem).filter(BudgetItem.budget_code == budget_code).first()
            if db_dup or budget_code in local_budget_codes:
                db.add(ImportError(
                    upload_id=upload_id,
                    row_index=int(idx) + 2,
                    error_message=f"Trùng mã dự toán: '{budget_code}' đã tồn tại trong cơ sở dữ liệu hoặc trong file.",
                    raw_data=json.dumps({k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}, ensure_ascii=False)
                ))
                continue

            local_budget_codes.add(budget_code)

            # Resolve/Create Program
            prog_name = clean_text(row.get("Chương trình"))
            program_id = None
            if prog_name:
                prog = db.query(Program).filter(Program.name == prog_name, Program.department_id == department_id).first()
                if not prog:
                    prog = Program(name=prog_name, description=f"Tạo tự động từ file import {upload_id}", department_id=department_id)
                    db.add(prog)
                    db.flush()
                program_id = prog.id

            # Resolve/Create Category
            cat_name = clean_text(row.get("Hạng mục"))
            category_id = None
            if cat_name:
                cat = db.query(BudgetCategory).filter(BudgetCategory.name == cat_name).first()
                if not cat:
                    cat_code = slugify_category_code(cat_name)
                    # Check if generated code is unique
                    dup_code = db.query(BudgetCategory).filter(BudgetCategory.code == cat_code).first()
                    if dup_code:
                        cat_code = f"{cat_code}_{datetime.now().strftime('%M%S')}"
                    cat = BudgetCategory(name=cat_name, code=cat_code)
                    db.add(cat)
                    db.flush()
                category_id = cat.id

            budget_item = BudgetItem(
                department_id=department_id,
                budget_code=budget_code,
                fiscal_year=int(clean_numeric(row.get("Năm", datetime.now().year))),
                quarter=int(clean_quarter_num(row.get("Quý", 1))),
                program_id=program_id,
                category_id=category_id,
                item_name=clean_text(row.get("Hạng mục", "Không rõ")),
                description=clean_text(row.get("Mô tả")),
                unit=clean_text(row.get("Đơn vị tính")),
                quantity=int(clean_numeric(row.get("Số lượng", 0))),
                unit_price=clean_numeric(row.get("Đơn giá", 0)),
                estimated_amount=clean_numeric(row.get("Thành tiền", 0)),
                priority=clean_text(row.get("Ưu tiên")),
                status=clean_text(row.get("Trạng thái", "draft")),
                upload_id=upload_id
            )
            db.add(budget_item)
            total_imported += 1

        # 2. PROCESS SHEET: Ke_hoach_chi_tieu -> spending_plans
        df_spending = pd.read_excel(xl, sheet_name=sheet_mapping["Ke_hoach_chi_tieu"])
        df_spending = normalize_df(df_spending)  # rename (VND) columns
        df_spending = df_spending.dropna(how='all')
        df_spending = clean_dataframe(df_spending, "Ke_hoach_chi_tieu")

        for idx, row in df_spending.iterrows():
            # Tháng may be stored as a date (e.g. 2026-01-01) or plain int
            thang_raw = row.get("Tháng")
            plan_month = extract_month(thang_raw)
            # Derive fiscal_year from the Tháng date when no separate Năm column exists
            fiscal_year = extract_year_from_date(thang_raw, fallback=int(clean_numeric(row.get("Năm", datetime.now().year)) or datetime.now().year))
            # Resolve/Create Program for Ke_hoach_chi_tieu
            prog_name = clean_text(row.get("Chương trình"))
            program_id = None
            if prog_name:
                prog = db.query(Program).filter(Program.name == prog_name, Program.department_id == department_id).first()
                if not prog:
                    prog = Program(name=prog_name, description=f"Tạo tự động từ file import {upload_id}", department_id=department_id)
                    db.add(prog)
                    db.flush()
                program_id = prog.id

            planned_amount = clean_numeric(row.get("Ngân sách kế hoạch", 0))
            actual_amount = clean_numeric(row.get("Thực chi", 0))
            variance_amount = clean_numeric(row.get("Chênh lệch", 0))
            usage_rate = clean_numeric(row.get("Tỷ lệ sử dụng", 0))
            warning_status = clean_text(row.get("Cảnh báo"))
            quarter = int(clean_quarter_num(row.get("Quý", 1)))

            existing_plan = db.query(SpendingPlan).filter(
                SpendingPlan.department_id == department_id,
                SpendingPlan.fiscal_year == fiscal_year,
                SpendingPlan.plan_month == plan_month,
                SpendingPlan.program_id == program_id
            ).first()

            if existing_plan:
                existing_plan.planned_amount = planned_amount
                existing_plan.actual_amount = actual_amount
                existing_plan.variance_amount = variance_amount
                existing_plan.usage_rate = usage_rate
                existing_plan.warning_status = warning_status
                existing_plan.quarter = quarter
                existing_plan.upload_id = upload_id
            else:
                spending_plan = SpendingPlan(
                    department_id=department_id,
                    plan_month=plan_month,
                    fiscal_year=fiscal_year,
                    quarter=quarter,
                    program_id=program_id,
                    planned_amount=planned_amount,
                    actual_amount=actual_amount,
                    variance_amount=variance_amount,
                    usage_rate=usage_rate,
                    warning_status=warning_status,
                    upload_id=upload_id
                )
                db.add(spending_plan)
            total_imported += 1

        # 3. PROCESS SHEET: De_nghi_thanh_toan -> payment_requests
        df_payment = pd.read_excel(xl, sheet_name=sheet_mapping["De_nghi_thanh_toan"])
        df_payment = normalize_df(df_payment)  # rename (VND) columns
        df_payment = df_payment.dropna(how='all')
        df_payment = clean_dataframe(df_payment, "De_nghi_thanh_toan")

        for idx, row in df_payment.iterrows():
            payment_code = clean_text(row.get("Mã đề nghị"))
            if not payment_code:
                continue

            # Check duplicate in DB or batch
            db_dup = db.query(PaymentRequest).filter(PaymentRequest.payment_code == payment_code).first()
            if db_dup or payment_code in local_payment_codes:
                db.add(ImportError(
                    upload_id=upload_id,
                    row_index=int(idx) + 2,
                    error_message=f"Trùng mã đề nghị thanh toán: '{payment_code}' đã tồn tại trong cơ sở dữ liệu hoặc trong file.",
                    raw_data=json.dumps({k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}, ensure_ascii=False)
                ))
                continue

            local_payment_codes.add(payment_code)

            # Resolve/Create Vendor
            vendor_name = clean_text(row.get("Nhà cung cấp"))
            vendor_id = None
            if vendor_name:
                vendor = db.query(Vendor).filter(Vendor.vendor_name == vendor_name).first()
                if not vendor:
                    vendor = Vendor(
                        vendor_name=vendor_name,
                        tax_code=None,
                        address=None,
                        contact_person=None,
                        phone=None,
                        email=None
                    )
                    db.add(vendor)
                    db.flush()
                vendor_id = vendor.id

            ngay_de_nghi = row.get("Ngày đề nghị")
            if isinstance(ngay_de_nghi, (datetime, pd.Timestamp)):
                req_date = ngay_de_nghi if isinstance(ngay_de_nghi, datetime) else ngay_de_nghi.to_pydatetime()
            else:
                req_date_str = clean_date(ngay_de_nghi)
                req_date = datetime.strptime(req_date_str, "%Y-%m-%d") if req_date_str else datetime.now()

            # Derive fiscal_year from request date (file may not have a Năm column)
            fiscal_year = extract_year_from_date(ngay_de_nghi, fallback=int(clean_numeric(row.get("Năm", datetime.now().year)) or datetime.now().year))

            payment_request = PaymentRequest(
                department_id=department_id,
                payment_code=payment_code,
                request_date=req_date,
                fiscal_year=fiscal_year,
                quarter=int(clean_quarter_num(row.get("Quý", 1))),
                vendor_id=vendor_id,
                payment_content=clean_text(row.get("Nội dung thanh toán", "Không rõ")),
                amount_before_vat=clean_numeric(row.get("Giá trị trước VAT", 0)),
                vat_rate=10.0,  # Standard 10%
                vat_amount=clean_numeric(row.get("VAT", 0)),
                total_amount=clean_numeric(row.get("Tổng thanh toán", 0)),
                payment_status=clean_text(row.get("Trạng thái", "pending")),
                priority=clean_text(row.get("Ưu tiên")),
                related_budget_code=clean_text(row.get("Mã dự toán liên quan")),
                upload_id=upload_id
            )
            db.add(payment_request)
            total_imported += 1

        # Finalise status update for UploadedFile
        db.query(UploadedFile).filter(UploadedFile.id == upload_id).update({
            "import_status": "Imported"
        })
        db.commit()
        return total_imported

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Lỗi hệ thống nghiêm trọng xảy ra trong quá trình ghi dữ liệu: {str(e)}")

def clean_quarter_num(val) -> int:
    val_str = str(val).strip().upper()
    match = re.search(r'[1-4]', val_str)
    if match:
        return int(match.group(0))
    return 1
