import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from shared.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    preference = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    home_location = Column(String(100), default="Mumbai")
    budget = Column(Float, default=25000.0)
    travel_style = Column(String(50), default="Balanced")
    interests_json = Column(Text, default="[]")  # JSON list
    activities_json = Column(Text, default="[]")  # JSON list
    food_preference = Column(String(50), default="No Restrictions")
    traveler_count = Column(Integer, default=2)
    preferred_destinations_json = Column(Text, default="[]")  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preference")

    @property
    def interests(self):
        return json.loads(self.interests_json or "[]")

    @interests.setter
    def interests(self, val):
        self.interests_json = json.dumps(val or [])

    @property
    def activities(self):
        return json.loads(self.activities_json or "[]")

    @activities.setter
    def activities(self, val):
        self.activities_json = json.dumps(val or [])

    @property
    def preferred_destinations(self):
        return json.loads(self.preferred_destinations_json or "[]")

    @preferred_destinations.setter
    def preferred_destinations(self, val):
        self.preferred_destinations_json = json.dumps(val or [])


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    state_country = Column(String(100), nullable=False)
    avg_cost = Column(Float, nullable=False)
    best_season = Column(String(50), nullable=False)
    weather_summary = Column(String(100), default="Pleasant & Sunny")
    activities_json = Column(Text, default="[]")
    travel_type = Column(String(50), default="Balanced")
    popularity = Column(Float, default=85.0)  # Out of 100
    distance_km = Column(Float, default=500.0)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def activities(self):
        return json.loads(self.activities_json or "[]")

    @activities.setter
    def activities(self, val):
        self.activities_json = json.dumps(val or [])


class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=False)
    budget = Column(Float, nullable=False)
    traveler_count = Column(Integer, default=2)
    interests_json = Column(Text, default="[]")
    travel_style = Column(String(50), default="Balanced")
    status = Column(String(50), default="planned")  # planned, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="trips")
    itinerary = relationship("Itinerary", back_populates="trip", uselist=False, cascade="all, delete-orphan")

    @property
    def interests(self):
        return json.loads(self.interests_json or "[]")

    @interests.setter
    def interests(self, val):
        self.interests_json = json.dumps(val or [])


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.id"), unique=True, nullable=False)
    destination = Column(String(100), nullable=False)
    total_days = Column(Integer, default=3)
    is_ai_generated = Column(Boolean, default=True)
    ai_status_message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="itinerary")
    items = relationship("ItineraryItem", back_populates="itinerary", cascade="all, delete-orphan")


class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    itinerary_id = Column(String(36), ForeignKey("itineraries.id"), nullable=False)
    day_number = Column(Integer, default=1)
    time = Column(String(20), default="09:00 AM")
    activity = Column(String(150), nullable=False)
    location = Column(String(150), nullable=False)
    duration = Column(String(50), default="2 hours")
    estimated_cost = Column(Float, default=0.0)
    travel_time = Column(String(50), default="15 mins")
    description = Column(Text, default="")

    itinerary = relationship("Itinerary", back_populates="items")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    destination = Column(String(100), nullable=False, index=True)
    travel_date = Column(String(20), nullable=False)
    hotel_price = Column(Float, nullable=False)
    transport_price = Column(Float, nullable=False)
    demand_score = Column(Float, default=0.5)  # 0.0 to 1.0
    season = Column(String(50), default="Regular")
    created_at = Column(DateTime, default=datetime.utcnow)


class PricePrediction(Base):
    __tablename__ = "price_predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    destination = Column(String(100), nullable=False)
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    trend = Column(String(50), nullable=False)
    booking_recommendation = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    destination = Column(String(100), unique=True, nullable=False, index=True)
    temperature_celsius = Column(Float, nullable=False)
    condition = Column(String(100), nullable=False)
    humidity_percent = Column(Integer, default=65)
    wind_speed_kmh = Column(Float, default=12.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=True)
    booking_type = Column(String(50), nullable=False)  # Flight, Hotel, Activity, Transport
    provider = Column(String(100), nullable=False)
    title = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    booking_url = Column(String(255), default="#")
    status = Column(String(50), default="Recommended")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    destination = Column(String(100), nullable=True)
    trip_id = Column(String(36), nullable=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    is_helpful = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedback")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="system")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
