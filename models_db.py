from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

# Base class for SQLAlchemy models
Base = declarative_base()

class GamePrediction(Base):
    """
    Stores predicted matches and probabilities.
    Each record represents one football match prediction.
    """
    __tablename__ = "game_predictions"

    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    match_date = Column(Date, nullable=False)

    home_win_prob = Column(Float, nullable=True)
    draw_prob = Column(Float, nullable=True)
    away_win_prob = Column(Float, nullable=True)

    predicted_winner = Column(String, nullable=True)
    league = Column(String, nullable=True)
    source = Column(String, default="Forebet")

    def __repr__(self):
        return (
            f"<GamePrediction(home='{self.home_team}', "
            f"away='{self.away_team}', winner='{self.predicted_winner}', "
            f"date='{self.match_date}')>"
        )
