# main.py
import os
import json
import smtplib
from email.mime.text import MIMEText
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from db import SessionLocal
from models_db import MatchPrediction, Base
import retrain  # the module we created above

# Initialize app and templates
app = FastAPI(title="Betting Predictor")
templates = Jinja2Templates(directory="dashboard/templates")
if os.path.isdir("dashboard/static"):
    app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# ensure DB tables exist
from db import engine
Base.metadata.create_all(bind=engine)

# email config (ENV)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

def send_email(subject: str, body: str):
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECIPIENT:
        print("[Email] SMTP not configured; skipping email.")
        return
    try:
        msg = MIMEText(body)
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT
        msg["Subject"] = subject

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("[Email] Sent.")
    except Exception as e:
        print("[Email] Failed to send:", e)


# Dashboard route (pulls today's matches from DB)
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    try:
        today = date.today()
        rows = db.query(MatchPrediction).filter(MatchPrediction.match_date == today).order_by(MatchPrediction.home_team).all()
        # convert to list of dicts for template
        matches = []
        for r in rows:
            matches.append({
                "home_team": r.home_team,
                "away_team": r.away_team,
                "prediction": r.prediction,
                "win_probability": r.win_probability,
                "odds": r.odds
            })
        return templates.TemplateResponse("index.html", {"request": request, "today": today.isoformat(), "matches": matches})
    finally:
        db.close()


# JSON API for today's predictions (useful for front-end js)
@app.get("/api/predictions/today")
def api_predictions_today():
    db = SessionLocal()
    try:
        today = date.today()
        rows = db.query(MatchPrediction).filter(MatchPrediction.match_date == today).order_by(MatchPrediction.home_team).all()
        out = [{
            "home_team": r.home_team,
            "away_team": r.away_team,
            "prediction": r.prediction,
            "win_probability": r.win_probability,
            "odds": json.loads(r.odds) if r.odds else None
        } for r in rows]
        return JSONResponse({"date": today.isoformat(), "matches": out})
    finally:
        db.close()


# Manual trigger endpoint (protected? For now open; you can add auth later)
@app.post("/retrain")
def trigger_retrain():
    res = retrain.fetch_today_and_run(date.today())
    # send quick email
    subject = f"[Poisson Predictor] Manual retrain {datetime.utcnow().isoformat()}"
    body = json.dumps(res, indent=2)
    send_email(subject, body)
    return res


# Scheduled retrain job
def scheduled_job_run():
    try:
        print("[Scheduler] Starting scheduled retrain:", datetime.utcnow().isoformat())
        res = retrain.fetch_today_and_run(date.today())
        subject = f"[Poisson Predictor] Daily retrain success {datetime.utcnow().date()}"
        body = json.dumps(res, indent=2)
        send_email(subject, body)
        print("[Scheduler] Retrain finished:", res)
    except Exception as e:
        print("[Scheduler] Retrain failed:", e)
        send_email(f"[Poisson Predictor] Daily retrain FAILED {datetime.utcnow().date()}", str(e))


# Start scheduler
scheduler = BackgroundScheduler()
# run daily at 04:00 UTC
scheduler.add_job(scheduled_job_run, "cron", hour=4, minute=0)
scheduler.start()

# When running under dev (uvicorn --reload) you can still call scheduled_job_run manually
@app.on_event("startup")
def on_startup():
    # Optionally run a retrain at startup if you want the DB filled immediately
    # WARNING: this will run on every container restart, which may be frequent on free tiers.
    print("[Startup] Scheduler started. Scheduled retrain is active.")
