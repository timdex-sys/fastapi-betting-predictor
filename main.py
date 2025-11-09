from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import date

app = FastAPI()

# Setup templates folder
templates = Jinja2Templates(directory="dashboard/templates")

# Optional: if you have static files (CSS, JS)
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# Example mock predictions (replace later with real database data)
def get_today_predictions():
    return [
        {"home": "Arsenal", "away": "Chelsea", "prediction": "Arsenal Win"},
        {"home": "Real Madrid", "away": "Barcelona", "prediction": "Draw"},
        {"home": "Man City", "away": "Liverpool", "prediction": "Man City Win"},
        {"home": "PSG", "away": "Monaco", "prediction": "PSG Win"},
    ]

@app.get("/")
def home(request: Request):
    today = date.today().strftime("%Y-%m-%d")
    games = get_today_predictions()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "today": today, "matches": games}
    )
