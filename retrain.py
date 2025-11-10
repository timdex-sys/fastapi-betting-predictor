import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from db import SessionLocal
from models_db import Base, GamePrediction

# --------------------------
# Helper function: Fetch and parse data
# --------------------------
def fetch_latest_matches_from_goal():
    """
    Fetch latest matches from Goal.com (example scraper).
    """
    url = "https://www.goal.com/en/fixtures"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    matches = []
    for match in soup.select(".match-row"):  # Example CSS selector
        try:
            home_team = match.select_one(".team-home .name").text.strip()
            away_team = match.select_one(".team-away .name").text.strip()
            match_time = match.select_one(".match-time").text.strip()
            matches.append({
                "home_team": home_team,
                "away_team": away_team,
                "match_time": match_time
            })
        except Exception:
            continue
    return matches


def fetch_predictions_from_forebet():
    """
    Fetch prediction data from Forebet.com.
    """
    url = "https://www.forebet.com/en/football-predictions"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    predictions = []
    for row in soup.select("table.forebet tr"):
        try:
            home_team = row.select_one(".homeTeam").text.strip()
            away_team = row.select_one(".awayTeam").text.strip()
            prediction = row.select_one(".predictedResult").text.strip()
            probability = row.select_one(".prob").text.strip()
            predictions.append({
                "home_team": home_team,
                "away_team": away_team,
                "prediction": prediction,
                "probability": probability
            })
        except Exception:
            continue
    return predictions


def fetch_injury_updates():
    """
    Example placeholder for fetching injury updates.
    Could be replaced with real API or data source.
    """
    return [
        {"team": "Arsenal", "player": "Saka", "status": "Doubtful"},
        {"team": "Man City", "player": "De Bruyne", "status": "Injured"}
    ]


# --------------------------
# Main retraining/update function
# --------------------------
def fetch_latest_matches_and_update_db():
    """
    Fetch data from Goal.com and Forebet, combine, and update the local database.
    """
    db: Session = SessionLocal()

    print("[INFO] Fetching latest matches and predictions...")
    matches = fetch_latest_matches_from_goal()
    predictions = fetch_predictions_from_forebet()
    injuries = fetch_injury_updates()

    print(f"[INFO] Retrieved {len(matches)} matches and {len(predictions)} predictions")

    # Clear old data
    db.query(GamePrediction).delete()
    db.commit()

    for match in matches:
        # Match teams
        for pred in predictions:
            if (
                pred["home_team"].lower() == match["home_team"].lower()
                and pred["away_team"].lower() == match["away_team"].lower()
            ):
                game = GamePrediction(
                    home_team=match["home_team"],
                    away_team=match["away_team"],
                    match_time=match["match_time"],
                    prediction=pred["prediction"],
                    probability=pred["probability"],
                    last_updated=datetime.utcnow()
                )
                db.add(game)
                break

    db.commit()
    db.close()
    print("[SUCCESS] Database updated with latest match predictions.")


if __name__ == "__main__":
    fetch_latest_matches_and_update_db()
