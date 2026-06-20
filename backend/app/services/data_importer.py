import os
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
    "Đã thanh toán": "Thực chi",
    "Còn lại": "Chênh lệch",
    "Giá trị trước VAT (VND)": "Giá trị trước VAT",
    "Tổng thanh toán (VND)": "Tổng thanh toán",
    "VAT 10%": "VAT",
}

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and apply column aliases."""
    df.columns = [str(c).strip() for c in df.columns]
    return df.rename(columns=COL_ALIASES)

def extract_month(val) -> int:
    """Extract month number from Tháng column (may be int or datetime or 'YYYY-MM')."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 1
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.month
    val_str = str(val).strip()
    # Try YYYY-MM
    match = re.search(r'(?:^|[^0-9])(?:20\d{2})[-/](0?[1-9]|1[0-2])(?:[^0-9]|$)', val_str)
    if match:
        return int(match.group(1))
    # Try MM/YYYY
    match2 = re.search(r'(?:^|[^0-9])(0?[1-9]|1[0-2])[-/](?:20\d{2})(?:[^0-9]|$)', val_str)
    if match2:
        return int(match2.group(1))
    try:
        month_val = int(clean_numeric(val))
        return month_val if 1 <= month_val <= 12 else 1
    except Exception:
        return 1

def extract_year_from_date(val, fallback: int = None) -> int:
    """Extract year from a date/datetime value."""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.year
    val_str = str(val).strip()
    match = re.search(r'(20\d{2})', val_str)
    if match:
        return int(match.group(1))
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


