from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
print("Users:", [{"email": u.email, "role": u.role} for u in users])
