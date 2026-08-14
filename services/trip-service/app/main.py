import sys
import os
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.database.connection import get_db, Base, engine
from database.models import Trip, Itinerary, ItineraryItem, generate_uuid
from shared.schemas.models import (
    TripCreateRequest, TripResponse, ItineraryResponse, ItineraryItemSchema
)
from shared.auth.jwt import decode_access_token
from shared.errors.handlers import (
    api_exception_handler, http_exception_handler, validation_exception_handler,
    generic_exception_handler, APIException
)
import uuid
from fastapi import Request
from shared.logging.structured import get_logger, request_id_ctx
from fastapi.exceptions import RequestValidationError

logger = get_logger("trip-service")

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    logger.warning(f"Could not initialize DB tables at startup: {exc}")

app = FastAPI(title="TravelMind AI - Trip Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_ctx.set(req_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise APIException("UNAUTHORIZED", "Missing authorization header", 401)
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise APIException("UNAUTHORIZED", "Invalid token scheme", 401)
    except ValueError:
        raise APIException("UNAUTHORIZED", "Malformed authorization header", 401)
    
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise APIException("UNAUTHORIZED", "Invalid or expired token", 401)
    return payload["sub"]

# ==================== REPOSITORY LAYER ====================
class TripRepository:
    @staticmethod
    def create_trip(db: Session, user_id: str, req: TripCreateRequest) -> Trip:
        trip = Trip(
            user_id=user_id,
            source=req.source,
            destination=req.destination,
            start_date=req.start_date,
            end_date=req.end_date,
            budget=req.budget,
            traveler_count=req.traveler_count,
            travel_style=req.travel_style,
            status="planned"
        )
        trip.interests = req.interests
        db.add(trip)
        db.flush()

        # Create default 3-day itinerary timeline
        itinerary = Itinerary(
            trip_id=trip.id,
            destination=req.destination,
            total_days=3,
            is_ai_generated=True,
            ai_status_message="Personalized itinerary generated based on your budget and preferences."
        )
        db.add(itinerary)
        db.flush()

        default_items = [
            ItineraryItem(
                itinerary_id=itinerary.id,
                day_number=1,
                time="09:00 AM",
                activity=f"Arrival & Hotel Check-in at {req.destination}",
                location=req.destination,
                duration="2 hours",
                estimated_cost=req.budget * 0.05,
                travel_time="30 mins",
                description="Settle into accommodation and refresh."
            ),
            ItineraryItem(
                itinerary_id=itinerary.id,
                day_number=1,
                time="02:00 PM",
                activity=f"Sightseeing & Local Exploration",
                location=f"{req.destination} City Center",
                duration="4 hours",
                estimated_cost=req.budget * 0.08,
                travel_time="20 mins",
                description="Explore top rated attractions and landmarks."
            ),
            ItineraryItem(
                itinerary_id=itinerary.id,
                day_number=2,
                time="10:00 AM",
                activity=f"Main Interest Activity: {req.interests[0] if req.interests else 'Adventure'}",
                location=f"{req.destination} Activity Hub",
                duration="5 hours",
                estimated_cost=req.budget * 0.15,
                travel_time="45 mins",
                description="Immerse in your preferred travel experiences."
            ),
            ItineraryItem(
                itinerary_id=itinerary.id,
                day_number=3,
                time="11:00 AM",
                activity="Souvenir Shopping & Local Cuisine",
                location="Local Market",
                duration="3 hours",
                estimated_cost=req.budget * 0.07,
                travel_time="15 mins",
                description="Enjoy famous regional delicacies and gift shopping."
            )
        ]
        db.add_all(default_items)
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def get_user_trips(db: Session, user_id: str) -> List[Trip]:
        return db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.created_at.desc()).all()

    @staticmethod
    def get_trip_by_id(db: Session, trip_id: str, user_id: str) -> Optional[Trip]:
        return db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()

    @staticmethod
    def update_trip(db: Session, trip: Trip, req: TripCreateRequest) -> Trip:
        trip.source = req.source
        trip.destination = req.destination
        trip.start_date = req.start_date
        trip.end_date = req.end_date
        trip.budget = req.budget
        trip.traveler_count = req.traveler_count
        trip.travel_style = req.travel_style
        trip.interests = req.interests
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def delete_trip(db: Session, trip: Trip):
        db.delete(trip)
        db.commit()

# ==================== ROUTES ====================
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "trip-service"}

