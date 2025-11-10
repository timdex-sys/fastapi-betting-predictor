from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from db import SessionLocal, engine
from models_db import Base, GamePrediction
from retrain import fetch_latest_matches_and_update_db

# --- Initialize FastAPI ---
app = FastAPI(title="Betting Predictor API", version="2.0")

# --- Setup templates and static folders ---
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
templates = Jinja2Templates(directory="dashboard/templates")

# --- Initialize DB ---
Base.metadata.create_all(bind=engine)

# --- Database session dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Background job: auto-refresh matches ---
def refresh_matches_job():
    print(f"[{datetime.now()}] Refreshing matches automatically...")
    fetch_latest_matches_and_update_db()

scheduler = BackgroundScheduler()
scheduler.add_job(refresh_matches_job, "interval", hours=6)
scheduler.start()

# --- Home route ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    """Render the dashboard with today's matches."""
    today = datetime.now().date()
    matches = db.query(GamePrediction).filter(GamePrediction.match_date == today).all()
    return templates.TemplateResponse("index.html", {"request": request, "matches": matches})

# --- API route: Refresh matches manually ---
@app.get("/refresh", response_class=HTMLResponse)
def refresh_data(request: Request, db: Session = Depends(get_db)):
    """Fetch latest matches from external sources and refresh dashboard."""
    fetch_latest_matches_and_update_db()
    today = datetime.now().date()
    matches = db.query(GamePrediction).filter(GamePrediction.match_date == today).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "matches": matches, "message": "Data refreshed successfully!"}
    )

# --- API health check ---
@app.get("/api/status")
def status():
    return {"status": "running", "message": "Betting predictor API is live!"}

# --- Shutdown event ---
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    print("Scheduler stopped cleanly.")
