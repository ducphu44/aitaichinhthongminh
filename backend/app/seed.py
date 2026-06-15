from sqlalchemy.orm import Session
from app.models import Department, Program, SpendingPlan, PaymentRequest, User
import random
from datetime import datetime
from app.auth import get_password_hash

def seed_mock_data(db: Session):
    # Seed Users independently
    if db.query(User).count() == 0:
        hashed_pw = get_password_hash("password123")
        users = [
            User(email="admin@abc.com", hashed_password=hashed_pw, role="admin"),
            User(email="leader@abc.com", hashed_password=hashed_pw, role="leader")
        ]
        db.add_all(users)
        db.commit()
        
        # Add staff and manager with department_id if departments exist later
    
    depts_data = [
        {"name": "Phòng Đào Tạo", "code": "DT01"},
        {"name": "Phòng Hành Chính", "code": "HC01"},
        {"name": "Phòng Tài Chính", "code": "TC01"},
        {"name": "Phòng CNTT", "code": "CNTT"},
        {"name": "Phòng Marketing Truyền thông", "code": "MKT"},
        {"name": "Phòng Tuyển sinh", "code": "TS"},
        {"name": "Phòng Công tác Sinh viên", "code": "CTSV"},
        {"name": "Phòng Hợp tác Doanh nghiệp & Phát triển", "code": "HTDN"},
        {"name": "Phòng Hợp tác Học thuật", "code": "HTHT"},
    ]
    
    # Check if data already exists
    if db.query(Department).count() > 0:
        # Check if we need to add missing departments
        existing_codes = {d.code for d in db.query(Department).all()}
        new_depts = []
        for d_data in depts_data:
            if d_data["code"] not in existing_codes:
                new_depts.append(Department(name=d_data["name"], code=d_data["code"]))
        if new_depts:
            db.add_all(new_depts)
            db.commit()

        # Check if staff and manager need to be updated with department
        staff = db.query(User).filter(User.email == "staff@abc.com").first()
        if not staff:
            depts = db.query(Department).all()
            if depts:
                hashed_pw = get_password_hash("password123")
                users = [
                    User(email="staff@abc.com", hashed_password=hashed_pw, role="finance_staff", department_id=depts[0].id),
                    User(email="manager@abc.com", hashed_password=hashed_pw, role="finance_manager", department_id=depts[0].id),
                ]
                db.add_all(users)
                db.commit()
        return

    print("Seeding mock data for demo...")
    
    # 1. Seed Departments
    depts = [
        Department(name="Phòng Đào Tạo", code="DT01"),
        Department(name="Phòng Hành Chính", code="HC01"),
        Department(name="Phòng Tài Chính", code="TC01"),
        Department(name="Phòng CNTT", code="CNTT"),
        Department(name="Phòng Marketing Truyền thông", code="MKT"),
        Department(name="Phòng Tuyển sinh", code="TS"),
        Department(name="Phòng Công tác Sinh viên", code="CTSV"),
        Department(name="Phòng Hợp tác Doanh nghiệp & Phát triển", code="HTDN"),
        Department(name="Phòng Hợp tác Học thuật", code="HTHT"),
    ]
    db.add_all(depts)
    db.commit()
    
    # Refresh to get IDs
    for d in depts:
        db.refresh(d)
        
    # 2. Seed Programs
    programs = [
        Program(name="Chương trình Chuyển đổi số", department_id=depts[0].id),
        Program(name="Nâng cấp Hạ tầng", department_id=depts[1].id),
        Program(name="Tổ chức Sự kiện Tuyển sinh", department_id=depts[0].id),
    ]
    db.add_all(programs)
    db.commit()
    for p in programs:
        db.refresh(p)
        
    # 3. Seed SpendingPlans for 2026
    plans = []
    for dept in depts:
        for month in range(1, 13):
            # Generate random realistic budgets
            planned = random.randint(100, 500) * 1000000
            
            # Create some variance (over budget or under budget)
            actual_variance = random.uniform(0.7, 1.2)
            actual = int(planned * actual_variance)
            
            plans.append(SpendingPlan(
                department_id=dept.id,
                plan_month=month,
                fiscal_year=2026,
                quarter=(month - 1) // 3 + 1,
                program_id=random.choice(programs).id,
                planned_amount=planned,
                actual_amount=actual,
                variance_amount=planned - actual,
                usage_rate=round(actual / planned, 2),
                warning_status="Overbudget" if actual > planned else "Normal"
            ))
            
    db.add_all(plans)
    
    # 5. Seed Users (staff and manager) if not seeded above
    staff = db.query(User).filter(User.email == "staff@abc.com").first()
    if not staff:
        hashed_pw = get_password_hash("password123")
        users = [
            User(email="staff@abc.com", hashed_password=hashed_pw, role="finance_staff", department_id=depts[2].id),
            User(email="manager@abc.com", hashed_password=hashed_pw, role="finance_manager", department_id=depts[2].id),
        ]
        db.add_all(users)
        db.commit()

    # 6. Seed Payment Requests
    requests = []
    for i in range(10):
        amount = random.randint(10, 100) * 1000000
        status = random.choice(["pending", "approved", "rejected"])
        requests.append(PaymentRequest(
            department_id=random.choice(depts).id,
            payment_code=f"PMT-2026-{i:03d}",
            request_date=datetime(2026, random.randint(1, 12), random.randint(1, 28)),
            fiscal_year=2026,
            quarter=1,
            payment_content=f"Thanh toán chi phí số {i}",
            total_amount=amount,
            payment_status=status
        ))
    db.add_all(requests)
    
    db.commit()
    print("Mock data seeded successfully.")
