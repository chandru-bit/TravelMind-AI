import sys
import os
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.database.connection import get_db, Base, engine
from database.models import User, UserPreference
from shared.schemas.models import (
    UserRegisterRequest, UserLoginRequest, UserResponse, AuthResponse,
    UserPreferencesSchema, UserProfileResponse
)
from shared.auth.jwt import hash_password, verify_password, create_access_token, decode_access_token
from shared.errors.handlers import (
    api_exception_handler, http_exception_handler, validation_exception_handler,
    generic_exception_handler, APIException
)
from shared.logging.structured import get_logger, request_id_ctx
from fastapi.exceptions import RequestValidationError

logger = get_logger("user-service")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelMind AI - User Service", version="1.0.0")

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
class UserRepository:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, req: UserRegisterRequest) -> User:
        user = User(
            name=req.name.strip(),
            email=req.email.lower().strip(),
            password_hash=hash_password(req.password)
        )
        db.add(user)
        db.flush()

        pref = UserPreference(user_id=user.id)
        db.add(pref)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, name: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.name = name
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def update_preferences(db: Session, user_id: str, req: UserPreferencesSchema) -> UserPreference:
        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id)
            db.add(pref)
        
        pref.home_location = req.home_location
        pref.budget = req.budget
        pref.travel_style = req.travel_style
        pref.food_preference = req.food_preference
        pref.traveler_count = req.traveler_count
        pref.interests = req.interests or []
        pref.activities = req.activities or []
        pref.preferred_destinations = req.preferred_destinations or []
        
        db.commit()
        db.refresh(pref)
        return pref

# ==================== ROUTES ====================
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user-service"}

@app.post("/users/register", response_model=AuthResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = UserRepository.get_by_email(db, req.email)
    if existing:
        raise APIException("CONFLICT", "An account with this email already exists.", 409)

    user = UserRepository.create_user(db, req)
    token = create_access_token({"sub": user.id, "email": user.email})
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )

@app.post("/users/login", response_model=AuthResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = UserRepository.get_by_email(db, req.email)
    if not user or not verify_password(req.password, user.password_hash):
        raise APIException("UNAUTHORIZED", "Invalid email or password.", 401)

    token = create_access_token({"sub": user.id, "email": user.email})
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )

@app.get("/users/me", response_model=UserProfileResponse)
def get_profile(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise APIException("NOT_FOUND", "User profile not found.", 404)

    pref_schema = None
    if user.preference:
        pref_schema = UserPreferencesSchema(
            home_location=user.preference.home_location,
            budget=user.preference.budget,
            travel_style=user.preference.travel_style,
            interests=user.preference.interests,
            activities=user.preference.activities,
            food_preference=user.preference.food_preference,
            traveler_count=user.preference.traveler_count,
            preferred_destinations=user.preference.preferred_destinations
        )

    return UserProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        preferences=pref_schema
    )

@app.put("/users/me", response_model=UserResponse)
def update_profile(name: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = UserRepository.update_user(db, user_id, name)
    return UserResponse.model_validate(user)

@app.get("/users/me/preferences", response_model=UserPreferencesSchema)
def get_preferences(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = UserRepository.get_by_id(db, user_id)
    if not user or not user.preference:
        return UserPreferencesSchema()
    return UserPreferencesSchema(
        home_location=user.preference.home_location,
        budget=user.preference.budget,
        travel_style=user.preference.travel_style,
        interests=user.preference.interests,
        activities=user.preference.activities,
        food_preference=user.preference.food_preference,
        traveler_count=user.preference.traveler_count,
        preferred_destinations=user.preference.preferred_destinations
    )

@app.put("/users/me/preferences", response_model=UserPreferencesSchema)
def update_preferences(req: UserPreferencesSchema, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    pref = UserRepository.update_preferences(db, user_id, req)
    return UserPreferencesSchema(
        home_location=pref.home_location,
        budget=pref.budget,
        travel_style=pref.travel_style,
        interests=pref.interests,
        activities=pref.activities,
        food_preference=pref.food_preference,
        traveler_count=pref.traveler_count,
        preferred_destinations=pref.preferred_destinations
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
