import sys
import os
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared.database.connection import SessionLocal, engine, Base
from database.models import User, Booking, Invoice, Payment, generate_uuid
from database.seed.seed_data import seed_database
import importlib

trip_mod = importlib.import_module("services.trip-service.app.main")
calculate_bill_data = trip_mod.calculate_bill_data
generate_unique_invoice_number = trip_mod.generate_unique_invoice_number
from shared.utils.pdf_generator import generate_invoice_pdf
from shared.auth.jwt import create_access_token

trip_client = TestClient(trip_mod.app)

@pytest.fixture(scope="module", autouse=True)
def setup_billing_test_db():
    seed_database()

# ==================== 1. BILL CALCULATION MATHEMATICAL TESTS ====================
def test_bill_calculation_exact_formula():
    """Verify formula:
    Room Price: ₹3,500/night, Nights: 3, Rooms: 1
    Room Cost: 3500 * 3 * 1 = 10,500
    Subtotal: 10,500
    Tax (18%): 1,890
    Service Fee: 300
    Discount: 500
    Final Amount: 10500 + 1890 + 300 - 500 = 12,190
    """
    calc = calculate_bill_data(room_price=3500.0, nights=3, rooms=1, service_fee=300.0, discount=500.0)
    assert calc["room_cost"] == 10500.0
    assert calc["subtotal"] == 10500.0
    assert calc["tax"] == 1890.0
    assert calc["service_fee"] == 300.0
    assert calc["discount"] == 500.0
    assert calc["total_amount"] == 12190.0

def test_tax_service_fee_and_discount_calculation():
    calc = calculate_bill_data(room_price=5000.0, nights=2, rooms=2, service_fee=400.0, discount=1000.0)
    # Room cost = 5000 * 2 * 2 = 20000
    # Tax = 20000 * 0.18 = 3600
    # Final = 20000 + 3600 + 400 - 1000 = 23000
    assert calc["room_cost"] == 20000.0
    assert calc["tax"] == 3600.0
    assert calc["total_amount"] == 23000.0

def test_invalid_negative_price_and_nights_validation():
    with pytest.raises(Exception):
        calculate_bill_data(room_price=-100.0, nights=3, rooms=1)
    with pytest.raises(Exception):
        calculate_bill_data(room_price=3500.0, nights=-1, rooms=1)
    with pytest.raises(Exception):
        calculate_bill_data(room_price=3500.0, nights=3, rooms=0)

# ==================== 2. INVOICE NUMBER GENERATION TESTS ====================
def test_invoice_number_generation_format():
    db = SessionLocal()
    try:
        inv_num = generate_unique_invoice_number(db)
        assert inv_num.startswith("TMAI-INV-2026-")
        assert len(inv_num) == 20  # TMAI-INV-2026-000001
    finally:
        db.close()

