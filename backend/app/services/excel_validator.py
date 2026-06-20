import os
import pandas as pd
import json
from sqlalchemy.orm import Session
from ..models import UploadedFile, ImportError
from .data_cleaning import clean_dataframe

REQUIRED_SHEETS = {
    "Du_toan_ngan_sach": [
        "Mã dự toán", "Năm", "Quý", "Chương trình", "Hạng mục", "Mô tả",
        "Đơn vị tính", "Số lượng",
    ],
    "Ke_hoach_chi_tieu": [
        "Tháng", "Quý", "Chương trình",
    ],
    "De_nghi_thanh_toan": [
        "Mã đề nghị", "Ngày đề nghị", "Quý", "Chương trình", "Nhà cung cấp",
        "Nội dung thanh toán", "Trạng thái",
    ],
}

# Canonical column name lookup: maps alternative spellings → canonical name used in validation
COL_ALIASES = {
    # Du_toan_ngan_sach
    "Đơn giá (VND)": "Đơn giá",
    "Thành tiền (VND)": "Thành tiền",
    # Ke_hoach_chi_tieu
    "Ngân sách kế hoạch (VND)": "Ngân sách kế hoạch",
    "Thực chi (VND)": "Thực chi",
    "Chênh lệch (VND)": "Chênh lệch",
    "Đã thanh toán": "Thực chi",
    "Còn lại": "Chênh lệch",
    # De_nghi_thanh_toan
    "Giá trị trước VAT (VND)": "Giá trị trước VAT",
    "Tổng thanh toán (VND)": "Tổng thanh toán",
    "VAT 10%": "VAT",
}

def normalize_columns(df):
    """Rename columns using COL_ALIASES so downstream code uses canonical names."""
    return df.rename(columns=COL_ALIASES)

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
        # Nếu lỗi liên quan đến zip (đặc trưng của việc dùng openpyxl đọc file .xls)
        if "Content_Types" in err_str or "zip" in err_str.lower() or "BadZipFile" in err_str:
            try:
                xl = pd.ExcelFile(file_path, engine="xlrd")
                return xl, "xlrd"
            except Exception as e2:
                raise ValueError(f"File không đúng chuẩn .xlsx và cũng không phải .xls hợp lệ. Chi tiết lỗi: {str(e2)}")
        raise ValueError(f"Lỗi đọc file: {err_str}")


