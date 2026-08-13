import sys
import os
import importlib
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared.database.connection import SessionLocal, Base, engine
from database.seed.seed_data import seed_database
from shared.schemas.models import PricePredictionRequest

pred_module = importlib.import_module("services.prediction-service.app.main")
ml_pipeline = pred_module.ml_pipeline
predict_price = pred_module.predict_price

def test_ml_model_training_and_prediction():
    seed_database()
    
    db = SessionLocal()
    try:
        ml_pipeline.train_from_db(db)
        assert ml_pipeline.is_trained == True
        assert "r2_score" in ml_pipeline.metrics

        req = PricePredictionRequest(
            destination="Goa",
            travel_date="2026-09-01",
            season="Monsoon",
            duration_days=4,
            traveler_count=2
        )
        res = predict_price(req, db)
        assert res.prediction_available == True
        assert res.current_price > 0
        assert res.predicted_price > 0
        assert res.trend in ["rising", "falling", "stable"]
    finally:
        db.close()
