from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .routers import catalog, uploads, dashboard, alerts, chat, ask, reports, auth
from .seed import seed_mock_data

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Financial Analyst Assistant API",
    description="Backend API for MVP AI Financial Analyst Assistant",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_mock_data(db)
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(uploads.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)
app.include_router(chat.router)
app.include_router(ask.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Financial Analyst Assistant API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