def validate_excel_file(file_path: str, upload_id: int, db: Session):
    try:
        # Load the Excel file to read sheet names
        xl, engine = load_excel_file(file_path)
        sheet_names = xl.sheet_names
    except ValueError as e:
        # File could not be read as Excel
        db.add(ImportError(
            upload_id=upload_id,
            row_index=0,
            error_message=f"Không thể đọc file Excel. Định dạng không hợp lệ hoặc file bị lỗi: {str(e)}",
            raw_data=None
        ))
        db.query(UploadedFile).filter(UploadedFile.id == upload_id).update({
            "import_status": "Failed",
            "total_rows": 0,
            "valid_rows": 0,
            "error_rows": 1
        })
        db.commit()
        return False
    except Exception as e:
        db.add(ImportError(
            upload_id=upload_id,
            row_index=0,
            error_message=f"Không thể đọc file Excel. Định dạng không hợp lệ hoặc file bị lỗi: {str(e)}",
            raw_data=None
        ))
        db.query(UploadedFile).filter(UploadedFile.id == upload_id).update({
            "import_status": "Failed",
            "total_rows": 0,
            "valid_rows": 0,
            "error_rows": 1
        })
        db.commit()
        return False

    errors_logged = 0
    total_rows = 0
    valid_rows = 0
    error_rows = 0
    
    # Map required sheets to actual sheet names in the file
    sheet_mapping = {}
    missing_sheets = []
    for req_sheet in REQUIRED_SHEETS.keys():
        # Exact match
        matches = [s for s in sheet_names if s == req_sheet]
        if not matches:
            # Suffix/substring match (e.g. '01_Du_toan_ngan_sach' matches 'Du_toan_ngan_sach')
            matches = [s for s in sheet_names if req_sheet.lower() in s.lower() or s.lower().endswith(req_sheet.lower())]
        
        if matches:
            sheet_mapping[req_sheet] = matches[0]
        else:
            missing_sheets.append(req_sheet)

    if missing_sheets:
        for sheet in missing_sheets:
            db.add(ImportError(
                upload_id=upload_id,
                row_index=0,
                error_message=f"Thiếu sheet bắt buộc: '{sheet}'",
                raw_data=None
            ))
            errors_logged += 1
        db.query(UploadedFile).filter(UploadedFile.id == upload_id).update({
            "import_status": "Failed",
            "total_rows": 0,
            "valid_rows": 0,
            "error_rows": errors_logged
        })
        db.commit()
        return False

    # Validate each sheet
    for sheet_name, required_cols in REQUIRED_SHEETS.items():
        actual_sheet_name = sheet_mapping[sheet_name]
        try:
            # Read sheet
            df = pd.read_excel(xl, sheet_name=actual_sheet_name, engine=engine)
            # Normalize column names (strip whitespace + apply aliases)
            df.columns = [str(col).strip() for col in df.columns]
            df = normalize_columns(df)
            # Remove completely empty rows
            df = df.dropna(how='all')
            sheet_total_rows = len(df)
            total_rows += sheet_total_rows

            # Check required columns (after normalization)
            actual_cols = list(df.columns)
            missing_cols = [col for col in required_cols if col not in actual_cols]

            if missing_cols:
                db.add(ImportError(
                    upload_id=upload_id,
                    row_index=0,
                    error_message=f"Sheet '{sheet_name}' thiếu các cột bắt buộc: {', '.join(missing_cols)}",
                    raw_data=None
                ))
                errors_logged += 1
                error_rows += sheet_total_rows
                continue

            # Clean dataframe before row-level validation
            df = clean_dataframe(df, sheet_name)

            # Row level checks if columns are present
            sheet_error_rows = 0
            for idx, row in df.iterrows():
                # Store row data as JSON
                row_dict = row.to_dict()
                # Clean NaNs for JSON serialization
                row_clean = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                row_json = json.dumps(row_clean, ensure_ascii=False, default=str)

                # Check for empty critical cells
                row_errors = []

                # Sheet-specific cell validations (use canonical names after normalize_columns)
                if sheet_name == "Du_toan_ngan_sach":
                    if pd.isna(row.get("Mã dự toán")):
                        row_errors.append("Mã dự toán không được để trống")
                    # Thành tiền may come from "Thành tiền (VND)" → normalized to "Thành tiền"
                    thanh_tien = row.get("Thành tiền")
                    if thanh_tien is None or pd.isna(thanh_tien):
                        row_errors.append("Thành tiền không được để trống")

                elif sheet_name == "Ke_hoach_chi_tieu":
                    if pd.isna(row.get("Tháng")):
                        row_errors.append("Tháng không được để trống")
                    ns_ke_hoach = row.get("Ngân sách kế hoạch")
                    if ns_ke_hoach is None or pd.isna(ns_ke_hoach):
                        row_errors.append("Ngân sách kế hoạch không được để trống")

                elif sheet_name == "De_nghi_thanh_toan":
                    if pd.isna(row.get("Mã đề nghị")):
                        row_errors.append("Mã đề nghị không được để trống")
                    tong_tt = row.get("Tổng thanh toán")
                    if tong_tt is None or pd.isna(tong_tt):
                        row_errors.append("Tổng thanh toán không được để trống")

                if row_errors:
                    db.add(ImportError(
                        upload_id=upload_id,
                        row_index=int(idx) + 2,  # 1-based, +1 for header
                        error_message=f"Lỗi tại sheet '{sheet_name}', dòng {int(idx) + 2}: {'; '.join(row_errors)}",
                        raw_data=row_json
                    ))
                    sheet_error_rows += 1
                    errors_logged += 1

            error_rows += sheet_error_rows
            valid_rows += (sheet_total_rows - sheet_error_rows)

        except Exception as e:
            db.add(ImportError(
                upload_id=upload_id,
                row_index=0,
                error_message=f"Lỗi khi xử lý sheet '{sheet_name}': {str(e)}",
                raw_data=None
            ))
            errors_logged += 1

    status = "Failed" if errors_logged > 0 else "Validated"
    
    db.query(UploadedFile).filter(UploadedFile.id == upload_id).update({
        "import_status": status,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "error_rows": error_rows
    })
    db.commit()
    return errors_logged == 0
