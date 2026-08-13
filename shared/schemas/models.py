from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==================== USER SCHEMAS ====================
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, example="Alex Morgan")
    email: str = Field(..., example="alex@example.com")
    password: str = Field(..., min_length=6, example="password123")

class UserLoginRequest(BaseModel):
    email: str = Field(..., example="alex@example.com")
    password: str = Field(..., example="password123")

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserPreferencesSchema(BaseModel):
    home_location: Optional[str] = "Mumbai"
    budget: Optional[float] = 25000.0
    travel_style: Optional[str] = "Balanced"  # Budget, Balanced, Premium, Luxury
    interests: Optional[List[str]] = ["Beach", "Adventure", "Food"]
    activities: Optional[List[str]] = ["Sightseeing", "Trekking", "Water Sports"]
    food_preference: Optional[str] = "No Restrictions"
    traveler_count: Optional[int] = 2
    preferred_destinations: Optional[List[str]] = ["Goa", "Kodaikanal"]

class UserProfileResponse(UserResponse):
    preferences: Optional[UserPreferencesSchema] = None

# ==================== TRIP & ITINERARY SCHEMAS ====================
class TripCreateRequest(BaseModel):
    source: str = Field(..., example="Mumbai")
    destination: str = Field(..., example="Goa")
    start_date: str = Field(..., example="2026-09-01")
    end_date: str = Field(..., example="2026-09-05")
    budget: float = Field(..., gt=0, example=30000.0)
    traveler_count: int = Field(..., gt=0, example=2)
    interests: List[str] = Field(default_factory=lambda: ["Beach", "Adventure"])
    travel_style: str = Field(default="Balanced", example="Balanced")

class ItineraryItemSchema(BaseModel):
    id: Optional[str] = None
    day_number: int = 1
    time: str = "09:00 AM"
    activity: str = "Beach Walk & Breakfast"
    location: str = "Calangute Beach"
    duration: str = "2 hours"
    estimated_cost: float = 500.0
    travel_time: str = "15 mins"
    description: str = "Enjoy morning sea breeze and fresh breakfast."

class TripResponse(BaseModel):
    id: str
    user_id: str
    source: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    traveler_count: int
    interests: List[str]
    travel_style: str
    status: str = "planned"
    created_at: Optional[datetime] = None

class ItineraryResponse(BaseModel):
    trip_id: str
    destination: str
    total_days: int
    items: List[ItineraryItemSchema]
    is_ai_generated: bool = True
    ai_status_message: Optional[str] = None

# ==================== RECOMMENDATION SCHEMAS ====================
class RecommendationRequest(BaseModel):
    source: Optional[str] = "Mumbai"
    budget: float = 25000.0
    travel_style: str = "Balanced"
    interests: List[str] = ["Beach", "Culture"]
    traveler_count: int = 2

class DestinationRecommendation(BaseModel):
    destination: str
    state_country: str
    match_score: float
    match_percentage: int
    estimated_cost: float
    best_season: str
    weather_summary: str
    activities: List[str]
    recommendation_reasons: List[str]
    breakdown_scores: Dict[str, float]

class RecommendationResponse(BaseModel):
    user_id: Optional[str] = None
    recommended_destinations: List[DestinationRecommendation]
    total_found: int

# ==================== ML PREDICTION SCHEMAS ====================
class PricePredictionRequest(BaseModel):
    destination: str = "Goa"
    travel_date: str = "2026-09-01"
    season: str = "Monsoon"
    duration_days: int = 4
    traveler_count: int = 2

class PricePredictionResponse(BaseModel):
    destination: str
    current_price: float
    predicted_price: float
    price_change_percent: float
    trend: str  # "rising", "falling", "stable"
    booking_recommendation: str  # "Book Now", "Wait for Drop", "Moderate Priority"
    prediction_available: bool = True
    message: Optional[str] = None
    model_metrics: Optional[Dict[str, float]] = None

# ==================== AI SCHEMAS ====================
class AIItineraryRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
    travel_style: str
    interests: List[str]
    traveler_count: int

class AIExplanationRequest(BaseModel):
    destination: str
    user_preferences: Dict[str, Any]

# ==================== BUDGET OPTIMIZER SCHEMAS ====================
class BudgetBreakdown(BaseModel):
    total_budget: float
    transportation: float
    accommodation: float
    food: float
    activities: float
    shopping: float
    emergency: float
    estimated_total: float
    remaining_budget: float
    is_over_budget: bool
    warning: Optional[str] = None
    optimization_suggestions: List[str]

# ==================== WEATHER SCHEMAS ====================
class WeatherResponse(BaseModel):
    destination: str
    temperature_celsius: float
    condition: str
    humidity_percent: int
    wind_speed_kmh: float
    is_demo_data: bool = False

# ==================== FEEDBACK & NOTIFICATION SCHEMAS ====================
class FeedbackCreateRequest(BaseModel):
    destination: Optional[str] = None
    trip_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: str
    is_helpful: bool = True

class FeedbackResponse(BaseModel):
    id: str
    user_id: str
    rating: int
    comment: str
    created_at: Optional[datetime] = None

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str  # "price_alert", "trip_reminder", "recommendation"
    is_read: bool = False
    created_at: Optional[datetime] = None
