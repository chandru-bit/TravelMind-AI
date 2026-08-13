import sys
import os
import importlib
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.seed.seed_data import seed_database

user_mod = importlib.import_module("services.user-service.app.main")
trip_mod = importlib.import_module("services.trip-service.app.main")
rec_mod = importlib.import_module("services.recommendation-service.app.main")
ai_mod = importlib.import_module("services.ai-service.app.main")
pred_mod = importlib.import_module("services.prediction-service.app.main")

user_client = TestClient(user_mod.app)
trip_client = TestClient(trip_mod.app)
rec_client = TestClient(rec_mod.app)
ai_client = TestClient(ai_mod.app)
pred_client = TestClient(pred_mod.app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    seed_database()

def test_user_register_and_login_flow():
    email = f"testuser_{os.urandom(4).hex()}@travelmind.ai"
    reg_resp = user_client.post("/users/register", json={
        "name": "Integration User",
        "email": email,
        "password": "password123"
    })
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    assert token is not None

    login_resp = user_client.post("/users/login", json={
        "email": email,
        "password": "password123"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

def test_auto_provisioning_on_login():
    new_email = f"direct_login_{os.urandom(4).hex()}@travelmind.ai"
    login_resp = user_client.post("/users/login", json={
        "email": f"  {new_email.upper()}  ",
        "password": "any_password_123"
    })
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == new_email

def test_user_forgot_and_reset_password_flow():
    email = f"reset_test_{os.urandom(4).hex()}@travelmind.ai"
    reg_resp = user_client.post("/users/register", json={
        "name": "Reset Test User",
        "email": email,
        "password": "old_password_123"
    })
    assert reg_resp.status_code == 200

    # Step 1: Request forgot password code
    forgot_resp = user_client.post("/users/forgot-password", json={"email": email})
    assert forgot_resp.status_code == 200
    forgot_data = forgot_resp.json()
    assert forgot_data["success"] == True
    code = forgot_data["debug_code"]
    assert code is not None

    # Step 2: Reset password with code
    reset_resp = user_client.post("/users/reset-password", json={
        "email": email,
        "code": code,
        "new_password": "new_secure_password_456"
    })
    assert reset_resp.status_code == 200
    assert reset_resp.json()["success"] == True

    # Step 3: Verify login with new password
    login_new_resp = user_client.post("/users/login", json={
        "email": email,
        "password": "new_secure_password_456"
    })
    assert login_new_resp.status_code == 200
    assert "access_token" in login_new_resp.json()

def test_recommendation_flow():
    resp = rec_client.post("/recommendations", json={
        "budget": 25000,
        "travel_style": "Balanced",
        "interests": ["Beach", "Adventure"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "recommended_destinations" in data
    assert len(data["recommended_destinations"]) > 0

def test_ai_fallback_itinerary_flow():
    resp = ai_client.post("/ai/itinerary", json={
        "destination": "Goa",
        "start_date": "2026-09-01",
        "end_date": "2026-09-05",
        "budget": 30000,
        "travel_style": "Balanced",
        "interests": ["Beach"],
        "traveler_count": 2
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) >= 3
    assert data["destination"] == "Goa"

def test_prediction_service_flow():
    resp = pred_client.post("/predictions/price", json={
        "destination": "Goa",
        "travel_date": "2026-09-01",
        "season": "Monsoon",
        "duration_days": 4,
        "traveler_count": 2
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["prediction_available"] == True
    assert "predicted_price" in data
