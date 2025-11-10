# model.py
"""
Machine learning & statistical model for football match outcome predictions.
Integrates Poisson goals, recent form, and odds-based calibration.
"""

import numpy as np
import pandas as pd
from scipy.stats import poisson
import json
import datetime as dt


# -----------------------------------------------------
# Core Poisson model
# -----------------------------------------------------
def poisson_match_prob(lambda_home: float, lambda_away: float, max_goals: int = 6):
    """
    Compute all possible scoreline probabilities up to max_goals for both teams.
    """
    probs = np.zeros((max_goals + 1, max_goals + 1))
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            probs[i][j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
    return probs


def match_outcome_probs(lambda_home: float, lambda_away: float):
    """
    Calculate probabilities of Home Win, Draw, Away Win using Poisson.
    """
    max_goals = 6
    matrix = poisson_match_prob(lambda_home, lambda_away, max_goals)
    home_win = np.sum(np.tril(matrix, -1))
    draw = np.sum(np.diag(matrix))
    away_win = np.sum(np.triu(matrix, 1))
    return {"home": home_win, "draw": draw, "away": away_win}


# -----------------------------------------------------
# Elo-style lambda estimation
# -----------------------------------------------------
def expected_goals_from_elo(home_elo, away_elo):
    """
    Approximate lambda_home, lambda_away from Elo ratings.
    """
    diff = home_elo - away_elo
    avg_goals = 2.7  # average total goals in Europe
    home_attack = 1.4 / (1 + np.exp(-diff / 400))
    away_attack = 1.3 / (1 + np.exp(diff / 400))
    lambda_home = avg_goals * home_attack / (home_attack + away_attack)
    lambda_away = avg_goals * away_attack / (home_attack + away_attack)
    return lambda_home, lambda_away


# -----------------------------------------------------
# Prediction interface
# -----------------------------------------------------
def predict_match(home_team, away_team, odds_home, odds_draw, odds_away, form_data=None):
    """
    Predict outcome using Poisson + odds calibration + optional form data.
    """

    # Convert bookmaker odds to implied probabilities
    implied_home = 1 / odds_home
    implied_draw = 1 / odds_draw
    implied_away = 1 / odds_away
    total = implied_home + implied_draw + implied_away
    implied_home /= total
    implied_draw /= total
    implied_away /= total

    # Default lambda based on odds ratio
    lambda_home = 1.5 * (implied_home / implied_away)
    lambda_away = 1.0 * (implied_away / implied_home)

    # Adjust based on recent form
    if form_data:
        home_form = np.mean(form_data.get(home_team, [1.0]))
        away_form = np.mean(form_data.get(away_team, [1.0]))
        lambda_home *= (1 + (home_form - 1) * 0.3)
        lambda_away *= (1 + (away_form - 1) * 0.3)

    probs = match_outcome_probs(lambda_home, lambda_away)

    # Calibration blending (combine Poisson + market)
    calibrated_home = (probs["home"] * 0.6) + (implied_home * 0.4)
    calibrated_draw = (probs["draw"] * 0.6) + (implied_draw * 0.4)
    calibrated_away = (probs["away"] * 0.6) + (implied_away * 0.4)

    normalized = np.array([calibrated_home, calibrated_draw, calibrated_away])
    normalized /= normalized.sum()

    outcome = ["Home", "Draw", "Away"][np.argmax(normalized)]
    prob = round(normalized.max() * 100, 2)

    return {
        "home_team": home_team,
        "away_team": away_team,
        "prediction": outcome,
        "probabilities": {
            "home": round(normalized[0] * 100, 2),
            "draw": round(normalized[1] * 100, 2),
            "away": round(normalized[2] * 100, 2),
        },
        "expected_goals": {"home": round(lambda_home, 2), "away": round(lambda_away, 2)},
        "implied_odds": {"home": odds_home, "draw": odds_draw, "away": odds_away},
        "timestamp": str(dt.datetime.utcnow())
    }


# -----------------------------------------------------
# Example usage
# -----------------------------------------------------
if __name__ == "__main__":
    test = predict_match(
        "Barcelona",
        "Club Brugge",
        odds_home=1.57,
        odds_draw=3.90,
        odds_away=5.19,
        form_data={"Barcelona": [1.2, 1.1, 1.3], "Club Brugge": [0.9, 1.0, 0.8]}
    )
    print(json.dumps(test, indent=2))