@app.post("/trips", response_model=TripResponse)
def create_trip(req: TripCreateRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if req.budget <= 0:
        raise APIException("BAD_REQUEST", "Budget must be greater than zero.", 400)
    if req.traveler_count <= 0:
        raise APIException("BAD_REQUEST", "Traveler count must be at least 1.", 400)

    trip = TripRepository.create_trip(db, user_id, req)
    return TripResponse(
        id=trip.id,
        user_id=trip.user_id,
        source=trip.source,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget=trip.budget,
        traveler_count=trip.traveler_count,
        interests=trip.interests,
        travel_style=trip.travel_style,
        status=trip.status,
        created_at=trip.created_at
    )

@app.get("/trips", response_model=List[TripResponse])
def list_trips(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    trips = TripRepository.get_user_trips(db, user_id)
    return [
        TripResponse(
            id=t.id,
            user_id=t.user_id,
            source=t.source,
            destination=t.destination,
            start_date=t.start_date,
            end_date=t.end_date,
            budget=t.budget,
            traveler_count=t.traveler_count,
            interests=t.interests,
            travel_style=t.travel_style,
            status=t.status,
            created_at=t.created_at
        )
        for t in trips
    ]

@app.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    trip = TripRepository.get_trip_by_id(db, trip_id, user_id)
    if not trip:
        raise APIException("NOT_FOUND", f"Trip with ID '{trip_id}' not found.", 404)
    return TripResponse(
        id=trip.id,
        user_id=trip.user_id,
        source=trip.source,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget=trip.budget,
        traveler_count=trip.traveler_count,
        interests=trip.interests,
        travel_style=trip.travel_style,
        status=trip.status,
        created_at=trip.created_at
    )

@app.get("/trips/{trip_id}/itinerary", response_model=ItineraryResponse)
def get_itinerary(trip_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    trip = TripRepository.get_trip_by_id(db, trip_id, user_id)
    if not trip or not trip.itinerary:
        raise APIException("NOT_FOUND", "Itinerary not found for this trip.", 404)
    
    items_schema = [
        ItineraryItemSchema(
            id=item.id,
            day_number=item.day_number,
            time=item.time,
            activity=item.activity,
            location=item.location,
            duration=item.duration,
            estimated_cost=item.estimated_cost,
            travel_time=item.travel_time,
            description=item.description
        )
        for item in sorted(trip.itinerary.items, key=lambda x: (x.day_number, x.time))
    ]

    return ItineraryResponse(
        trip_id=trip.id,
        destination=trip.destination,
        total_days=trip.itinerary.total_days,
        items=items_schema,
        is_ai_generated=trip.itinerary.is_ai_generated,
        ai_status_message=trip.itinerary.ai_status_message
    )

@app.post("/trips/{trip_id}/itinerary/items", response_model=ItineraryItemSchema)
def add_itinerary_item(trip_id: str, item_req: ItineraryItemSchema, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    trip = TripRepository.get_trip_by_id(db, trip_id, user_id)
    if not trip or not trip.itinerary:
        raise APIException("NOT_FOUND", "Trip itinerary not found.", 404)

    new_item = ItineraryItem(
        itinerary_id=trip.itinerary.id,
        day_number=item_req.day_number,
        time=item_req.time,
        activity=item_req.activity,
        location=item_req.location,
        duration=item_req.duration,
        estimated_cost=item_req.estimated_cost,
        travel_time=item_req.travel_time,
        description=item_req.description
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return ItineraryItemSchema(
        id=new_item.id,
        day_number=new_item.day_number,
        time=new_item.time,
        activity=new_item.activity,
        location=new_item.location,
        duration=new_item.duration,
        estimated_cost=new_item.estimated_cost,
        travel_time=new_item.travel_time,
        description=new_item.description
    )

@app.put("/trips/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: str, req: TripCreateRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    trip = TripRepository.get_trip_by_id(db, trip_id, user_id)
    if not trip:
        raise APIException("NOT_FOUND", "Trip not found.", 404)
    updated = TripRepository.update_trip(db, trip, req)
    return TripResponse(
        id=updated.id,
        user_id=updated.user_id,
        source=updated.source,
        destination=updated.destination,
        start_date=updated.start_date,
        end_date=updated.end_date,
        budget=updated.budget,
        traveler_count=updated.traveler_count,
        interests=updated.interests,
        travel_style=updated.travel_style,
        status=updated.status,
        created_at=updated.created_at
    )

@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    trip = TripRepository.get_trip_by_id(db, trip_id, user_id)
    if not trip:
        raise APIException("NOT_FOUND", "Trip not found.", 404)
    TripRepository.delete_trip(db, trip)
    return {"success": True, "message": "Trip successfully deleted."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
