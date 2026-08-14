import sys
import os
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.database.connection import get_db, Base, engine
from database.models import Trip, Itinerary, ItineraryItem, Booking, Invoice, Payment, User, generate_uuid
from shared.schemas.models import (
    TripCreateRequest, TripResponse, ItineraryResponse, ItineraryItemSchema,
    InvoiceDetailSchema, InvoiceResponse, DemoPaymentRequest, PaymentResponse, BillingSummaryResponse
)
from shared.auth.jwt import decode_access_token
from shared.errors.handlers import (
    api_exception_handler, http_exception_handler, validation_exception_handler,
    generic_exception_handler, APIException
)
from shared.utils.pdf_generator import generate_invoice_pdf
import uuid
from datetime import datetime
from fastapi import Request, Response
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

# ==================== BILLING MODULE HELPERS & ROUTES ====================
def calculate_bill_data(room_price: float, nights: int, rooms: int, service_fee: float = 300.0, discount: float = 500.0) -> dict:
    """Calculates bill components mathematically:
    Room Cost = Room Price * Nights * Rooms
    Subtotal = Room Cost
    Tax = 18% of Subtotal
    Final Total = Subtotal + Tax + Service Fee - Discount
    """
    if room_price <= 0:
        raise APIException("BAD_REQUEST", "Room price must be a positive number.", 400)
    if nights <= 0:
        raise APIException("BAD_REQUEST", "Number of nights must be greater than zero.", 400)
    if rooms <= 0:
        raise APIException("BAD_REQUEST", "Number of rooms must be greater than zero.", 400)
    if service_fee < 0:
        raise APIException("BAD_REQUEST", "Service fee cannot be negative.", 400)
    if discount < 0:
        raise APIException("BAD_REQUEST", "Discount cannot be negative.", 400)

    room_cost = round(room_price * nights * rooms, 2)
    subtotal = room_cost
    tax = round(subtotal * 0.18, 2)
    total_amount = round(subtotal + tax + service_fee - discount, 2)

    if total_amount < 0:
        raise APIException("BAD_REQUEST", "Final amount calculation resulted in a negative total.", 400)

    return {
        "room_cost": room_cost,
        "subtotal": subtotal,
        "tax": tax,
        "service_fee": service_fee,
        "discount": discount,
        "total_amount": total_amount
    }

def generate_unique_invoice_number(db: Session) -> str:
    """Generates unique invoice number TMAI-INV-2026-000001 avoiding duplicates."""
    count = db.query(Invoice).count() + 1
    seq = f"{count:06d}"
    candidate = f"TMAI-INV-2026-{seq}"
    while db.query(Invoice).filter(Invoice.invoice_number == candidate).first():
        count += 1
        seq = f"{count:06d}"
        candidate = f"TMAI-INV-2026-{seq}"
    return candidate

def build_invoice_detail_schema(invoice: Invoice, db: Session) -> InvoiceDetailSchema:
    booking = db.query(Booking).filter(Booking.id == invoice.booking_id).first()
    latest_payment = db.query(Payment).filter(Payment.invoice_id == invoice.id).order_by(Payment.created_at.desc()).first()
    pay_status = latest_payment.payment_status if latest_payment else "Pending"

    guest_name = "Customer"
    guest_email = "guest@travelmind.ai"
    if booking:
        guest_name = booking.guest_name or "Customer"
        guest_email = booking.guest_email or "guest@travelmind.ai"

    user_rec = db.query(User).filter(User.id == invoice.user_id).first()
    if user_rec:
        if user_rec.name and guest_name == "Customer":
            guest_name = user_rec.name
        if user_rec.email and guest_email == "guest@travelmind.ai":
            guest_email = user_rec.email

    return InvoiceDetailSchema(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        booking_id=booking.id if booking else invoice.booking_id,
        booking_reference=booking.booking_reference if (booking and booking.booking_reference) else f"TMAI-2026-{(booking.id[:6] if booking else '000123').upper()}",
        hotel_name=booking.hotel_name if booking else "Ocean Pearl Resort",
        room_type=booking.room_type if booking else "Deluxe Room",
        guest_name=guest_name,
        guest_email=guest_email,
        guest_phone=booking.guest_phone if booking else "+91 98765 43210",
        check_in=booking.check_in if booking else "2026-08-20",
        check_out=booking.check_out if booking else "2026-08-23",
        nights=booking.nights if booking else 3,
        rooms=booking.rooms if booking else 1,
        room_price=booking.room_price if booking else 3500.0,
        subtotal=invoice.subtotal,
        tax=invoice.tax,
        service_fee=invoice.service_fee,
        discount=invoice.discount,
        total_amount=invoice.total_amount,
        currency=invoice.currency or "INR",
        payment_status=pay_status,
        invoice_status=invoice.invoice_status or "Generated",
        created_at=invoice.created_at.strftime("%Y-%m-%d %H:%M") if invoice.created_at else None
    )

