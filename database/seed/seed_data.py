import sys
import os
import random
from datetime import datetime, timedelta

# Append project root to python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared.database.connection import engine, Base, SessionLocal
from database.models import Destination, PriceHistory, WeatherData, User, UserPreference, Trip, Feedback, Notification, generate_uuid
from shared.auth.jwt import hash_password

DESTINATIONS = [
    {
        "name": "Goa",
        "state_country": "Goa, India",
        "avg_cost": 22000.0,
        "best_season": "Winter (Nov - Feb)",
        "weather_summary": "Sunny & Tropical 28°C",
        "activities": ["Beach Walk", "Water Sports", "Nightlife", "Seafood Tasting", "Fort Exploration"],
        "travel_type": "Balanced",
        "popularity": 96.0,
        "distance_km": 590.0,
    },
    {
        "name": "Pondicherry",
        "state_country": "Puducherry, India",
        "avg_cost": 18000.0,
        "best_season": "Oct - Mar",
        "weather_summary": "Coastal Breeze 27°C",
        "activities": ["French Quarter Walk", "Auroville Visit", "Beach Relaxation", "Cafe Hopping"],
        "travel_type": "Balanced",
        "popularity": 88.0,
        "distance_km": 310.0,
    },
    {
        "name": "Ooty",
        "state_country": "Tamil Nadu, India",
        "avg_cost": 20000.0,
        "best_season": "Sep - May",
        "weather_summary": "Cool & Misty 16°C",
        "activities": ["Botanical Garden", "Toy Train Ride", "Tea Plantation Tour", "Boating in Ooty Lake"],
        "travel_type": "Budget",
        "popularity": 90.0,
        "distance_km": 530.0,
    },
    {
        "name": "Munnar",
        "state_country": "Kerala, India",
        "avg_cost": 24000.0,
        "best_season": "Sep - Mar",
        "weather_summary": "Crisp Mountain Air 18°C",
        "activities": ["Tea Estates Visit", "Eravikulam Trekking", "Attukad Waterfall", "Spice Plantation"],
        "travel_type": "Balanced",
        "popularity": 92.0,
        "distance_km": 480.0,
    },
    {
        "name": "Kodaikanal",
        "state_country": "Tamil Nadu, India",
        "avg_cost": 19000.0,
        "best_season": "Oct - Mar",
        "weather_summary": "Pleasant Hill Climate 17°C",
        "activities": ["Kodai Lake Boating", "Coaker's Walk", "Pillar Rocks Trek", "Cycling"],
        "travel_type": "Budget",
        "popularity": 87.0,
        "distance_km": 460.0,
    },
    {
        "name": "Gokarna",
        "state_country": "Karnataka, India",
        "avg_cost": 16000.0,
        "best_season": "Oct - Mar",
        "weather_summary": "Warm & Sunny 29°C",
        "activities": ["Om Beach Trek", "Kudle Sunset", "Temple Visit", "Beach Camping"],
        "travel_type": "Budget",
        "popularity": 89.0,
        "distance_km": 480.0,
    },
    {
        "name": "Coorg",
        "state_country": "Karnataka, India",
        "avg_cost": 25000.0,
        "best_season": "Oct - Apr",
        "weather_summary": "Lush & Misty 20°C",
        "activities": ["Coffee Plantation Tour", "Abbey Falls", "Elephant Camp", "Trekking"],
        "travel_type": "Balanced",
        "popularity": 91.0,
        "distance_km": 240.0,
    },
    {
        "name": "Varkala",
        "state_country": "Kerala, India",
        "avg_cost": 21000.0,
        "best_season": "Nov - Mar",
        "weather_summary": "Cliff Ocean Breeze 28°C",
        "activities": ["Cliffside Dining", "Ayurvedic Spa", "Surfing Lessons", "Janardanaswamy Temple"],
        "travel_type": "Balanced",
        "popularity": 86.0,
        "distance_km": 620.0,
    },
    {
        "name": "Jaipur",
        "state_country": "Rajasthan, India",
        "avg_cost": 28000.0,
        "best_season": "Oct - Mar",
        "weather_summary": "Sunny Desert 24°C",
        "activities": ["Amber Fort Tour", "Hawa Mahal", "Bazaar Shopping", "Rajasthani Thali Dining"],
        "travel_type": "Premium",
        "popularity": 95.0,
        "distance_km": 1150.0,
    },
    {
        "name": "Manali",
        "state_country": "Himachal Pradesh, India",
        "avg_cost": 32000.0,
        "best_season": "Oct - Jun",
        "weather_summary": "Snowy & Chilly 10°C",
        "activities": ["Solang Valley Sports", "Rohtang Pass Snow Tour", "Hadimba Temple", "River Rafting"],
        "travel_type": "Premium",
        "popularity": 97.0,
        "distance_km": 1950.0,
    },
    {
        "name": "Udaipur",
        "state_country": "Rajasthan, India",
        "avg_cost": 35000.0,
        "best_season": "Sep - Mar",
        "weather_summary": "Pleasant Lake Climate 23°C",
        "activities": ["City Palace Tour", "Lake Pichola Cruise", "Jagmandir Visit", "Sunset at Monsoon Palace"],
        "travel_type": "Luxury",
        "popularity": 94.0,
        "distance_km": 750.0,
    },
    {
        "name": "Rishikesh",
        "state_country": "Uttarakhand, India",
        "avg_cost": 17000.0,
        "best_season": "Sep - May",
        "weather_summary": "Fresh River Air 21°C",
        "activities": ["White Water Rafting", "Ganga Aarti", "Yoga & Meditation", "Beatles Ashram"],
        "travel_type": "Budget",
        "popularity": 91.0,
        "distance_km": 1400.0,
    },
    {
        "name": "Mysore",
        "state_country": "Karnataka, India",
        "avg_cost": 15000.0,
        "best_season": "Oct - Mar",
        "weather_summary": "Mild & Pleasant 26°C",
        "activities": ["Mysore Palace Tour", "Chamundi Hill", "Silk Bazaar Shopping", "Zoo Visit"],
        "travel_type": "Budget",
        "popularity": 85.0,
        "distance_km": 140.0,
    },
    {
        "name": "Wayanad",
        "state_country": "Kerala, India",
        "avg_cost": 23000.0,
        "best_season": "Oct - May",
        "weather_summary": "Tropical Rainforest 22°C",
        "activities": ["Banasura Sagar Dam", "Edakkal Caves", "Chembra Peak Trek", "Wildlife Safari"],
        "travel_type": "Balanced",
        "popularity": 89.0,
        "distance_km": 280.0,
    },
    {
        "name": "Andaman",
        "state_country": "Andaman & Nicobar Islands, India",
        "avg_cost": 55000.0,
        "best_season": "Oct - May",
        "weather_summary": "Island Paradise 29°C",
        "activities": ["Scuba Diving Havelock", "Cellular Jail Light Show", "Radhanagar Beach", "Glass Bottom Boat"],
        "travel_type": "Luxury",
        "popularity": 98.0,
        "distance_km": 1600.0,
    }
]

