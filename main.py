from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Initialize app
app = FastAPI(title="Betting Predictor Dashboard")

# Tell FastAPI where the templates are
templates = Jinja2Templates(directory="templates")

# Example: mock data (later this will come from your predictor)
today_matches = [
    {"home": "Aston Villa", "away": "Maccabi Tel Aviv", "prediction": "Aston Villa Win"},
    {"home": "Bologna", "away": "Brann", "prediction": "Bologna Win"},
    {"home": "Sturm Graz", "away": "Nottingham", "prediction": "Nottingham Win"},
]

# Route for the dashboard page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "matches": today_matches}
    )

# Optional API endpoint if you need JSON data
@app.get("/api/matches")
def get_matches():
    return {"matches": today_matches}

