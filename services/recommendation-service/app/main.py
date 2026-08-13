import sys
import os
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.database.connection import get_db, Base, engine
from database.models import Destination, WeatherData, Feedback, generate_uuid
from shared.schemas.models import (
    RecommendationRequest, DestinationRecommendation, RecommendationResponse,
    FeedbackCreateRequest, FeedbackResponse
)
from shared.auth.jwt import decode_access_token
from shared.cache.redis_client import cache
from shared.errors.handlers import (
    api_exception_handler, http_exception_handler, validation_exception_handler,
    generic_exception_handler, APIException
)
from shared.logging.structured import get_logger
from fastapi.exceptions import RequestValidationError

logger = get_logger("recommendation-service")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelMind AI - Recommendation Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

def get_optional_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization:
        return None
    try:
        scheme, token = authorization.split()
        if scheme.lower() == "bearer":
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                return payload["sub"]
    except Exception:
        pass
    return None

# ==================== SCORING ENGINE ====================
def calculate_budget_score(user_budget: float, dest_cost: float) -> float:
    """Calculates budget score (0.0 to 1.0). Perfect score if cost <= budget."""
    if dest_cost <= user_budget:
        ratio = dest_cost / user_budget
        # Prefer destinations that utilize 50-90% of user budget
        return round(0.8 + 0.2 * ratio, 2)
    else:
        over = dest_cost - user_budget
        penalty = over / user_budget
        return max(0.1, round(1.0 - penalty, 2))

def calculate_interest_score(user_interests: List[str], dest_activities: List[str], dest_type: str) -> float:
    """Calculates interest overlap score (0.0 to 1.0)."""
    if not user_interests:
        return 0.70
    
    matches = 0
    u_interests_lower = [i.lower() for i in user_interests]
    d_activities_lower = [a.lower() for a in dest_activities]

    for ui in u_interests_lower:
        if any(ui in da or da in ui for da in d_activities_lower) or ui in dest_type.lower():
            matches += 1
            
    score = min(1.0, (matches / len(user_interests)) + 0.3)
    return round(score, 2)

def calculate_weather_score(weather: Optional[WeatherData]) -> float:
    """Calculates weather condition score (0.0 to 1.0)."""
    if not weather:
        return 0.80
    cond = weather.condition.lower()
    if "sunny" in cond or "clear" in cond or "pleasant" in cond:
        return 0.95
    elif "cloudy" in cond or "misty" in cond:
        return 0.85
    elif "rain" in cond or "storm" in cond:
        return 0.50
    return 0.75

def calculate_activity_score(dest_activities: List[str]) -> float:
    """Calculates activity richness score (0.0 to 1.0)."""
    count = len(dest_activities)
    if count >= 4:
        return 0.95
    elif count == 3:
        return 0.85
    elif count == 2:
        return 0.70
    return 0.50

def calculate_distance_score(dest_distance: float) -> float:
    """Calculates distance match score (0.0 to 1.0)."""
    if dest_distance <= 500:
        return 0.95
    elif dest_distance <= 1000:
        return 0.85
    elif dest_distance <= 1500:
        return 0.75
    return 0.65

def score_destination(dest: Destination, req: RecommendationRequest, weather: Optional[WeatherData]) -> DestinationRecommendation:
    b_score = calculate_budget_score(req.budget, dest.avg_cost)
    i_score = calculate_interest_score(req.interests, dest.activities, dest.travel_type)
    w_score = calculate_weather_score(weather)
    a_score = calculate_activity_score(dest.activities)
    d_score = calculate_distance_score(dest.distance_km)

    # FR-06 Weighted Formula:
    # Final Score = (Budget * 0.25) + (Interest * 0.30) + (Weather * 0.15) + (Activity * 0.15) + (Distance * 0.15)
    final_score = (b_score * 0.25) + (i_score * 0.30) + (w_score * 0.15) + (a_score * 0.15) + (d_score * 0.15)
    match_percentage = int(min(99, max(50, final_score * 100)))

    reasons = []
    if b_score >= 0.8:
        reasons.append(f"Fits within your selected budget of ₹{req.budget:,.0f}")
    if i_score >= 0.7 and req.interests:
        reasons.append(f"Matches your interests in {', '.join(req.interests[:2])}")
    if w_score >= 0.8 and weather:
        reasons.append(f"Great weather ({weather.condition}, {weather.temperature_celsius:.1f}°C)")
    if not reasons:
        reasons.append("Popular travel destination with excellent overall rating")

    weather_desc = f"{weather.condition}, {weather.temperature_celsius:.1f}°C" if weather else dest.weather_summary

    return DestinationRecommendation(
        destination=dest.name,
        state_country=dest.state_country,
        match_score=round(final_score, 3),
        match_percentage=match_percentage,
        estimated_cost=dest.avg_cost,
        best_season=dest.best_season,
        weather_summary=weather_desc,
        activities=dest.activities,
        recommendation_reasons=reasons,
        breakdown_scores={
            "budget": b_score,
            "interest": i_score,
            "weather": w_score,
            "activity": a_score,
            "distance": d_score
        }
    )

# ==================== ROUTES ====================
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "recommendation-service"}

@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    req: RecommendationRequest,
    user_id: Optional[str] = Depends(get_optional_user_id),
    db: Session = Depends(get_db)
):
    cache_key = f"rec:{req.budget}:{req.travel_style}:{','.join(req.interests or [])}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info("Serving recommendation result from Redis cache")
        return RecommendationResponse(**cached_result)

    destinations = db.query(Destination).all()
    weather_map = {w.destination: w for w in db.query(WeatherData).all()}

    scored_list = []
    for dest in destinations:
        w_data = weather_map.get(dest.name)
        scored_rec = score_destination(dest, req, w_data)
        scored_list.append(scored_rec)

    # Sort descending by match score
    scored_list.sort(key=lambda x: x.match_score, reverse=True)

    response = RecommendationResponse(
        user_id=user_id,
        recommended_destinations=scored_list[:10],
        total_found=len(scored_list)
    )

    cache.set(cache_key, response.model_dump(), ttl_seconds=300)
    return response

@app.get("/recommendations/destinations")
def list_destinations(db: Session = Depends(get_db)):
    dests = db.query(Destination).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "state_country": d.state_country,
            "avg_cost": d.avg_cost,
            "best_season": d.best_season,
            "weather_summary": d.weather_summary,
            "activities": d.activities,
            "travel_type": d.travel_type,
            "popularity": d.popularity
        }
        for d in dests
    ]

@app.post("/recommendations/feedback", response_model=FeedbackResponse)
def submit_feedback(
    req: FeedbackCreateRequest,
    user_id: Optional[str] = Depends(get_optional_user_id),
    db: Session = Depends(get_db)
):
    actual_user_id = user_id or "anonymous-user"
    fb = Feedback(
        user_id=actual_user_id,
        destination=req.destination,
        trip_id=req.trip_id,
        rating=req.rating,
        comment=req.comment,
        is_helpful=req.is_helpful
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return FeedbackResponse(
        id=fb.id,
        user_id=fb.user_id,
        rating=fb.rating,
        comment=fb.comment,
        created_at=fb.created_at
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