def load_excel_file(file_path: str):
    """Attempt to load Excel file with openpyxl, fallback to xlrd if zip/format error."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".numbers":
        raise ValueError("Hệ thống không hỗ trợ định dạng Apple Numbers (.numbers). Vui lòng mở file bằng Numbers và chọn File -> Export To -> Excel (.xlsx) để tải lên.")

    try:
        xl = pd.ExcelFile(file_path, engine="openpyxl")
        return xl, "openpyxl"
    except Exception as e:
        err_str = str(e)
        if "Content_Types" in err_str or "zip" in err_str.lower() or "BadZipFile" in err_str:
            try:
                xl = pd.ExcelFile(file_path, engine="xlrd")
                return xl, "xlrd"
            except Exception as e2:
                raise ValueError(f"File không đúng chuẩn .xlsx và cũng không phải .xls hợp lệ. Chi tiết lỗi: {str(e2)}")
        raise ValueError(f"Lỗi đọc file: {err_str}")


def import_excel_data(file_path: str, upload_id: int, department_id: int, db: Session, dry_run: bool = False):
    try:
        xl, engine = load_excel_file(file_path)
        sheet_names = xl.sheet_names
    except ValueError:
        raise
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
    local_spending_keys = set()

    inserted = 0
    updated = 0
    unchanged = 0
    preview_details = []

    ATTR_TO_EXCEL = {
        "item_name": "Hạng mục",
        "description": "Mô tả",
        "unit": "Đơn vị tính",
        "quantity": "Số lượng",
        "unit_price": "Đơn giá",
        "estimated_amount": "Thành tiền",
        "priority": "Ưu tiên",
        "status": "Trạng thái",
        "fiscal_year": "Năm",
        "quarter": "Quý",
        "plan_month": "Tháng",
        "department_id": "Mã phòng ban",
        "program_id": "Mã chương trình",
        "category_id": "Mã hạng mục",
        "amount": "Số tiền",
        "request_date": "Ngày đề nghị",
        "payment_date": "Ngày thanh toán",
        "approver": "Người phê duyệt"
    }

    def add_preview(sheet: str, code: str, action: str, details: list):
        if len(preview_details) < 50:
            preview_details.append({
                "sheet": sheet,
                "code": code,
                "action": action,
                "details": details
            })

    def apply_updates(obj, new_attrs):
        changes = []
        for k, v in new_attrs.items():
            old_v = getattr(obj, k)
            if old_v != v:
                col_name = ATTR_TO_EXCEL.get(k, k)
                changes.append({
                    "column": col_name,
                    "old": old_v,
                    "new": v
                })
                setattr(obj, k, v)
        return changes

    # We use a sub-transaction (nested transaction) so we can rollback if anything fails catastrophically
    try:
        # 1. PROCESS SHEET: Du_toan_ngan_sach -> budget_items
        df_dutoan = pd.read_excel(xl, sheet_name=sheet_mapping["Du_toan_ngan_sach"], engine=engine)
        df_dutoan = normalize_df(df_dutoan)  # rename (VND) columns
        df_dutoan = df_dutoan.dropna(how='all')
        df_dutoan = clean_dataframe(df_dutoan, "Du_toan_ngan_sach")

        for idx, row in df_dutoan.iterrows():
            budget_code = clean_text(row.get("Mã dự toán"))
            if not budget_code:
                continue
            # Check duplicate in current file batch
            if budget_code in local_budget_codes:
                db.add(ImportError(
                    upload_id=upload_id,
                    row_index=int(idx) + 2,
                    error_message=f"Trúng mã dự toán: '{budget_code}' đã tồn tại trong file.",
                    raw_data=json.dumps({k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}, ensure_ascii=False, default=str)
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

            new_attrs = {
                "department_id": department_id,
                "fiscal_year": int(clean_numeric(row.get("Năm", datetime.now().year))),
                "quarter": int(clean_quarter_num(row.get("Quý", 1))),
                "program_id": program_id,
                "category_id": category_id,
                "item_name": clean_text(row.get("Hạng mục", "Không rõ")),
                "description": clean_text(row.get("Mô tả")),
                "unit": clean_text(row.get("Đơn vị tính")),
                "quantity": int(clean_numeric(row.get("Số lượng", 0))),
                "unit_price": clean_numeric(row.get("Đơn giá", 0)),
                "estimated_amount": clean_numeric(row.get("Thành tiền", 0)),
                "priority": clean_text(row.get("Ưu tiên")),
                "status": clean_text(row.get("Trạng thái", "draft"))
            }

            db_dup = db.query(BudgetItem).filter(BudgetItem.budget_code == budget_code).first()
            if db_dup:
                changed_keys = apply_updates(db_dup, new_attrs)
                if changed_keys:
                    db_dup.upload_id = upload_id
                    updated += 1
                    add_preview("Dự toán ngân sách", budget_code, "Cập nhật", changed_keys)
                else:
                    db_dup.upload_id = upload_id
                    unchanged += 1
            else:
                budget_item = BudgetItem(
                    budget_code=budget_code,
                    upload_id=upload_id,
                    **new_attrs
                )
                db.add(budget_item)
                inserted += 1
                insert_details = []
                for k in ["item_name", "quantity", "unit_price", "estimated_amount"]:
                    if k in new_attrs and new_attrs[k]:
                        insert_details.append({
                            "column": ATTR_TO_EXCEL.get(k, k),
                            "old": "-",
                            "new": new_attrs[k]
                        })
                add_preview("Dự toán ngân sách", budget_code, "Thêm mới", insert_details)

        db.flush()

        # 2. PROCESS SHEET: Ke_hoach_chi_tieu -> spending_plans
        df_spending = pd.read_excel(xl, sheet_name=sheet_mapping["Ke_hoach_chi_tieu"], engine=engine)
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

            spending_key = (department_id, fiscal_year, plan_month, program_id)
            if spending_key in local_spending_keys:
                db.add(ImportError(
                    upload_id=upload_id,
                    row_index=int(idx) + 2,
                    error_message=f"Trùng kế hoạch chi tiêu: Tháng {plan_month}/{fiscal_year} cho Chương trình này đã tồn tại trong file.",
                    raw_data=json.dumps({k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}, ensure_ascii=False, default=str)
                ))
                continue
            
            local_spending_keys.add(spending_key)

            new_attrs = {
                "planned_amount": planned_amount,
                "actual_amount": actual_amount,
                "variance_amount": variance_amount,
                "usage_rate": usage_rate,
                "warning_status": warning_status,
                "quarter": quarter
            }

            if existing_plan:
                changed_keys = apply_updates(existing_plan, new_attrs)
                if changed_keys:
                    existing_plan.upload_id = upload_id
                    updated += 1
                    add_preview("Kế hoạch chi tiêu", f"Tháng {plan_month}/{fiscal_year}", "Cập nhật", changed_keys)
                else:
                    existing_plan.upload_id = upload_id
                    unchanged += 1
            else:
                spending_plan = SpendingPlan(
                    department_id=department_id,
                    plan_month=plan_month,
                    fiscal_year=fiscal_year,
                    program_id=program_id,
                    upload_id=upload_id,
                    **new_attrs
                )
                db.add(spending_plan)
                inserted += 1
                insert_details = []
                for k in ["item_name", "amount", "status"]:
                    if k in new_attrs and new_attrs[k]:
                        insert_details.append({
                            "column": ATTR_TO_EXCEL.get(k, k),
                            "old": "-",
                            "new": new_attrs[k]
                        })
                add_preview("Kế hoạch chi tiêu", f"Tháng {plan_month}/{fiscal_year}", "Thêm mới", insert_details)

        db.flush()

        # 3. PROCESS SHEET: De_nghi_thanh_toan -> payment_requests
        df_payment = pd.read_excel(xl, sheet_name=sheet_mapping["De_nghi_thanh_toan"], engine=engine)
        df_payment = normalize_df(df_payment)  # rename (VND) columns
        df_payment = df_payment.dropna(how='all')
        df_payment = clean_dataframe(df_payment, "De_nghi_thanh_toan")

        for idx, row in df_payment.iterrows():
            payment_code = clean_text(row.get("Mã đề nghị"))
            if not payment_code:
                continue

            # Check duplicate in current file batch
            if payment_code in local_payment_codes:
                db.add(ImportError(
                    upload_id=upload_id,
                    row_index=int(idx) + 2,
                    error_message=f"Trúng mã đề nghị thanh toán: '{payment_code}' đã tồn tại trong file.",
                    raw_data=json.dumps({k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}, ensure_ascii=False, default=str)
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

            db_dup = db.query(PaymentRequest).filter(PaymentRequest.payment_code == payment_code).first()
            new_attrs = {
                "department_id": department_id,
                "request_date": req_date,
                "fiscal_year": fiscal_year,
                "quarter": int(clean_quarter_num(row.get("Quý", 1))),
                "vendor_id": vendor_id,
                "payment_content": clean_text(row.get("Nội dung thanh toán", "Không rõ")),
                "amount_before_vat": clean_numeric(row.get("Giá trị trước VAT", 0)),
                "vat_rate": 10.0,
                "vat_amount": clean_numeric(row.get("VAT", 0)),
                "total_amount": clean_numeric(row.get("Tổng thanh toán", 0)),
                "payment_status": clean_text(row.get("Trạng thái", "pending")),
                "priority": clean_text(row.get("Ưu tiên")),
                "related_budget_code": clean_text(row.get("Mã dự toán liên quan"))
            }

            if db_dup:
                changed_keys = apply_updates(db_dup, new_attrs)
                if changed_keys:
                    db_dup.upload_id = upload_id
                    updated += 1
                    add_preview("Đề nghị thanh toán", payment_code, "Cập nhật", changed_keys)
                else:
                    db_dup.upload_id = upload_id
                    unchanged += 1
            else:
                payment_request = PaymentRequest(
                    payment_code=payment_code,
                    upload_id=upload_id,
                    **new_attrs
                )
                db.add(payment_request)
                inserted += 1
                insert_details = []
                for k in ["item_name", "amount", "status"]:
                    if k in new_attrs and new_attrs[k]:
                        insert_details.append({
                            "column": ATTR_TO_EXCEL.get(k, k),
                            "old": "-",
                            "new": new_attrs[k]
                        })
                add_preview("Đề nghị thanh toán", payment_code, "Thêm mới", insert_details)

        if not dry_run:
            # Finalise status update for UploadedFile
            db.query(UploadedFile).filter(UploadedFile.id == upload_id).update({
                "import_status": "Imported",
                "inserted_rows": inserted,
                "updated_rows": updated,
                "preview_details": json.dumps(preview_details, ensure_ascii=False) if preview_details else None
            })
            db.commit()
        else:
            db.rollback()
        return {
            "inserted": inserted,
            "updated": updated,
            "unchanged": unchanged,
            "preview_details": preview_details
        }

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Lỗi hệ thống nghiêm trọng xảy ra trong quá trình ghi dữ liệu: {str(e)}")

def clean_quarter_num(val) -> int:
    val_str = str(val).strip().upper()
    match = re.search(r'[1-4]', val_str)
    if match:
        return int(match.group(0))
    return 1
