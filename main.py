from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date
from db import SessionLocal, engine
from models_db import Base, MatchPrediction

# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from datetime import timedelta

@app.get("/filter/{day}")
def filter_by_day(request: Request, day: str):
    db = next(get_db())
    today = date.today()

    if day == "tomorrow":
        target_date = today + timedelta(days=1)
    elif day == "all":
        matches = db.query(MatchPrediction).all()
        target_date = None
    else:
        target_date = today

    if target_date:
        matches = db.query(MatchPrediction).filter(MatchPrediction.match_date == target_date).all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "today": target_date or "All", "matches": matches}
    )