# ==================== 3. BILLING API & TRANSACTION TESTS ====================
def test_create_and_get_invoice_api_flow():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@travelmind.ai").first()
        token = create_access_token({"sub": user.id, "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}

        booking_id = f"test-booking-{generate_uuid()[:8]}"
        booking = Booking(
            id=booking_id,
            user_id=user.id,
            booking_reference=f"TMAI-2026-{generate_uuid()[:6].upper()}",
            booking_type="Hotel",
            provider="Grand Resort & Spa",
            title="Grand Resort - Deluxe Room",
            price=3500.0,
            status="Confirmed",
            hotel_name="Grand Resort & Spa",
            room_type="Deluxe Room",
            guest_name=user.name,
            guest_email=user.email,
            nights=3,
            rooms=1,
            room_price=3500.0
        )
        db.add(booking)
        db.commit()

        # Step 1: Create Invoice API
        resp = trip_client.post(f"/api/bookings/{booking.id}/billing", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] == True
        inv = data["invoice"]
        assert inv["subtotal"] == 10500.0
        assert inv["tax"] == 1890.0
        assert inv["service_fee"] == 300.0
        assert inv["discount"] == 500.0
        assert inv["total_amount"] == 12190.0
        assert inv["invoice_number"].startswith("TMAI-INV-2026-")
        assert inv["payment_status"] == "Pending"

        # Step 2: Fetch Invoice by Invoice ID
        inv_resp = trip_client.get(f"/api/invoices/{inv['id']}", headers=headers)
        assert inv_resp.status_code == 200
        assert inv_resp.json()["invoice"]["invoice_number"] == inv["invoice_number"]

        # Step 3: Fetch Invoice by Booking ID
        inv_by_book = trip_client.get(f"/api/bookings/{booking.id}/invoice", headers=headers)
        assert inv_by_book.status_code == 200
        assert inv_by_book.json()["invoice"]["id"] == inv["id"]
    finally:
        db.close()

def test_duplicate_invoice_prevention():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@travelmind.ai").first()
        token = create_access_token({"sub": user.id, "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}

        booking_id = f"test-dup-{generate_uuid()[:8]}"
        booking = Booking(
            id=booking_id,
            user_id=user.id,
            booking_reference=f"TMAI-2026-{generate_uuid()[:6].upper()}",
            price=3500.0
        )
        db.add(booking)
        db.commit()

        # First Call -> Creates Invoice
        r1 = trip_client.post(f"/api/bookings/{booking.id}/billing", headers=headers)
        assert r1.status_code == 200

        # Second Call -> Idempotently returns existing invoice without duplication
        r2 = trip_client.post(f"/api/bookings/{booking.id}/billing", headers=headers)
        assert r2.status_code == 200
        assert r2.json()["invoice"]["id"] == r1.json()["invoice"]["id"]
    finally:
        db.close()

def test_unauthorized_invoice_access_prevention():
    db = SessionLocal()
    try:
        user1 = db.query(User).filter(User.email == "demo@travelmind.ai").first()
        token1 = create_access_token({"sub": user1.id, "email": user1.email})
        
        # Create second user
        token2 = create_access_token({"sub": "other-user-999", "email": "other@travelmind.ai"})
        headers2 = {"Authorization": f"Bearer {token2}"}

        booking = Booking(
            id=f"priv-booking-{generate_uuid()[:8]}",
            user_id=user1.id,
            price=4000.0
        )
        db.add(booking)
        db.commit()

        inv = Invoice(
            invoice_number=f"TMAI-INV-2026-{generate_uuid()[:6]}",
            booking_id=booking.id,
            user_id=user1.id,
            subtotal=4000.0,
            tax=720.0,
            service_fee=300.0,
            discount=0.0,
            total_amount=5020.0
        )
        db.add(inv)
        db.commit()

        # User2 tries to access User1's invoice -> 403 Forbidden
        forbidden_resp = trip_client.get(f"/api/invoices/{inv.id}", headers=headers2)
        assert forbidden_resp.status_code == 403
    finally:
        db.close()

def test_demo_payment_success_and_failure():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@travelmind.ai").first()
        token = create_access_token({"sub": user.id, "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}

        booking = Booking(id=f"pay-booking-{generate_uuid()[:8]}", user_id=user.id, price=3500.0)
        db.add(booking)
        db.commit()

        inv_resp = trip_client.post(f"/api/bookings/{booking.id}/billing", headers=headers)
        inv_id = inv_resp.json()["invoice"]["id"]

        # Test Demo Payment Failure Simulation
        fail_resp = trip_client.post(f"/api/invoices/{inv_id}/payment/demo", json={"simulate_failure": True}, headers=headers)
        assert fail_resp.status_code == 200
        assert fail_resp.json()["payment_status"] == "Failed"
        assert fail_resp.json()["success"] == False

        # Test Demo Payment Success
        succ_resp = trip_client.post(f"/api/invoices/{inv_id}/payment/demo", json={"simulate_failure": False}, headers=headers)
        assert succ_resp.status_code == 200
        assert succ_resp.json()["payment_status"] == "Paid"
        assert succ_resp.json()["success"] == True
        assert "Demo payment successful" in succ_resp.json()["message"]
    finally:
        db.close()

def test_invoice_pdf_generation_and_download():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@travelmind.ai").first()
        token = create_access_token({"sub": user.id, "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}

        booking = Booking(id=f"pdf-booking-{generate_uuid()[:8]}", user_id=user.id, price=3500.0)
        db.add(booking)
        db.commit()

        inv_resp = trip_client.post(f"/api/bookings/{booking.id}/billing", headers=headers)
        inv_id = inv_resp.json()["invoice"]["id"]

        # PDF Download Endpoint
        pdf_resp = trip_client.get(f"/api/invoices/{inv_id}/download", headers=headers)
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert len(pdf_resp.content) > 100
        assert b"%PDF" in pdf_resp.content[:10]
    finally:
        db.close()