def seed_database():
    """Initializes tables and seeds initial realistic demo data."""
    print("Creating database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Destinations
        print("Seeding destinations...")
        for dest_data in DESTINATIONS:
            existing = db.query(Destination).filter(Destination.name == dest_data["name"]).first()
            if not existing:
                d = Destination(
                    name=dest_data["name"],
                    state_country=dest_data["state_country"],
                    avg_cost=dest_data["avg_cost"],
                    best_season=dest_data["best_season"],
                    weather_summary=dest_data["weather_summary"],
                    travel_type=dest_data["travel_type"],
                    popularity=dest_data["popularity"],
                    distance_km=dest_data["distance_km"]
                )
                d.activities = dest_data["activities"]
                db.add(d)
        db.commit()

        # 2. Seed Weather Data
        print("Seeding weather data...")
        for dest in db.query(Destination).all():
            w_existing = db.query(WeatherData).filter(WeatherData.destination == dest.name).first()
            if not w_existing:
                w = WeatherData(
                    destination=dest.name,
                    temperature_celsius=random.uniform(18.0, 32.0),
                    condition=random.choice(["Sunny", "Clear Sky", "Pleasant", "Partly Cloudy", "Misty"]),
                    humidity_percent=random.randint(50, 80),
                    wind_speed_kmh=random.uniform(8.0, 20.0)
                )
                db.add(w)
        db.commit()

        # 3. Seed Price History (For ML Price Prediction training dataset)
        print("Seeding historical price dataset for ML training...")
        dest_names = [d["name"] for d in DESTINATIONS]
        seasons = ["Peak", "Regular", "Off-Season", "Monsoon"]
        base_prices = {"Goa": 22000, "Manali": 32000, "Andaman": 55000, "Ooty": 20000, "Jaipur": 28000}
        
        for dest_name in dest_names:
            base_p = base_prices.get(dest_name, 20000.0)
            for month in range(1, 13):
                date_str = f"2026-{month:02d}-15"
                season = seasons[month % 4]
                multiplier = 1.3 if season == "Peak" else (0.8 if season == "Off-Season" else 1.0)
                hotel_price = (base_p * 0.6 * multiplier) + random.uniform(-1000, 1000)
                transport_price = (base_p * 0.4 * multiplier) + random.uniform(-500, 500)
                demand = 0.9 if season == "Peak" else (0.4 if season == "Off-Season" else 0.6)
                
                ph = PriceHistory(
                    destination=dest_name,
                    travel_date=date_str,
                    hotel_price=round(hotel_price, 2),
                    transport_price=round(transport_price, 2),
                    demand_score=round(demand, 2),
                    season=season
                )
                db.add(ph)
        db.commit()

        # 4. Seed Demo User
        print("Seeding demo user...")
        demo_user = db.query(User).filter(User.email == "demo@travelmind.ai").first()
        if not demo_user:
            demo_user = User(
                name="Demo Explorer",
                email="demo@travelmind.ai",
                password_hash=hash_password("password123")
            )
            db.add(demo_user)
            db.flush()

            user_pref = UserPreference(
                user_id=demo_user.id,
                home_location="Mumbai",
                budget=25000.0,
                travel_style="Balanced",
                food_preference="No Restrictions",
                traveler_count=2
            )
            user_pref.interests = ["Beach", "Adventure", "Food"]
            user_pref.activities = ["Sightseeing", "Water Sports", "Photography"]
            user_pref.preferred_destinations = ["Goa", "Kodaikanal"]
            db.add(user_pref)

            # Sample Trip
            sample_trip = Trip(
                user_id=demo_user.id,
                source="Mumbai",
                destination="Goa",
                start_date="2026-09-10",
                end_date="2026-09-14",
                budget=30000.0,
                traveler_count=2,
                travel_style="Balanced",
                status="planned"
            )
            sample_trip.interests = ["Beach", "Adventure"]
            db.add(sample_trip)

            # Sample Feedback
            fb = Feedback(
                user_id=demo_user.id,
                destination="Goa",
                rating=5,
                comment="TravelMind AI recommendation was spot on! Goa fit our budget perfectly.",
                is_helpful=True
            )
            db.add(fb)

            # Sample Notification
            notif = Notification(
                user_id=demo_user.id,
                title="Welcome to TravelMind AI!",
                message="Your personalized travel recommendations and price predictions are ready.",
                type="recommendation"
            )
            db.add(notif)
            db.flush()

            # Seed Demo Booking, Invoice, and Payment
            from database.models import Booking, Invoice, Payment
            demo_booking = Booking(
                id="demo-booking-001",
                trip_id=sample_trip.id,
                user_id=demo_user.id,
                booking_reference="TMAI-2026-000123",
                booking_type="Hotel",
                provider="Ocean Pearl Resort Hospitality",
                title="Ocean Pearl Resort - Deluxe Room",
                price=3500.0,
                status="Confirmed",
                hotel_name="Ocean Pearl Resort",
                room_type="Deluxe Room",
                guest_name="Demo Explorer",
                guest_email="demo@travelmind.ai",
                guest_phone="+91 98765 43210",
                check_in="2026-08-20",
                check_out="2026-08-23",
                nights=3,
                rooms=1,
                room_price=3500.0
            )
            db.add(demo_booking)
            db.flush()

            # Room Cost = 3500 * 3 * 1 = 10500
            # Subtotal = 10500, Tax (18%) = 1890, Service Fee = 300, Discount = 500
            # Total = 10500 + 1890 + 300 - 500 = 12190
            demo_invoice = Invoice(
                id="demo-invoice-001",
                invoice_number="TMAI-INV-2026-000001",
                booking_id=demo_booking.id,
                user_id=demo_user.id,
                subtotal=10500.0,
                tax=1890.0,
                service_fee=300.0,
                discount=500.0,
                total_amount=12190.0,
                currency="INR",
                invoice_status="Generated"
            )
            db.add(demo_invoice)
            db.flush()

            demo_payment = Payment(
                id="demo-payment-001",
                invoice_id=demo_invoice.id,
                booking_id=demo_booking.id,
                payment_reference="DEMO-PAY-2026-000001",
                amount=12190.0,
                payment_method="DEMO_PAYMENT",
                payment_status="Pending"
            )
            db.add(demo_payment)
            db.commit()

        print("Database successfully seeded with 15 realistic destinations, weather data, and ML training dataset!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
