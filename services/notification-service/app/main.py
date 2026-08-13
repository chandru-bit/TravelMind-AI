import sys
import os
from typing import List, Optional
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.database.connection import get_db, Base, engine
from database.models import Notification
from shared.schemas.models import NotificationResponse
from shared.auth.jwt import decode_access_token
from shared.errors.handlers import (
    api_exception_handler, http_exception_handler, validation_exception_handler,
    generic_exception_handler, APIException
)
from shared.logging.structured import get_logger
from fastapi.exceptions import RequestValidationError

logger = get_logger("notification-service")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TravelMind AI - Notification Service", version="1.0.0")

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

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notification-service"}

@app.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            message=n.message,
            type=n.type,
            is_read=n.is_read,
            created_at=n.created_at
        )
        for n in notifs
    ]

@app.post("/notifications", response_model=NotificationResponse)
def create_notification(
    title: str,
    message: str,
    notif_type: str = "system",
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        is_read=False
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    return NotificationResponse(
        id=notif.id,
        user_id=notif.user_id,
        title=notif.title,
        message=notif.message,
        type=notif.type,
        is_read=notif.is_read,
        created_at=notif.created_at
    )

@app.put("/notifications/{notif_id}/read")
def mark_as_read(notif_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user_id).first()
    if not notif:
        raise APIException("NOT_FOUND", "Notification not found.", 404)
    notif.is_read = True
    db.commit()
    return {"success": True, "message": "Notification marked as read."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