def ensure_default_booking(db: Session, user_id: str, booking_id: str) -> Booking:
    """Helper to retrieve or auto-create demo room booking if missing."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        if booking_id.startswith("demo-") or booking_id == "default":
            booking = Booking(
                id=booking_id if booking_id != "default" else generate_uuid(),
                user_id=user_id,
                booking_reference=f"TMAI-2026-{uuid.uuid4().hex[:6].upper()}",
                booking_type="Hotel",
                provider="TravelMind AI Hospitality",
                title="Ocean Pearl Resort",
                price=3500.0,
                status="Confirmed",
                hotel_name="Ocean Pearl Resort",
                room_type="Deluxe Room",
                guest_name="Customer",
                guest_email="guest@travelmind.ai",
                guest_phone="+91 98765 43210",
                check_in="2026-08-20",
                check_out="2026-08-23",
                nights=3,
                rooms=1,
                room_price=3500.0
            )
            db.add(booking)
            db.commit()
            db.refresh(booking)
    return booking

@app.post("/bookings/{booking_id}/billing", response_model=InvoiceResponse)
@app.post("/api/bookings/{booking_id}/billing", response_model=InvoiceResponse)
def create_booking_billing(booking_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    booking = ensure_default_booking(db, user_id, booking_id)
    if not booking:
        raise APIException("NOT_FOUND", "Booking not found.", 404)

    if booking.user_id and booking.user_id != user_id:
        raise APIException("FORBIDDEN", "You are not authorized to access this invoice.", 403)

    existing_inv = db.query(Invoice).filter(Invoice.booking_id == booking.id).first()
    if existing_inv:
        return InvoiceResponse(success=True, invoice=build_invoice_detail_schema(existing_inv, db))

    calc = calculate_bill_data(
        room_price=booking.room_price or 3500.0,
        nights=booking.nights or 3,
        rooms=booking.rooms or 1
    )

    try:
        inv_num = generate_unique_invoice_number(db)
        invoice = Invoice(
            invoice_number=inv_num,
            booking_id=booking.id,
            user_id=user_id,
            subtotal=calc["subtotal"],
            tax=calc["tax"],
            service_fee=calc["service_fee"],
            discount=calc["discount"],
            total_amount=calc["total_amount"],
            currency="INR",
            invoice_status="Generated"
        )
        db.add(invoice)
        db.flush()

        payment = Payment(
            invoice_id=invoice.id,
            booking_id=booking.id,
            payment_reference=f"DEMO-PAY-2026-{uuid.uuid4().hex[:8].upper()}",
            amount=calc["total_amount"],
            payment_method="DEMO_PAYMENT",
            payment_status="Pending"
        )
        db.add(payment)
        db.commit()
        db.refresh(invoice)
    except APIException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.error(f"Error generating invoice transaction: {exc}")
        raise APIException("INTERNAL_SERVER_ERROR", "Unable to generate the invoice. Please try again.", 500)

    return InvoiceResponse(success=True, invoice=build_invoice_detail_schema(invoice, db))

@app.get("/bookings/{booking_id}/billing")
@app.get("/api/bookings/{booking_id}/billing")
def get_booking_billing_preview(booking_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    booking = ensure_default_booking(db, user_id, booking_id)
    if not booking:
        raise APIException("NOT_FOUND", "Booking not found.", 404)

    if booking.user_id and booking.user_id != user_id:
        raise APIException("FORBIDDEN", "You are not authorized to access this invoice.", 403)

    calc = calculate_bill_data(
        room_price=booking.room_price or 3500.0,
        nights=booking.nights or 3,
        rooms=booking.rooms or 1
    )
    return {
        "success": True,
        "booking_id": booking.id,
        "hotel_name": booking.hotel_name,
        "room_type": booking.room_type,
        "nights": booking.nights,
        "rooms": booking.rooms,
        "room_price": booking.room_price,
        "calculation": calc
    }

@app.get("/bookings/{booking_id}/invoice", response_model=InvoiceResponse)
@app.get("/api/bookings/{booking_id}/invoice", response_model=InvoiceResponse)
def get_invoice_by_booking(booking_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    booking = ensure_default_booking(db, user_id, booking_id)
    if not booking:
        raise APIException("NOT_FOUND", "Booking not found.", 404)

    if booking.user_id and booking.user_id != user_id:
        raise APIException("FORBIDDEN", "You are not authorized to access this invoice.", 403)

    invoice = db.query(Invoice).filter(Invoice.booking_id == booking.id).first()
    if not invoice:
        return create_booking_billing(booking_id, user_id, db)

    return InvoiceResponse(success=True, invoice=build_invoice_detail_schema(invoice, db))

@app.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
@app.get("/api/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice_by_id(invoice_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        # Search by invoice_number if invoice_id is number
        invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_id).first()
    if not invoice:
        raise APIException("NOT_FOUND", "Invoice not found.", 404)

    if invoice.user_id != user_id:
        raise APIException("FORBIDDEN", "You are not authorized to access this invoice.", 403)

    return InvoiceResponse(success=True, invoice=build_invoice_detail_schema(invoice, db))

@app.get("/invoices/{invoice_id}/download")
@app.get("/api/invoices/{invoice_id}/download")
def download_invoice_pdf(invoice_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_id).first()
    if not invoice:
        raise APIException("NOT_FOUND", "Invoice not found.", 404)

    if invoice.user_id != user_id:
        raise APIException("FORBIDDEN", "You are not authorized to access this invoice.", 403)

    inv_schema = build_invoice_detail_schema(invoice, db)
    pdf_bytes = generate_invoice_pdf(inv_schema.model_dump())

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="invoice-{invoice.invoice_number}.pdf"'
        }
    )

@app.post("/invoices/{invoice_id}/payment/demo", response_model=PaymentResponse)
@app.post("/api/invoices/{invoice_id}/payment/demo", response_model=PaymentResponse)
def process_demo_payment(invoice_id: str, req: DemoPaymentRequest = DemoPaymentRequest(), user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_id).first()
    if not invoice:
        raise APIException("NOT_FOUND", "Invoice not found.", 404)

    if invoice.user_id != user_id:
        raise APIException("FORBIDDEN", "You are not authorized to access this invoice.", 403)

    payment = db.query(Payment).filter(Payment.invoice_id == invoice.id).order_by(Payment.created_at.desc()).first()
    if not payment:
        payment = Payment(
            invoice_id=invoice.id,
            booking_id=invoice.booking_id,
            payment_reference=f"DEMO-PAY-2026-{uuid.uuid4().hex[:8].upper()}",
            amount=invoice.total_amount,
            payment_method="DEMO_PAYMENT",
            payment_status="Pending"
        )
        db.add(payment)
        db.flush()

    if req.simulate_failure:
        payment.payment_status = "Failed"
        payment.paid_at = None
        db.commit()
        inv_schema = build_invoice_detail_schema(invoice, db)
        return PaymentResponse(
            success=False,
            payment_status="Failed",
            payment_reference=payment.payment_reference,
            message="Demo payment failed. Please try again.",
            invoice=inv_schema
        )
    else:
        payment.payment_status = "Paid"
        payment.paid_at = datetime.utcnow()
        db.commit()
        inv_schema = build_invoice_detail_schema(invoice, db)
        return PaymentResponse(
            success=True,
            payment_status="Paid",
            payment_reference=payment.payment_reference,
            message="Demo payment successful. No real money was charged.",
            invoice=inv_schema
        )

@app.get("/users/me/billing-summary", response_model=BillingSummaryResponse)
@app.get("/api/users/me/billing-summary", response_model=BillingSummaryResponse)
def get_user_billing_summary(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user_invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
    user_bookings = db.query(Booking).filter(Booking.user_id == user_id).all()

    total_bookings = max(len(user_bookings), len(user_invoices), 1)
    total_spending = sum(inv.total_amount for inv in user_invoices) if user_invoices else 12190.0
    
    paid_count = 0
    pending_count = 0
    for inv in user_invoices:
        pmt = db.query(Payment).filter(Payment.invoice_id == inv.id).order_by(Payment.created_at.desc()).first()
        if pmt and pmt.payment_status == "Paid":
            paid_count += 1
        else:
            pending_count += 1

    return BillingSummaryResponse(
        total_bookings=total_bookings,
        total_spending=round(total_spending, 2),
        pending_payments=pending_count,
        paid_bookings=paid_count
    )

@app.get("/users/me/bookings")
@app.get("/api/users/me/bookings")
def get_user_room_bookings(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    if not bookings:
        # Create default demo booking if none exists
        ensure_default_booking(db, user_id, f"demo-booking-{user_id[:8]}")
        bookings = db.query(Booking).filter(Booking.user_id == user_id).all()

    results = []
    for b in bookings:
        inv = db.query(Invoice).filter(Invoice.booking_id == b.id).first()
        inv_data = build_invoice_detail_schema(inv, db) if inv else None
        results.append({
            "id": b.id,
            "booking_reference": b.booking_reference or f"TMAI-2026-{b.id[:6].upper()}",
            "hotel_name": b.hotel_name,
            "room_type": b.room_type,
            "check_in": b.check_in,
            "check_out": b.check_out,
            "nights": b.nights,
            "rooms": b.rooms,
            "price": b.price,
            "status": b.status,
            "invoice": inv_data
        })
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
