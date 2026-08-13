import sys
import os
import json
import httpx
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.schemas.models import (
    AIItineraryRequest, AIExplanationRequest, ItineraryResponse, ItineraryItemSchema
)
from shared.errors.handlers import (
    api_exception_handler, http_exception_handler, validation_exception_handler,
    generic_exception_handler, APIException
)
from shared.logging.structured import get_logger
from fastapi.exceptions import RequestValidationError

logger = get_logger("ai-service")

app = FastAPI(title="TravelMind AI - AI Service", version="1.0.0")

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

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# ==================== FALLBACK GENERATOR ====================
def generate_fallback_itinerary(req: AIItineraryRequest) -> ItineraryResponse:
    """FR-10 Deterministic fallback itinerary generator when LLM is unconfigured/unavailable."""
    items = []
    dest = req.destination
    interests_str = ", ".join(req.interests) if req.interests else "local highlights"

    # Day 1
    items.append(ItineraryItemSchema(
        day_number=1,
        time="09:00 AM",
        activity=f"Arrival & Morning Refresh in {dest}",
        location=f"{dest} Central Station / Airport",
        duration="2 hours",
        estimated_cost=round(req.budget * 0.05, 2),
        travel_time="30 mins",
        description=f"Check into your accommodation and get settled."
    ))
    items.append(ItineraryItemSchema(
        day_number=1,
        time="02:00 PM",
        activity=f"Explore Heritage & City Landmark",
        location=f"{dest} Main Square",
        duration="3.5 hours",
        estimated_cost=round(req.budget * 0.08, 2),
        travel_time="20 mins",
        description=f"Guided tour around famous spots in {dest} tailored for {req.travel_style} travel."
    ))

    # Day 2
    items.append(ItineraryItemSchema(
        day_number=2,
        time="09:30 AM",
        activity=f"Primary Interest Activity: {interests_str}",
        location=f"{dest} Attraction Zone",
        duration="4 hours",
        estimated_cost=round(req.budget * 0.15, 2),
        travel_time="35 mins",
        description=f"Dedicated time for {interests_str} based on your onboard preferences."
    ))
    items.append(ItineraryItemSchema(
        day_number=2,
        time="06:00 PM",
        activity="Sunset View & Local Cuisine Tasting",
        location=f"{dest} Popular Viewpoint",
        duration="3 hours",
        estimated_cost=round(req.budget * 0.10, 2),
        travel_time="15 mins",
        description="Enjoy evening dining featuring authentic regional culinary specialties."
    ))

    # Day 3
    items.append(ItineraryItemSchema(
        day_number=3,
        time="10:00 AM",
        activity="Souvenir Shopping & Relaxation",
        location=f"{dest} Artisan Market",
        duration="3 hours",
        estimated_cost=round(req.budget * 0.07, 2),
        travel_time="15 mins",
        description="Leisure stroll through markets before departure preparations."
    ))

    return ItineraryResponse(
        trip_id="ai-generated",
        destination=req.destination,
        total_days=3,
        items=items,
        is_ai_generated=False,
        ai_status_message="AI personalization unavailable — showing standard itinerary."
    )

# ==================== ROUTES ====================
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-service",
        "llm_configured": bool(LLM_API_KEY)
    }

@app.post("/ai/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(req: AIItineraryRequest):
    if not LLM_API_KEY or DEMO_MODE:
        logger.info("Using deterministic fallback itinerary generator (DEMO_MODE=true or missing LLM_API_KEY).")
        return generate_fallback_itinerary(req)

    # Live LLM Integration
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            prompt = (
                f"Generate a 3-day travel itinerary for {req.destination}. "
                f"Budget: {req.budget}, Travel Style: {req.travel_style}, Interests: {', '.join(req.interests)}. "
                f"Return JSON array of items with fields: day_number, time, activity, location, duration, estimated_cost, travel_time, description."
            )
            response = await client.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                items_data = json.loads(content)
                items = [ItineraryItemSchema(**item) for item in items_data]
                return ItineraryResponse(
                    trip_id="ai-live",
                    destination=req.destination,
                    total_days=3,
                    items=items,
                    is_ai_generated=True,
                    ai_status_message="Personalized itinerary generated by AI."
                )
    except Exception as e:
        logger.warning("LLM API call failed (%s). Falling back to deterministic itinerary generator.", str(e))

    return generate_fallback_itinerary(req)

@app.post("/ai/explain")
def explain_recommendation(req: AIExplanationRequest):
    dest = req.destination
    prefs = req.user_preferences or {}
    b = prefs.get("budget", 25000)
    style = prefs.get("travel_style", "Balanced")
    
    explanation = (
        f"We recommended {dest} because it perfectly aligns with your {style} travel style "
        f"and estimated budget of ₹{b:,.0f}. The climate, popular attractions, and local cost structures "
        f"maximize value and experience satisfaction."
    )
    
    return {
        "destination": dest,
        "explanation": explanation,
        "is_ai_generated": bool(LLM_API_KEY and not DEMO_MODE)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
