import pandas as pd
import re
from datetime import datetime

def clean_text(val):
    if pd.isna(val):
        return ""
    # Trim and reduce multiple spaces to a single space
    s = str(val).strip()
    return re.sub(r'\s+', ' ', s)

def clean_numeric(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip()
    if not val_str:
        return 0.0
    
    # Remove common currency symbols and labels
    val_str = re.sub(r'[đĐvVnNdD\s\$]', '', val_str)
    
    if not val_str:
        return 0.0

    # Detect separator usage
    if "," in val_str and "." in val_str:
        if val_str.rfind(",") > val_str.rfind("."):
            # e.g., 1.234,56 -> 1234.56
            val_str = val_str.replace(".", "").replace(",", ".")
        else:
            # e.g., 1,234.56 -> 1234.56
            val_str = val_str.replace(",", "")
    elif "," in val_str:
        # Single or multiple commas
        if val_str.count(",") > 1:
            val_str = val_str.replace(",", "")
        else:
            parts = val_str.split(",")
            if len(parts[1]) == 3:  # thousands separator, e.g., 1,200
                val_str = val_str.replace(",", "")
            else:  # decimal separator, e.g., 1200,50
                val_str = val_str.replace(",", ".")
    elif "." in val_str:
        # Single or multiple dots
        if val_str.count(".") > 1:
            val_str = val_str.replace(".", "")
        else:
            parts = val_str.split(".")
            if len(parts[1]) == 3:  # thousands separator, e.g., 1.200
                val_str = val_str.replace(".", "")
            else:  # decimal separator, e.g., 1200.50
                pass  # keep it as is
                
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def clean_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%Y-%m-%d")
    
    val_str = str(val).strip()
    if not val_str:
        return None
    
    # Common formats to check
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    # Try pandas parser as fallback
    try:
        dt = pd.to_datetime(val_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def clean_quarter(val):
    if pd.isna(val):
        return "Q1"
    
    val_str = str(val).strip().upper()
    if not val_str:
        return "Q1"
    
    # Look for digits
    match = re.search(r'[1-4]', val_str)
    if match:
        return f"Q{match.group(0)}"
    
    return "Q1"

def clean_priority(val):
    val_str = clean_text(val).lower()
    if "cao" in val_str:
        return "Cao"
    elif "thấp" in val_str or "thap" in val_str:
        return "Thấp"
    else:
        return "Trung bình"

def clean_status(val):
    val_str = clean_text(val).lower()
    if "đã thanh toán" in val_str or "da thanh toan" in val_str:
        return "Đã thanh toán"
    elif "đã duyệt" in val_str or "da duyet" in val_str:
        return "Đã duyệt"
    elif "từ chối" in val_str or "tu choi" in val_str:
        return "Từ chối"
    else:
        return "Chờ duyệt"

def clean_and_validate_formulas(df: pd.DataFrame, sheet_type: str) -> pd.DataFrame:
    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Pre-cast calculated columns to avoid pandas type mismatch errors
    for col in df.columns:
        col_clean = str(col).strip()
        if col_clean in ["Thành tiền", "Chênh lệch", "Tỷ lệ sử dụng", "VAT 10%", "Tổng thanh toán"]:
            df[col] = df[col].astype(float)
        elif col_clean in ["Cảnh báo"]:
            df[col] = df[col].astype(object)
            
    if sheet_type == "Du_toan_ngan_sach":
        # Thành tiền = Số lượng * Đơn giá
        for idx, row in df.iterrows():
            qty = clean_numeric(row.get("Số lượng", 0))
            price = clean_numeric(row.get("Đơn giá", 0))
            calc_amount = qty * price
            
            excel_amount = clean_numeric(row.get("Thành tiền", 0))
            # If difference is larger than 1.0 or empty, overwrite with calculated
            if abs(excel_amount - calc_amount) > 1.0 or pd.isna(row.get("Thành tiền")):
                df.at[idx, "Thành tiền"] = calc_amount

    elif sheet_type == "Ke_hoach_chi_tieu":
        # Chênh lệch = Thực chi - Ngân sách kế hoạch
        # Tỷ lệ sử dụng = Thực chi / Ngân sách kế hoạch
        # Cảnh báo: Tỷ lệ > 105% -> "Vượt kế hoạch", < 80% -> "Thấp hơn kế hoạch", else -> "Đúng kế hoạch"
        for idx, row in df.iterrows():
            planned = clean_numeric(row.get("Ngân sách kế hoạch", 0))
            actual = clean_numeric(row.get("Thực chi", 0))
            
            calc_variance = actual - planned
            calc_rate = actual / planned if planned > 0 else 0.0
            
            if calc_rate > 1.05:
                calc_warning = "Vượt kế hoạch"
            elif calc_rate < 0.8:
                calc_warning = "Thấp hơn kế hoạch"
            else:
                calc_warning = "Đúng kế hoạch"
                
            excel_variance = clean_numeric(row.get("Chênh lệch", 0))
            excel_rate = clean_numeric(row.get("Tỷ lệ sử dụng", 0))
            
            # Recalculate columns if difference is significant
            # Since Chênh lệch = Thực chi - Ngân sách kế hoạch, overspending is variance > 0
            if abs(excel_variance - calc_variance) > 1.0 or pd.isna(row.get("Chênh lệch")):
                df.at[idx, "Chênh lệch"] = calc_variance
                
            if abs(excel_rate - calc_rate) > 0.01 or pd.isna(row.get("Tỷ lệ sử dụng")):
                df.at[idx, "Tỷ lệ sử dụng"] = calc_rate
                
            df.at[idx, "Cảnh báo"] = calc_warning

    elif sheet_type == "De_nghi_thanh_toan":
        # VAT = Giá trị trước VAT * 10%
        # Tổng thanh toán = Giá trị trước VAT + VAT
        for idx, row in df.iterrows():
            before_vat = clean_numeric(row.get("Giá trị trước VAT", 0))
            calc_vat = before_vat * 0.1
            calc_total = before_vat + calc_vat

            # After normalize_df, the column is "VAT" (was "VAT 10%")
            excel_vat = clean_numeric(row.get("VAT", 0))
            excel_total = clean_numeric(row.get("Tổng thanh toán", 0))

            if abs(excel_vat - calc_vat) > 1.0 or pd.isna(row.get("VAT")):
                df.at[idx, "VAT"] = calc_vat

            if abs(excel_total - calc_total) > 1.0 or pd.isna(row.get("Tổng thanh toán")):
                df.at[idx, "Tổng thanh toán"] = calc_total
                
    return df

def clean_dataframe(df: pd.DataFrame, sheet_type: str) -> pd.DataFrame:
    # 1. Strip whitespace and clean text/dates/numbers column by column
    for col in df.columns:
        col_clean = str(col).strip()
        # Text fields
        if col_clean in ["Mã dự toán", "Chương trình", "Hạng mục", "Mô tả", "Đơn vị tính", "Ghi chú", 
                         "Mã đề nghị", "Nhà cung cấp", "Nội dung thanh toán", "Mã dự toán liên quan"]:
            df[col] = df[col].apply(clean_text)
        # Numbers (exclude Tháng — may be a datetime and handled separately in importer)
        elif col_clean in ["Số lượng", "Đơn giá", "Thành tiền", "Ngân sách kế hoạch", "Thực chi",
                           "Chênh lệch", "Tỷ lệ sử dụng", "Giá trị trước VAT", "VAT", "Tổng thanh toán", "Năm"]:
            df[col] = df[col].apply(clean_numeric)
        # Date
        elif col_clean in ["Ngày đề nghị"]:
            df[col] = df[col].apply(clean_date)
        # Quarter
        elif col_clean in ["Quý"]:
            df[col] = df[col].apply(clean_quarter)
        # Priority
        elif col_clean in ["Ưu tiên"]:
            df[col] = df[col].apply(clean_priority)
        # Status
        elif col_clean in ["Trạng thái"]:
            df[col] = df[col].apply(clean_status)
            
    # 2. Recalculate spreadsheet formulas
    df = clean_and_validate_formulas(df, sheet_type)
    return df
