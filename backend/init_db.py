import sys
import os

# Add the directory containing the app package to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
sys.path.append(os.path.dirname(__file__))

from app.database import Base, engine, SessionLocal
from app.models import Department, Program, BudgetCategory, Vendor

def init_db():
    # Drop and recreate tables to ensure new columns are created
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()
    try:
        # Seed initial departments
        initial_departments = [
            {"name": "Phòng CNTT", "code": "CNTT"},
            {"name": "Phòng Marketing Truyền thông", "code": "MKT"},
            {"name": "Phòng Tuyển sinh", "code": "TS"},
            {"name": "Phòng Công tác Sinh viên", "code": "CTSV"},
            {"name": "Phòng Hợp tác Doanh nghiệp & Phát triển", "code": "HTDN"},
            {"name": "Phòng Hợp tác Học thuật", "code": "HTHT"},
        ]

        print("Seeding initial departments...")
        dept_map = {}
        for dept_data in initial_departments:
            dept = Department(name=dept_data["name"], code=dept_data["code"])
            db.add(dept)
            db.flush()  # Flush to get the generated ID
            dept_map[dept.code] = dept.id
            print(f"Added department: {dept.name} ({dept.code}) with ID {dept.id}")

        # Seed initial programs
        initial_programs = [
            {"name": "Nâng cấp hệ thống mạng nội bộ", "description": "Nâng cấp switch và access point", "dept_code": "CNTT"},
            {"name": "Mua bản quyền Office 365 và Cloud", "description": "Bản quyền năm học mới", "dept_code": "CNTT"},
            {"name": "Chiến dịch tuyển sinh Hè 2026", "description": "Chạy ads và tư vấn tuyển sinh", "dept_code": "TS"},
            {"name": "Tổ chức sự kiện Hướng nghiệp", "description": "Ngày hội việc làm cho sinh viên", "dept_code": "HTDN"},
            {"name": "Chào tân sinh viên 2026", "description": "Sự kiện chào đón khóa mới", "dept_code": "CTSV"},
        ]

        print("Seeding initial programs...")
        for prog_data in initial_programs:
            dept_id = dept_map.get(prog_data["dept_code"])
            if dept_id:
                prog = Program(
                    name=prog_data["name"],
                    description=prog_data["description"],
                    department_id=dept_id
                )
                db.add(prog)
                print(f"Added program: {prog.name} for department {prog_data['dept_code']}")

        # Seed initial budget categories
        initial_categories = [
            {"name": "Chi phí lương và phụ cấp", "code": "CP_LUONG"},
            {"name": "Chi phí văn phòng phẩm", "code": "CP_VPP"},
            {"name": "Chi phí thiết bị, phần mềm", "code": "CP_TB"},
            {"name": "Chi phí Marketing, quảng cáo", "code": "CP_MKT"},
            {"name": "Chi phí sự kiện, hội thảo", "code": "CP_SKE"},
        ]

        print("Seeding initial budget categories...")
        for cat_data in initial_categories:
            cat = BudgetCategory(name=cat_data["name"], code=cat_data["code"])
            db.add(cat)
            print(f"Added category: {cat.name} ({cat.code})")

        # Seed initial vendors
        initial_vendors = [
            {
                "vendor_name": "Công ty Cổ phần Thế giới Di động",
                "tax_code": "0303217354",
                "address": "128 Trần Quang Khải, Q.1, TP.HCM",
                "contact_person": "Nguyễn Văn A",
                "phone": "02838125960",
                "email": "contact@mwg.vn"
            },
            {
                "vendor_name": "Công ty Cổ phần Bán lẻ Kỹ thuật số FPT",
                "tax_code": "0311609355",
                "address": "261 Khánh Hội, Q.4, TP.HCM",
                "contact_person": "Trần Thị B",
                "phone": "02873023456",
                "email": "info@fptshop.com.vn"
            },
            {
                "vendor_name": "Công ty TNHH Truyền thông & Giải trí Star",
                "tax_code": "0109876543",
                "address": "15 Lê Lợi, Q. Hoàn Kiếm, Hà Nội",
                "contact_person": "Lê Văn C",
                "phone": "02439876543",
                "email": "sales@staragency.vn"
            }
        ]

        print("Seeding initial vendors...")
        for vendor_data in initial_vendors:
            vendor = Vendor(
                vendor_name=vendor_data["vendor_name"],
                tax_code=vendor_data["tax_code"],
                address=vendor_data["address"],
                contact_person=vendor_data["contact_person"],
                phone=vendor_data["phone"],
                email=vendor_data["email"]
            )
            db.add(vendor)
            print(f"Added vendor: {vendor.vendor_name}")

        db.commit()
        print("Database seeding completed.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
