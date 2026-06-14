from app.database import SessionLocal
from app.seed import seed_mock_data
db = SessionLocal()
seed_mock_data(db)
db.close()
print("Done seeding")
